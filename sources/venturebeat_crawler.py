"""
VentureBeat Crawler
Crawler específico para notícias de IA do VentureBeat
"""

from typing import List, Dict, Optional
import feedparser
import re
from .base_crawler import BaseCrawler

class VentureBeatCrawler(BaseCrawler):
    """Crawler para VentureBeat - seção de IA"""
    
    def __init__(self):
        super().__init__(
            source_name="VentureBeat",
            base_url="https://venturebeat.com"
        )
        # Usar o RSS principal e filtrar por IA
        self.main_rss_url = "https://venturebeat.com/feed/"
        self.ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'llm', 'gpt', 'openai', 'anthropic', 'claude', 'gemini', 'chatgpt', 'generative', 'neural', 'deep learning']
    
    def get_news_urls(self) -> List[str]:
        """Obter URLs das notícias de IA do VentureBeat via RSS"""
        try:
            feed = feedparser.parse(self.main_rss_url)
            urls = []
            
            if not feed.entries:
                self.logger.error("Nenhuma entrada encontrada no RSS do VentureBeat")
                return []
            
            self.logger.info(f"VentureBeat RSS: {len(feed.entries)} entradas encontradas")
            
            for entry in feed.entries:
                if hasattr(entry, 'link') and hasattr(entry, 'title'):
                    # Filtrar por palavras-chave relacionadas à IA
                    title_lower = entry.title.lower()
                    summary_lower = getattr(entry, 'summary', '').lower()
                    
                    # Verificar se contém palavras-chave de IA
                    if any(keyword in title_lower or keyword in summary_lower for keyword in self.ai_keywords):
                        urls.append(entry.link)
                        self.logger.debug(f"URL de IA encontrada: {entry.title}")
                        
                        # Limitar a 15 URLs de IA
                        if len(urls) >= 15:
                            break
            
            self.logger.info(f"VentureBeat: {len(urls)} URLs de IA filtradas")
            return urls
            
        except Exception as e:
            self.logger.error(f"Erro ao processar RSS do VentureBeat: {e}")
            return []
    
    def extract_article_content(self, url: str) -> Optional[Dict]:
        """Extrair conteúdo do artigo do VentureBeat"""
        response = self.make_request(url)
        if not response:
            return None
        
        soup = self.parse_html(response.text)
        
        try:
            # Extrair título - tentar múltiplos seletores
            title_elem = (soup.find('h1', class_=re.compile(r'.*title.*', re.I)) or
                         soup.find('h1', class_=re.compile(r'.*headline.*', re.I)) or
                         soup.find('h1') or
                         soup.find('title'))
            title = self.clean_text(title_elem.get_text()) if title_elem else "Título não encontrado"
            
            # Extrair conteúdo do artigo - tentar múltiplos seletores
            content_elem = (soup.find('div', class_=re.compile(r'.*content.*', re.I)) or
                           soup.find('div', class_=re.compile(r'.*entry.*', re.I)) or
                           soup.find('div', class_=re.compile(r'.*body.*', re.I)) or
                           soup.find('article') or
                           soup.find('main'))
            
            if content_elem:
                # Remover elementos desnecessários
                for elem in content_elem.find_all(['script', 'style', 'aside', 'nav', 'figure', 'header', 'footer']):
                    elem.decompose()
                
                paragraphs = content_elem.find_all('p')
                content = ' '.join([self.clean_text(p.get_text()) for p in paragraphs if p.get_text().strip()])
            else:
                # Fallback: pegar todos os parágrafos da página
                paragraphs = soup.find_all('p')
                content = ' '.join([self.clean_text(p.get_text()) for p in paragraphs[:10] if p.get_text().strip()])
            
            if not content.strip():
                content = "Conteúdo não encontrado"
            
            # Extrair data de publicação
            date_elem = (soup.find('time') or
                        soup.find('span', class_=re.compile(r'.*date.*', re.I)) or
                        soup.find('div', class_=re.compile(r'.*date.*', re.I)) or
                        soup.find('span', class_=re.compile(r'.*time.*', re.I)))
            
            published_date = "Data não encontrada"
            if date_elem:
                if date_elem.get('datetime'):
                    published_date = date_elem.get('datetime')
                elif date_elem.get_text():
                    published_date = self.clean_text(date_elem.get_text())
            
            # Extrair autor
            author_elem = (soup.find('span', class_=re.compile(r'.*author.*', re.I)) or
                          soup.find('a', class_=re.compile(r'.*author.*', re.I)) or
                          soup.find('div', class_=re.compile(r'.*byline.*', re.I)) or
                          soup.find('a', rel='author'))
            author = self.clean_text(author_elem.get_text()) if author_elem else "Autor não encontrado"
            
            return {
                'title': title,
                'content': content[:2000],  # Limitar conteúdo
                'author': author,
                'published_date': published_date,
                'summary': content[:300] + "..." if len(content) > 300 else content
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair conteúdo de {url}: {e}")
            return None