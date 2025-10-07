"""
Logger Configuration
Configuração do sistema de logging
"""

import logging
import os
from datetime import datetime
from pathlib import Path

def setup_logger(log_level: str = "INFO") -> logging.Logger:
    """Configurar sistema de logging"""
    
    # Criar diretório de logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Nome do arquivo de log com timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = log_dir / f"ai_news_agent_{timestamp}.log"
    
    # Configurar formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configurar handler para arquivo
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Configurar handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Configurar logger principal
    logger = logging.getLogger("ai_news_agent")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remover handlers existentes para evitar duplicação
    logger.handlers.clear()
    
    # Adicionar handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Evitar propagação para o logger raiz
    logger.propagate = False
    
    return logger