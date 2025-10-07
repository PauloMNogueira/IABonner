"""News Analyzer
Módulo para análise de notícias usando Ollama como provedor principal com sistema de fallback
"""

import os
import json
import logging
import requests
from typing import List, Dict, Optional
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
from dotenv import load_dotenv

class NewsAnalyzer:
    """Analisador de notícias usando Ollama como provedor principal com fallback"""
    
    def __init__(self):
        load_dotenv()
        self.logger = logging.getLogger(__name__)
        
        # Configurações dos provedores em ordem de prioridade (Ollama primeiro)
        self.providers = {
            'ollama': {
                'api_key': 'local',  # Ollama não precisa de API key
                'base_url': os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434/v1'),
                'model': os.getenv('OLLAMA_MODEL', 'llama3:latest'),
                'free': True,
                'priority': 1
            },
            'openrouter': {
                'api_key': os.getenv('OPENROUTER_API_KEY'),
                'base_url': 'https://openrouter.ai/api/v1',
                'model': os.getenv('DEFAULT_MODEL', 'meta-llama/llama-3.3-70b-instruct:free'),
                'free': True,
                'priority': 2
            },
            'groq': {
                'api_key': os.getenv('GROQ_API_KEY'),
                'base_url': 'https://api.groq.com/openai/v1',
                'model': os.getenv('GROQ_MODEL', 'llama3-8b-8192'),
                'free': True,
                'priority': 3
            },
            'together': {
                'api_key': os.getenv('TOGETHER_API_KEY'),
                'base_url': 'https://api.together.xyz/v1',
                'model': os.getenv('TOGETHER_MODEL', 'meta-llama/Llama-2-7b-chat-hf'),
                'free': False,  # $1 crédito inicial
                'priority': 4
            },
            'huggingface': {
                'api_key': os.getenv('HUGGINGFACE_API_KEY'),
                'base_url': 'https://api-inference.huggingface.co/models',
                'model': os.getenv('HUGGINGFACE_MODEL', 'microsoft/DialoGPT-medium'),
                'free': True,
                'priority': 5
            }
        }
        
        # Tentar configurar provedores em ordem de prioridade
        self.available_providers = []
        self._setup_providers()
        
        self.analysis_enabled = os.getenv('ANALYSIS_ENABLED', 'true').lower() == 'true'
        self.current_provider_index = 0
    
    def _check_ollama_availability(self):
        """Verificar se Ollama está rodando e disponível"""
        try:
            ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
            # Remover /v1 se estiver presente para o health check
            health_url = ollama_url.replace('/v1', '') + '/api/tags'
            
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    self.logger.info(f"🦙 Ollama disponível com {len(models)} modelos")
                    return True
                else:
                    self.logger.warning("🦙 Ollama rodando mas sem modelos instalados")
                    return False
            return False
        except Exception as e:
            self.logger.debug(f"🦙 Ollama não disponível: {e}")
            return False
    
    def _setup_providers(self):
        """Configurar provedores disponíveis em ordem de prioridade"""
        # Ordenar provedores por prioridade
        sorted_providers = sorted(self.providers.items(), key=lambda x: x[1].get('priority', 999))
        
        for provider_name, config in sorted_providers:
            if provider_name == 'ollama':
                # Verificar se Ollama está rodando
                if self._check_ollama_availability():
                    try:
                        client = OpenAI(
                            api_key='ollama',  # Ollama não precisa de key real
                            base_url=config['base_url']
                        )
                        self.available_providers.append({
                            'name': provider_name,
                            'config': config,
                            'client': client,
                            'type': 'openai_compatible'
                        })
                        self.logger.info(f"✅ Provedor {provider_name} configurado (local) - PRIORIDADE 1")
                    except Exception as e:
                        self.logger.warning(f"❌ Erro ao configurar {provider_name}: {e}")
                else:
                    self.logger.warning(f"⚠️ Ollama não está disponível - verifique se está rodando")
            elif config['api_key'] and config['api_key'] != 'your_api_key_here':
                try:
                    if provider_name == 'huggingface':
                        # Hugging Face usa requests diretamente
                        self.available_providers.append({
                            'name': provider_name,
                            'config': config,
                            'client': None,
                            'type': 'huggingface'
                        })
                    elif OpenAI:
                        # Outros provedores usam OpenAI client
                        client = OpenAI(
                            api_key=config['api_key'],
                            base_url=config['base_url']
                        )
                        self.available_providers.append({
                            'name': provider_name,
                            'config': config,
                            'client': client,
                            'type': 'openai_compatible'
                        })
                    
                    self.logger.info(f"✅ Provedor {provider_name} configurado - PRIORIDADE {config['priority']}")
                except Exception as e:
                    self.logger.warning(f"❌ Erro ao configurar {provider_name}: {e}")
        
        if self.available_providers:
            primary_provider = self.available_providers[0]['name']
            self.logger.info(f"🔧 {len(self.available_providers)} provedores disponíveis")
            self.logger.info(f"🎯 Provedor principal: {primary_provider}")
            self.logger.info(f"📋 Ordem: {[p['name'] for p in self.available_providers]}")
        else:
            self.logger.warning("⚠️ Nenhum provedor de LLM configurado. Usando análise local.")
    
    def analyze_news(self, news_item: Dict) -> Optional[Dict]:
        """Analisar uma notícia usando sistema de fallback"""
        
        self.logger.info(f"🔍 Iniciando análise da notícia: {news_item.get('title', 'N/A')[:50]}...")
        
        if not self.analysis_enabled:
            self.logger.info("📝 Análise desabilitada, usando análise local")
            return self._local_analysis(news_item)
        
        # Tentar cada provedor disponível
        for i, provider in enumerate(self.available_providers):
            try:
                self.logger.info(f"🚀 Tentando provedor {provider['name']} ({i+1}/{len(self.available_providers)})")
                
                if provider['type'] == 'huggingface':
                    result = self._analyze_with_huggingface(news_item, provider)
                else:
                    result = self._analyze_with_openai_compatible(news_item, provider)
                
                if result:
                    self.logger.info(f"✅ Análise concluída com {provider['name']}")
                    return result
                    
            except Exception as e:
                self.logger.warning(f"❌ Erro com {provider['name']}: {str(e)}")
                
                # Se for rate limit, tentar próximo provedor
                if "429" in str(e) or "rate" in str(e).lower():
                    self.logger.info(f"⏳ Rate limit em {provider['name']}, tentando próximo...")
                    continue
                else:
                    self.logger.error(f"🔍 Erro técnico em {provider['name']}: {type(e).__name__}")
        
        # Se todos os provedores falharam, usar análise local
        self.logger.warning("⚠️ Todos os provedores falharam, usando análise local")
        return self._local_analysis(news_item)
    
    def _analyze_with_openai_compatible(self, news_item: Dict, provider: Dict) -> Optional[Dict]:
        """Analisar usando provedor compatível com OpenAI"""
        
        # Primeiro, traduzir se necessário (exceto para Ollama que pode ser mais lento)
        if provider['name'] != 'ollama':
            translated_item = self._translate_news_item_simple(news_item)
        else:
            translated_item = news_item
        
        # Criar prompt para análise
        prompt = self._create_analysis_prompt(translated_item)
        
        # Configurações específicas para Ollama
        max_tokens = 1500 if provider['name'] == 'ollama' else 2000
        temperature = 0.5 if provider['name'] == 'ollama' else 0.7
        
        response = provider['client'].chat.completions.create(
            model=provider['config']['model'],
            messages=[
                {
                    "role": "system",
                    "content": "Você é um analista especializado em inteligência artificial e tecnologia. Sua tarefa é analisar notícias sobre IA e fornecer insights específicos para desenvolvedores de software e empresas do ramo imobiliário/shopping centers. Responda sempre em português brasileiro."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        analysis_text = response.choices[0].message.content
        parsed_analysis = self._parse_analysis_response(analysis_text)
        
        # Adicionar título e resumo traduzidos
        parsed_analysis['titulo_traduzido'] = translated_item.get('title', news_item.get('title', ''))
        parsed_analysis['resumo_traduzido'] = translated_item.get('summary', news_item.get('summary', ''))
        parsed_analysis['provedor_usado'] = provider['name']  # Indicar qual provedor foi usado
        
        return parsed_analysis
    
    def _analyze_with_huggingface(self, news_item: Dict, provider: Dict) -> Optional[Dict]:
        """Analisar usando Hugging Face Inference API"""
        
        headers = {"Authorization": f"Bearer {provider['config']['api_key']}"}
        
        # Criar prompt simplificado para Hugging Face
        title = news_item.get('title', '')
        content = news_item.get('content', news_item.get('summary', ''))[:500]  # Limitar tamanho
        
        prompt = f"Analise esta notícia de IA: {title}. {content}"
        
        api_url = f"{provider['config']['base_url']}/{provider['config']['model']}"
        
        response = requests.post(
            api_url,
            headers=headers,
            json={"inputs": prompt, "parameters": {"max_length": 500}},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                analysis_text = result[0].get('generated_text', '')
                
                # Parse básico para Hugging Face
                return {
                    'resumo_executivo': analysis_text[:200] + '...' if len(analysis_text) > 200 else analysis_text,
                    'pontos_chave': '• Análise via Hugging Face\n• Conteúdo processado automaticamente\n• Relevante para IA e tecnologia',
                    'nivel_relevancia': 'Médio - Análise automática via Hugging Face',
                    'titulo_traduzido': title,
                    'resumo_traduzido': news_item.get('summary', 'Resumo não disponível')
                }
        
        return None
    
    def _translate_news_item_simple(self, news_item: Dict) -> Dict:
        """Tradução simples ou manter original se não conseguir traduzir"""
        
        title = news_item.get('title', '')
        summary = news_item.get('summary', news_item.get('content', ''))
        
        # Se já estiver em português, não traduzir
        if self._is_portuguese(title) and self._is_portuguese(summary):
            return news_item
        
        # Tentar traduzir apenas com o primeiro provedor disponível
        if self.available_providers:
            try:
                provider = self.available_providers[0]
                if provider['type'] == 'openai_compatible':
                    
                    translation_prompt = f"""
Traduza para português brasileiro:

TÍTULO: {title}
RESUMO: {summary}

Responda apenas:
TÍTULO_TRADUZIDO: [título em português]
RESUMO_TRADUZIDO: [resumo em português]
"""
                    
                    response = provider['client'].chat.completions.create(
                        model=provider['config']['model'],
                        messages=[
                            {"role": "system", "content": "Você é um tradutor. Traduza para português brasileiro."},
                            {"role": "user", "content": translation_prompt}
                        ],
                        max_tokens=1000,
                        temperature=0.3
                    )
                    
                    translation_text = response.choices[0].message.content
                    
                    # Parse da tradução
                    translated_title = title
                    translated_summary = summary
                    
                    lines = translation_text.split('\n')
                    for line in lines:
                        if line.startswith('TÍTULO_TRADUZIDO:'):
                            translated_title = line.replace('TÍTULO_TRADUZIDO:', '').strip()
                        elif line.startswith('RESUMO_TRADUZIDO:'):
                            translated_summary = line.replace('RESUMO_TRADUZIDO:', '').strip()
                    
                    translated_item = news_item.copy()
                    translated_item['title'] = translated_title
                    translated_item['summary'] = translated_summary
                    
                    return translated_item
                    
            except Exception as e:
                self.logger.warning(f"❌ Erro na tradução: {e}")
        
        return news_item
    
    def _is_portuguese(self, text: str) -> bool:
        """Verificar se o texto está em português (verificação simples)"""
        portuguese_words = ['de', 'da', 'do', 'para', 'com', 'em', 'por', 'uma', 'um', 'que', 'não', 'são', 'como', 'mais', 'sobre', 'pela', 'pelo']
        words = text.lower().split()
        portuguese_count = sum(1 for word in words if word in portuguese_words)
        return portuguese_count >= 2 or len(words) < 5
    
    def _create_analysis_prompt(self, news_item: Dict) -> str:
        """Criar prompt para análise da notícia"""
        
        title = news_item.get('title', 'N/A')
        content = news_item.get('content', news_item.get('summary', 'N/A'))
        
        prompt = f"""
Analise a seguinte notícia sobre inteligência artificial e tecnologia:

**Título:** {title}

**Conteúdo:** {content}

Por favor, forneça uma análise estruturada seguindo EXATAMENTE este formato (mantenha os cabeçalhos):

## RESUMO EXECUTIVO
[Resumo da notícia, em português brasileiro]

## PONTOS-CHAVE
[3-5 pontos principais desta notícia em formato de lista]

## NÍVEL DE RELEVÂNCIA
[Alto/Médio/Baixo] - [Justificativa em uma frase]

IMPORTANTE: Responda sempre em português brasileiro e mantenha exatamente os cabeçalhos mostrados acima.
"""
        
        return prompt
    
    def _parse_analysis_response(self, analysis_text: str) -> Dict:
        """Fazer parse da resposta da análise"""
        
        self.logger.info("📋 Fazendo parse da resposta da análise...")
        
        sections = {
            'resumo_executivo': '',
            'pontos_chave': '',
            'nivel_relevancia': ''
        }
        
        current_section = None
        lines = analysis_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Detectar seções com ## ou **
            if ('## RESUMO EXECUTIVO' in line.upper() or 
                '**RESUMO EXECUTIVO**' in line.upper() or
                'RESUMO EXECUTIVO' in line.upper()):
                current_section = 'resumo_executivo'
                self.logger.debug("📝 Encontrada seção: RESUMO EXECUTIVO")
            elif ('## PONTOS-CHAVE' in line.upper() or '## PONTOS CHAVE' in line.upper() or
                  '**PONTOS-CHAVE**' in line.upper() or '**PONTOS CHAVE**' in line.upper() or
                  'PONTOS-CHAVE' in line.upper() or 'PONTOS CHAVE' in line.upper()):
                current_section = 'pontos_chave'
                self.logger.debug("📝 Encontrada seção: PONTOS-CHAVE")
            elif ('## NÍVEL DE RELEVÂNCIA' in line.upper() or '## NIVEL DE RELEVANCIA' in line.upper() or
                  '**NÍVEL DE RELEVÂNCIA**' in line.upper() or '**NIVEL DE RELEVANCIA**' in line.upper() or
                  'NÍVEL DE RELEVÂNCIA' in line.upper() or 'NIVEL DE RELEVANCIA' in line.upper()):
                current_section = 'nivel_relevancia'
                self.logger.debug("📝 Encontrada seção: NÍVEL DE RELEVÂNCIA")
            elif current_section and line and not line.startswith('##') and not line.startswith('**'):
                # Pular linhas que são apenas marcadores de seção
                if not any(marker in line.upper() for marker in ['RESUMO EXECUTIVO', 'PONTOS-CHAVE', 'PONTOS CHAVE', 'NÍVEL DE RELEVÂNCIA', 'NIVEL DE RELEVANCIA']):
                    sections[current_section] += line + '\n'
        
        # Limpar seções
        for key in sections:
            sections[key] = sections[key].strip()
        
        return sections
    
    def _local_analysis(self, news_item: Dict) -> Dict:
        """Análise local inteligente baseada em palavras-chave e padrões"""
        
        title = news_item.get('title', 'N/A')
        content = news_item.get('content', news_item.get('summary', ''))
        
        self.logger.info("🏠 Gerando análise local inteligente")
        
        # Análise de relevância baseada em palavras-chave
        high_relevance_keywords = ['openai', 'chatgpt', 'claude', 'gemini', 'breakthrough', 'revolutionary', 'billion', 'funding', 'ipo', 'acquisition']
        medium_relevance_keywords = ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 'neural', 'algorithm', 'automation', 'robot']
        low_relevance_keywords = ['update', 'minor', 'patch', 'bug', 'fix']
        
        text_lower = (title + ' ' + content).lower()
        
        # Calcular relevância
        high_count = sum(1 for keyword in high_relevance_keywords if keyword in text_lower)
        medium_count = sum(1 for keyword in medium_relevance_keywords if keyword in text_lower)
        low_count = sum(1 for keyword in low_relevance_keywords if keyword in text_lower)
        
        if high_count >= 2:
            relevancia = 'Alto - Contém múltiplas palavras-chave de alta relevância'
        elif high_count >= 1 or medium_count >= 3:
            relevancia = 'Médio - Relevância moderada para o setor de IA'
        elif medium_count >= 1:
            relevancia = 'Médio - Relacionado à inteligência artificial'
        else:
            relevancia = 'Baixo - Relevância limitada para IA'
        
        # Gerar pontos-chave baseados no conteúdo
        pontos_chave = []
        if 'openai' in text_lower or 'chatgpt' in text_lower:
            pontos_chave.append('• Desenvolvimento em OpenAI/ChatGPT')
        if 'google' in text_lower or 'gemini' in text_lower:
            pontos_chave.append('• Inovação do Google em IA')
        if 'microsoft' in text_lower:
            pontos_chave.append('• Iniciativa da Microsoft')
        if 'funding' in text_lower or 'investment' in text_lower:
            pontos_chave.append('• Movimentação de investimentos')
        if 'enterprise' in text_lower or 'business' in text_lower:
            pontos_chave.append('• Aplicação empresarial')
        if 'developer' in text_lower or 'api' in text_lower:
            pontos_chave.append('• Ferramentas para desenvolvedores')
        
        if not pontos_chave:
            pontos_chave = [
                '• Notícia relacionada à inteligência artificial',
                '• Potencial impacto no setor de tecnologia',
                '• Relevante para acompanhamento do mercado'
            ]
        
        # Resumo executivo inteligente
        resumo = f"Análise local da notícia: {title}. "
        if high_count > 0:
            resumo += "Esta notícia apresenta desenvolvimentos significativos em IA com potencial impacto no mercado. "
        elif medium_count > 0:
            resumo += "Esta notícia aborda temas relevantes de inteligência artificial. "
        else:
            resumo += "Esta notícia tem conexão com tecnologia e pode ser de interesse. "
        
        resumo += "Recomenda-se acompanhamento para avaliar oportunidades de aplicação em negócios e desenvolvimento."
        
        return {
            'resumo_executivo': resumo,
            'pontos_chave': '\n'.join(pontos_chave),
            'nivel_relevancia': relevancia,
            'titulo_traduzido': title,
            'resumo_traduzido': news_item.get('summary', 'Resumo não disponível'),
            'metodo_analise': 'local'  # Indicador de que foi análise local
        }