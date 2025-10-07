#!/usr/bin/env python3
"""
Run Once
Script para executar o AI News Agent uma única vez (útil para testes)
"""

import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from main import main

if __name__ == "__main__":
    print("🤖 Executando AI News Agent...")
    print("=" * 50)
    
    try:
        main()
        print("=" * 50)
        print("✅ Execução concluída com sucesso!")
        
    except KeyboardInterrupt:
        print("\\n❌ Execução interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro na execução: {e}")
        sys.exit(1)