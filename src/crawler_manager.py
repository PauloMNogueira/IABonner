"""
Crawler Manager
Gerenciador que coordena todos os crawlers de notícias
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict
from pathlib import Path

# Importar crawlers
from sources.techcrunch_crawler import TechCrunchCrawler
from sources.mit_technology_review_crawler import MITTechnologyReviewCrawler

class CrawlerManager:
    """Gerenciador de crawlers de notícias"""
    
    def __init__(self):
        self.logger = logging.getLogger("crawler_manager")
        self.output_dir = Path(os.getenv('OUTPUT_DIR', 'news_data'))
        self.output_dir.mkdir(exist_ok=True)
        
        # Inicializar crawlers
        self.crawlers = [
            TechCrunchCrawler(),
            MITTechnologyReviewCrawler()
        ]
    
    def crawl_all_sources(self) -> List[Dict]:
        """Executar crawler em todas as fontes"""
        self.logger.info("Iniciando crawler em todas as fontes")
        
        all_news = []
        
        for crawler in self.crawlers:
            try:
                self.logger.info(f"Executando crawler: {crawler.source_name}")
                
                max_articles = int(os.getenv('MAX_NEWS_PER_SOURCE', 10))
                news = crawler.crawl(max_articles=max_articles)
                
                if news:
                    all_news.extend(news)
                    self.save_news_to_file(news, crawler.source_name)
                    self.logger.info(f"{crawler.source_name}: {len(news)} notícias coletadas")
                else:
                    self.logger.warning(f"{crawler.source_name}: Nenhuma notícia coletada")
                    
            except Exception as e:
                self.logger.error(f"Erro no crawler {crawler.source_name}: {e}")
                continue
        
        self.logger.info(f"Crawler concluído: {len(all_news)} notícias no total")
        
        # Salvar todas as notícias em um arquivo consolidado
        if all_news:
            self.save_consolidated_news(all_news)
        
        return all_news
    
    def save_news_to_file(self, news: List[Dict], source_name: str):
        """Salvar notícias de uma fonte específica em arquivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{source_name.lower().replace(' ', '_')}_{timestamp}.txt"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Notícias de {source_name}\\n")
                f.write(f"# Coletadas em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
                f.write(f"# Total de notícias: {len(news)}\\n\\n")
                
                for i, article in enumerate(news, 1):
                    f.write(f"## Notícia {i}\\n")
                    f.write(f"**Título:** {article.get('title', 'N/A')}\\n")
                    f.write(f"**Autor:** {article.get('author', 'N/A')}\\n")
                    f.write(f"**Data:** {article.get('published_date', 'N/A')}\\n")
                    f.write(f"**URL:** {article.get('url', 'N/A')}\\n")
                    f.write(f"**Resumo:** {article.get('summary', 'N/A')}\\n")
                    f.write(f"**Conteúdo:** {article.get('content', 'N/A')}\\n")
                    f.write("\\n" + "="*80 + "\\n\\n")
            
            self.logger.info(f"Notícias de {source_name} salvas em: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar notícias de {source_name}: {e}")
    
    def save_consolidated_news(self, all_news: List[Dict]):
        """Salvar todas as notícias em um arquivo consolidado JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"consolidated_news_{timestamp}.json"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'total_news': len(all_news),
                    'sources': list(set([news['source'] for news in all_news])),
                    'news': all_news
                }, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Notícias consolidadas salvas em: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar notícias consolidadas: {e}")
    
    def get_latest_news_file(self) -> str:
        """Obter o arquivo de notícias mais recente"""
        json_files = list(self.output_dir.glob("consolidated_news_*.json"))
        if json_files:
            return str(max(json_files, key=os.path.getctime))
        return None