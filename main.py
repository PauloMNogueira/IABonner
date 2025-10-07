#!/usr/bin/env python3
"""
AI News Crawler Agent
Agente de IA para fazer crawler de notícias sobre IA dos principais sites
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Importar módulos do projeto
from src.crawler_manager import CrawlerManager
from src.news_analyzer import NewsAnalyzer
from src.html_generator import HTMLGenerator
from src.utils.logger import setup_logger

def main():
    """Função principal do agente de notícias de IA"""
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Configurar logging
    logger = setup_logger()
    logger.info("Iniciando AI News Crawler Agent")
    
    try:
        # Inicializar componentes
        crawler_manager = CrawlerManager()
        news_analyzer = NewsAnalyzer()
        html_generator = HTMLGenerator()
        
        # 1. Fazer crawler das notícias
        logger.info("Iniciando crawler de notícias...")
        news_data = crawler_manager.crawl_all_sources()
        
        if not news_data:
            logger.warning("Nenhuma notícia encontrada")
            return
        
        logger.info(f"Encontradas {len(news_data)} notícias")
        
        # 2. Analisar notícias com LLM
        logger.info("Analisando notícias com LLM...")
        analyzed_news = []
        
        for news in news_data:
            try:
                analysis = news_analyzer.analyze_news(news)
                if analysis:
                    analyzed_news.append({
                        **news,
                        'analysis': analysis
                    })
            except Exception as e:
                logger.error(f"Erro ao analisar notícia: {e}")
                continue
        
        logger.info(f"Analisadas {len(analyzed_news)} notícias")
        
        # 3. Gerar HTML
        logger.info("Gerando HTML...")
        html_generator.generate_html(analyzed_news)
        
        logger.info("Processo concluído com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro no processo principal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()