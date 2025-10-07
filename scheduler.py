#!/usr/bin/env python3
"""
Scheduler
Sistema de agendamento para execução diária do AI News Agent
"""

import schedule
import time
import logging
import sys
from datetime import datetime
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from main import main as run_news_agent
from src.utils.logger import setup_logger

def scheduled_job():
    """Tarefa agendada para executar o agente de notícias"""
    logger = logging.getLogger("scheduler")
    
    try:
        logger.info("Iniciando execução agendada do AI News Agent")
        run_news_agent()
        logger.info("Execução agendada concluída com sucesso")
        
    except Exception as e:
        logger.error(f"Erro na execução agendada: {e}")

def main():
    """Função principal do scheduler"""
    
    # Configurar logging
    logger = setup_logger()
    logger.info("Iniciando AI News Agent Scheduler")
    
    # Agendar execução diária às 08:00
    schedule.every().day.at("08:00").do(scheduled_job)
    
    # Também agendar para às 18:00 (opcional)
    schedule.every().day.at("18:00").do(scheduled_job)
    
    logger.info("Agendamento configurado:")
    logger.info("- Execução diária às 08:00")
    logger.info("- Execução diária às 18:00")
    logger.info("Pressione Ctrl+C para parar o scheduler")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar a cada minuto
            
    except KeyboardInterrupt:
        logger.info("Scheduler interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro no scheduler: {e}")

if __name__ == "__main__":
    main()