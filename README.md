# 🤖 AI News Agent - JCPM

Um agente inteligente para fazer crawler e análise de notícias sobre Inteligência Artificial dos principais sites especializados, com foco em insights para desenvolvedores de software e empresas do ramo imobiliário/shopping centers.

## 🎯 Funcionalidades

- **Crawler Automatizado**: Coleta notícias de múltiplas fontes especializadas em IA
- **Análise Inteligente**: Usa LLM via OpenRouter para analisar cada notícia
- **Insights Personalizados**: Gera análises específicas para:
  - Desenvolvedores de software
  - Empresa JCPM (shopping centers/imobiliário)
- **Execução Agendada**: Roda automaticamente 2x por dia
- **GitHub Pages**: Gera site HTML automaticamente hospedado
- **Múltiplos Formatos**: Salva dados em TXT e JSON

## 📁 Estrutura do Projeto

```
agent_ai_news/
├── sources/                    # Crawlers por fonte
│   ├── base_crawler.py        # Classe base
│   ├── techcrunch_crawler.py  # TechCrunch
│   ├── venturebeat_crawler.py # VentureBeat
│   └── mit_technology_review_crawler.py # MIT Tech Review
├── src/                       # Código principal
│   ├── crawler_manager.py     # Gerenciador de crawlers
│   ├── news_analyzer.py       # Análise com LLM
│   ├── html_generator.py      # Gerador de HTML
│   └── utils/
│       └── logger.py          # Sistema de logging
├── docs/                      # HTML para GitHub Pages
├── news_data/                 # Dados coletados
├── logs/                      # Arquivos de log
├── .github/workflows/         # GitHub Actions
├── main.py                    # Script principal
├── scheduler.py               # Agendador
├── run_once.py               # Execução única
└── requirements.txt          # Dependências
```

## 🚀 Configuração

### 1. Clonar o Repositório

```bash
git clone <seu-repositorio>
cd agent_ai_news
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente

Copie o arquivo de exemplo e configure suas chaves:

```bash
cp .env.example .env
```

Edite o arquivo `.env`:

```env
# OpenRouter API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Model Configuration
DEFAULT_MODEL=anthropic/claude-3-haiku

# GitHub Configuration (para GitHub Pages)
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=your_username/your_repo_name
GITHUB_BRANCH=gh-pages

# News Configuration
MAX_NEWS_PER_SOURCE=10
OUTPUT_DIR=news_data
HTML_OUTPUT_DIR=docs
```

### 4. Obter Chave da OpenRouter

1. Acesse [OpenRouter](https://openrouter.ai/)
2. Crie uma conta
3. Gere uma API key
4. Adicione a chave no arquivo `.env`

## 🎮 Como Usar

### Execução Única (Teste)

```bash
python run_once.py
```

### Execução com Agendamento

```bash
python scheduler.py
```

### Execução Manual

```bash
python main.py
```

## 🔄 Automação com GitHub Actions

O projeto inclui automação completa via GitHub Actions:

### Configuração no GitHub

1. **Secrets necessários**:
   - `OPENROUTER_API_KEY`: Sua chave da OpenRouter

2. **Habilitar GitHub Pages**:
   - Vá em Settings > Pages
   - Source: Deploy from a branch
   - Branch: `gh-pages`

### Funcionamento

- **Execução automática**: 2x por dia (08:00 e 18:00 UTC)
- **Execução manual**: Via GitHub Actions tab
- **Deploy automático**: Para GitHub Pages após cada execução

## 📊 Fontes de Notícias

Atualmente o sistema coleta de:

- **TechCrunch** - Seção de IA
- **VentureBeat** - Feed RSS de IA  
- **MIT Technology Review** - Seção de IA

### Adicionar Nova Fonte

1. Crie um novo crawler em `sources/`:

```python
from .base_crawler import BaseCrawler

class NovaFonteCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("Nova Fonte", "https://exemplo.com")
    
    def get_news_urls(self):
        # Implementar lógica para obter URLs
        pass
    
    def extract_article_content(self, url):
        # Implementar extração de conteúdo
        pass
