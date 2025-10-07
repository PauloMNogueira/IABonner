"""
MIT Technology Review Crawler
Crawler específico para notícias de IA do MIT Technology Review
"""

from typing import List, Dict, Optional
import re
import feedparser
from .base_crawler import BaseCrawler

class MITTechnologyReviewCrawler(BaseCrawler):
    """Crawler para MIT Technology Review - seção de IA"""
    
    def __init__(self):
        super().__init__(
            source_name="MIT Technology Review",
            base_url="https://www.technologyreview.com"
        )
        self.rss_url = "https://www.technologyreview.com/feed/"
        
        # Palavras-chave para filtrar artigos relacionados à IA
        self.ai_keywords = [
            'artificial intelligence', 'ai', 'machine learning', 'deep learning',
            'neural network', 'chatgpt', 'openai', 'llm', 'large language model',
            'generative ai', 'automation', 'robot', 'algorithm', 'data science',
            'computer vision', 'natural language', 'nlp', 'gpt', 'claude',
            'gemini', 'anthropic', 'microsoft ai', 'google ai', 'meta ai',
            'agent', 'ai agent', 'autonomous', 'intelligent system'
        ]
    
    def get_news_urls(self) -> List[str]:
        """Obter URLs de notícias de IA usando RSS feed"""
        try:
            self.logger.debug(f"Acessando RSS feed: {self.rss_url}")
            feed = feedparser.parse(self.rss_url)
            
            if not feed.entries:
                self.logger.warning(f"MIT Technology Review: Nenhuma entrada encontrada no RSS feed")
                return []
            
            ai_urls = []
            
            for entry in feed.entries:
                title = entry.title.lower()
                summary = getattr(entry, 'summary', '').lower()
                
                # Verificar se o artigo é relacionado à IA
                is_ai_related = any(keyword in title or keyword in summary 
                                  for keyword in self.ai_keywords)
                
                if is_ai_related:
                    ai_urls.append(entry.link)
                    self.logger.debug(f"URL de IA encontrada: {entry.title}")
            
            self.logger.info(f"MIT Technology Review: {len(ai_urls)} URLs de IA filtradas")
            return ai_urls[:15]  # Limitar a 15 artigos
            
        except Exception as e:
            self.logger.error(f"Erro ao obter URLs do MIT Technology Review: {e}")
            return []
    
    def extract_article_content(self, url: str) -> Optional[Dict]:
        """Extrair conteúdo do artigo do MIT Technology Review"""
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
                           soup.find('div', class_=re.compile(r'.*body.*', re.I)) or
                           soup.find('article') or
                           soup.find('main'))
            
            if content_elem:
                # Remover elementos desnecessários
                for elem in content_elem.find_all(['script', 'style', 'aside', 'nav', 'header', 'footer']):
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
                        soup.find('div', class_=re.compile(r'.*date.*', re.I)))
            
            published_date = "Data não encontrada"
            if date_elem:
                if date_elem.get('datetime'):
                    published_date = date_elem.get('datetime')
                elif date_elem.get_text():
                    published_date = self.clean_text(date_elem.get_text())
            
            # Extrair autor
            author_elem = (soup.find('span', class_=re.compile(r'.*author.*', re.I)) or
                          soup.find('a', class_=re.compile(r'.*author.*', re.I)) or
                          soup.find('div', class_=re.compile(r'.*byline.*', re.I)))
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