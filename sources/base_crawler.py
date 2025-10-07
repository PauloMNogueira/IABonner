"""
Base Crawler Class
Classe base para todos os crawlers de notícias
"""

import requests
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional
import logging
from bs4 import BeautifulSoup
import time

class BaseCrawler(ABC):
    """Classe base para crawlers de notícias"""
    
    def __init__(self, source_name: str, base_url: str):
        self.source_name = source_name
        self.base_url = base_url
        self.logger = logging.getLogger(f"crawler.{source_name}")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    @abstractmethod
    def get_news_urls(self) -> List[str]:
        """Método abstrato para obter URLs das notícias"""
        pass
    
    @abstractmethod
    def extract_article_content(self, url: str) -> Optional[Dict]:
        """Método abstrato para extrair conteúdo do artigo"""
        pass
    
    def crawl(self, max_articles: int = 10) -> List[Dict]:
        """Método principal para fazer crawler das notícias"""
        self.logger.info(f"Iniciando crawler para {self.source_name}")
        
        try:
            # Obter URLs das notícias
            news_urls = self.get_news_urls()
            
            if not news_urls:
                self.logger.warning(f"Nenhuma URL encontrada para {self.source_name}")
                return []
            
            # Limitar número de artigos
            news_urls = news_urls[:max_articles]
            
            articles = []
            for i, url in enumerate(news_urls):
                try:
                    self.logger.info(f"Processando artigo {i+1}/{len(news_urls)}: {url}")
                    
                    article = self.extract_article_content(url)
                    if article:
                        article['source'] = self.source_name
                        article['url'] = url
                        article['crawled_at'] = datetime.now().isoformat()
                        articles.append(article)
                    
                    # Delay entre requisições para ser respeitoso
                    time.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Erro ao processar {url}: {e}")
                    continue
            
            self.logger.info(f"Crawler {self.source_name} concluído: {len(articles)} artigos")
            return articles
            
        except Exception as e:
            self.logger.error(f"Erro no crawler {self.source_name}: {e}")
            return []
    
    def make_request(self, url: str, timeout: int = 10) -> Optional[requests.Response]:
        """Fazer requisição HTTP com tratamento de erro"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            self.logger.error(f"Erro na requisição para {url}: {e}")
            return None
    
    def parse_html(self, html_content: str) -> BeautifulSoup:
        """Parse do conteúdo HTML"""
        return BeautifulSoup(html_content, 'html.parser')
    
    def clean_text(self, text: str) -> str:
        """Limpar e normalizar texto"""
        if not text:
            return ""
        
        # Remover espaços extras e quebras de linha
        text = ' '.join(text.split())
        return text.strip()