```

2. Adicione no `crawler_manager.py`:

```python
from sources.nova_fonte_crawler import NovaFonteCrawler

# No __init__:
self.crawlers = [
    TechCrunchCrawler(),
    VentureBeatCrawler(),
    MITTechnologyReviewCrawler(),
    NovaFonteCrawler()  # Adicionar aqui
]
```

## 📈 Análise com IA

Cada notícia é analisada pelo LLM gerando:

### 📋 Resumo Executivo
Resumo conciso da notícia

### 👨‍💻 Impacto para Desenvolvedores
- Novas oportunidades de desenvolvimento
- Tecnologias que podem ser adotadas
- Mudanças nas práticas de desenvolvimento
- Impacto nas ferramentas e frameworks

### 🏢 Impacto para JCPM (Shopping Centers/Imobiliário)
- Oportunidades de implementação de IA
- Melhorias na experiência do cliente
- Otimização de operações
- Novas fontes de receita
- Automação de processos

### 🎯 Pontos-Chave
Lista dos principais pontos da notícia

### ⭐ Nível de Relevância
Classificação: Alto/Médio/Baixo com justificativa

## 📱 Interface Web

O sistema gera automaticamente um site HTML moderno com:

- **Design Responsivo**: Funciona em desktop e mobile
- **Filtros**: Por nível de relevância
- **Animações**: Interface fluida e moderna
- **API JSON**: Dados disponíveis em formato JSON

### Acesso ao Site

Após configurar GitHub Pages: `https://seu-usuario.github.io/agent_ai_news`

## 📝 Logs e Monitoramento

- **Logs detalhados**: Salvos em `logs/`
- **Formato estruturado**: Data, hora, nível, mensagem
- **Rotação automática**: Por data
- **Console e arquivo**: Saída dupla

## 🛠️ Desenvolvimento

### Estrutura de Classes

```python
# Crawler base
BaseCrawler
├── get_news_urls()          # Obter URLs das notícias
├── extract_article_content() # Extrair conteúdo
└── crawl()                  # Processo completo

# Gerenciador
CrawlerManager
├── crawl_all_sources()      # Executar todos os crawlers
├── save_news_to_file()      # Salvar em TXT
└── save_consolidated_news() # Salvar JSON consolidado

# Analisador
NewsAnalyzer
├── analyze_news()           # Analisar com LLM
├── _create_analysis_prompt() # Criar prompt
└── _parse_analysis_response() # Parse da resposta

# Gerador HTML
HTMLGenerator
├── generate_html()          # Gerar site completo
├── _generate_index_page()   # Página principal
├── _generate_css()          # Estilos
└── _generate_js()           # JavaScript
```

### Testes

```bash
# Testar crawler específico
python -c "from sources.techcrunch_crawler import TechCrunchCrawler; c = TechCrunchCrawler(); print(c.crawl(max_articles=2))"

# Testar análise
python -c "from src.news_analyzer import NewsAnalyzer; a = NewsAnalyzer(); print(a._simulate_analysis({'title': 'Test'}))"
```

## 🔧 Troubleshooting

### Problemas Comuns

1. **Erro de API Key**:
   - Verifique se `OPENROUTER_API_KEY` está configurada
   - Teste a chave no site da OpenRouter

2. **Crawler não encontra notícias**:
   - Sites podem ter mudado estrutura HTML
   - Verifique logs para detalhes
   - Atualize seletores CSS se necessário

3. **GitHub Pages não atualiza**:
   - Verifique se GitHub Actions está habilitado
   - Confirme se branch `gh-pages` existe
   - Verifique permissões do repositório

4. **Dependências**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

### Debug

```bash
# Executar com logs detalhados
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from main import main
main()
"
```

## 📄 Licença

Este projeto é desenvolvido para uso interno da JCPM.

## 🤝 Contribuição

Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

---

**Desenvolvido com ❤️ e IA para JCPM**