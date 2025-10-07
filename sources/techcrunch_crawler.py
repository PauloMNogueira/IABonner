"""
TechCrunch Crawler
Crawler específico para notícias de IA do TechCrunch
"""

from typing import List, Dict, Optional
import re
from .base_crawler import BaseCrawler

class TechCrunchCrawler(BaseCrawler):
    """Crawler para TechCrunch - seção de IA"""
    
    def __init__(self):
        super().__init__(
            source_name="TechCrunch",
            base_url="https://techcrunch.com"
        )
        self.ai_section_url = "https://techcrunch.com/category/artificial-intelligence/"
    
    def get_news_urls(self) -> List[str]:
        """Obter URLs das notícias de IA do TechCrunch"""
        response = self.make_request(self.ai_section_url)
        if not response:
            return []
        
        soup = self.parse_html(response.text)
        urls = []
        
        # Procurar por links de artigos - seletores mais específicos
        article_links = soup.find_all('a', href=True, class_=lambda x: x and ('post-block__title__link' in x or 'river-block__title-link' in x))
        
        # Se não encontrar com classes específicas, tentar uma abordagem mais ampla
        if not article_links:
            article_links = soup.find_all('a', href=True)
        
        for link in article_links:
            href = link.get('href')
            # Aceitar qualquer artigo do TechCrunch, não apenas de 2024/2025
            if href and 'techcrunch.com' in href and '/20' in href:
                # Filtrar apenas artigos relacionados a IA
                title = link.get_text().lower()
                if any(keyword in title for keyword in ['ai', 'artificial intelligence', 'machine learning', 'llm', 'gpt', 'openai', 'anthropic', 'chatgpt', 'claude', 'gemini']):
                    if href not in urls:
                        urls.append(href)
        
        return urls[:15]  # Limitar a 15 URLs
    
    def extract_article_content(self, url: str) -> Optional[Dict]:
        """Extrair conteúdo do artigo do TechCrunch"""
        response = self.make_request(url)
        if not response:
            return None
        
        soup = self.parse_html(response.text)
        
        try:
            # Extrair título
            title_elem = soup.find('h1', class_='wp-block-post-title') or soup.find('h1')
            title = self.clean_text(title_elem.get_text()) if title_elem else "Título não encontrado"
            
            # Extrair conteúdo do artigo
            content_elem = soup.find('div', class_='entry-content') or soup.find('article')
            if content_elem:
                # Remover elementos desnecessários
                for elem in content_elem.find_all(['script', 'style', 'aside', 'nav']):
                    elem.decompose()
                
                paragraphs = content_elem.find_all('p')
                content = ' '.join([self.clean_text(p.get_text()) for p in paragraphs])
            else:
                content = "Conteúdo não encontrado"
            
            # Extrair data de publicação
            date_elem = soup.find('time') or soup.find('span', class_='date')
            published_date = date_elem.get('datetime') if date_elem and date_elem.get('datetime') else "Data não encontrada"
            
            # Extrair autor
            author_elem = soup.find('a', class_='author') or soup.find('span', class_='author')
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