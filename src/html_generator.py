"""
HTML Generator
Gerador de HTML para GitHub Pages
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import logging

class HTMLGenerator:
    """Gerador de HTML para exibir notícias no GitHub Pages"""
    
    def __init__(self):
        self.logger = logging.getLogger("html_generator")
        self.output_dir = Path(os.getenv('HTML_OUTPUT_DIR', 'docs'))
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_html(self, analyzed_news: List[Dict]):
        """Gerar HTML com as notícias analisadas"""
        
        if not analyzed_news:
            self.logger.warning("Nenhuma notícia para gerar HTML")
            return
        
        try:
            # Gerar página principal
            self._generate_index_page(analyzed_news)
            
            # Gerar CSS
            self._generate_css()
            
            # Gerar JavaScript
            self._generate_js()
            
            # Gerar arquivo JSON para API
            self._generate_json_api(analyzed_news)
            
            self.logger.info(f"HTML gerado com sucesso em: {self.output_dir}")
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar HTML: {e}")
    
    def _generate_index_page(self, analyzed_news: List[Dict]):
        """Gerar página principal HTML"""
        
        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IA BONNER - Notícias de IA</title>
    <link rel="stylesheet" href="styles.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <div class="header-content">
                <h1><i class="fas fa-robot"></i> AI News Agent</h1>
                <p class="subtitle">Notícias de IA para Desenvolvedores e Empresas</p>
                <div class="update-info">
                    <i class="fas fa-clock"></i>
                    Última atualização: {datetime.now().strftime('%d/%m/%Y às %H:%M')}
                </div>
            </div>
        </div>
    </header>

    <main class="main">
        <div class="container">
            <div class="stats-section">
                <div class="stat-card">
                    <i class="fas fa-newspaper"></i>
                    <div class="stat-info">
                        <span class="stat-number">{len(analyzed_news)}</span>
                        <span class="stat-label">Notícias Analisadas</span>
                    </div>
                </div>
                <div class="stat-card">
                    <i class="fas fa-globe"></i>
                    <div class="stat-info">
                        <span class="stat-number">{len(set([news['source'] for news in analyzed_news]))}</span>
                        <span class="stat-label">Fontes</span>
                    </div>
                </div>
                <div class="stat-card">
                    <i class="fas fa-brain"></i>
                    <div class="stat-info">
                        <span class="stat-number">100%</span>
                        <span class="stat-label">Análise IA</span>
                    </div>
                </div>
            </div>

            <div class="filters">
                <button class="filter-btn active" data-filter="all">Todas</button>
                <button class="filter-btn" data-filter="alto">Alta Relevância</button>
                <button class="filter-btn" data-filter="medio">Média Relevância</button>
                <button class="filter-btn" data-filter="baixo">Baixa Relevância</button>
            </div>

            <div class="news-grid" id="newsGrid">
                {self._generate_news_cards(analyzed_news)}
            </div>
        </div>
    </main>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2025 Paulo Marcelo - AI News Agent.</p>
        </div>
    </footer>

    <script src="script.js"></script>
</body>
</html>"""
        
        with open(self.output_dir / "index.html", 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_news_cards(self, analyzed_news: List[Dict]) -> str:
        """Gerar cards das notícias"""
        
        cards_html = ""
        
        for i, news in enumerate(analyzed_news):
            analysis = news.get('analysis', {})
            
            # Determinar nível de relevância
            relevancia = analysis.get('nivel_relevancia', 'Médio').lower()
            if 'alto' in relevancia:
                relevancia_class = 'alto'
                relevancia_icon = 'fas fa-fire'
                relevancia_color = '#e74c3c'
            elif 'baixo' in relevancia:
                relevancia_class = 'baixo'
                relevancia_icon = 'fas fa-leaf'
                relevancia_color = '#95a5a6'
            else:
                relevancia_class = 'medio'
                relevancia_icon = 'fas fa-star'
                relevancia_color = '#f39c12'
            
            cards_html += f"""
            <article class="news-card" data-relevancia="{relevancia_class}">
                <div class="news-header">
                    <div class="source-info">
                        <span class="source">{news.get('source', 'N/A')}</span>
                        <span class="date">{self._format_date(news.get('published_date', ''))}</span>
                    </div>
                    <div class="relevancia-badge" style="color: {relevancia_color}">
                        <i class="{relevancia_icon}"></i>
                        {relevancia_class.title()}
                    </div>
                </div>
                
                <h2 class="news-title">{news.get('title', 'Título não disponível')}</h2>
                
                <div class="news-summary">
                    {analysis.get('resumo_executivo', 'Resumo não disponível')}
                </div>
                
                <div class="analysis-sections">                                                                    
                    <div class="analysis-section">
                        <h3><i class="fas fa-list"></i> Pontos-Chave</h3>
                        <div class="pontos-chave">
                            {self._format_pontos_chave(analysis.get('pontos_chave', ''))}
                        </div>
                    </div>
                </div>
                
                <div class="news-footer">
                    <a href="{news.get('url', '#')}" target="_blank" class="read-more">
                        <i class="fas fa-external-link-alt"></i>
                        Ler notícia completa
                    </a>
                    <span class="author">Por: {news.get('author', 'Autor não informado')}</span>
                </div>
            </article>
            """
        
        return cards_html
    
    def _format_pontos_chave(self, pontos_chave: str) -> str:
        """Formatar pontos-chave como lista HTML"""
        if not pontos_chave:
            return "<p>Pontos-chave não disponíveis</p>"
        
        lines = pontos_chave.split('\\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('•') or line.startswith('-')):
                # Remover marcador e adicionar como item de lista
                text = line[1:].strip()
                formatted_lines.append(f"<li>{text}</li>")
        
        if formatted_lines:
            return f"<ul>{''.join(formatted_lines)}</ul>"
        else:
            return f"<p>{pontos_chave}</p>"
    
    def _format_date(self, date_str: str) -> str:
        """Formatar data para exibição"""
        if not date_str or date_str == "Data não encontrada":
            return "Data não disponível"
        
        try:
            # Tentar diferentes formatos de data
            for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%d/%m/%Y']:
                try:
                    dt = datetime.strptime(date_str[:19], fmt)
                    return dt.strftime('%d/%m/%Y')
                except ValueError:
                    continue
            return date_str
        except:
            return "Data não disponível"
    
    def _generate_css(self):
        """Gerar arquivo CSS"""
        
        css_content = """
/* Reset e Base */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #2c3e50;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Header */
.header {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    padding: 2rem 0;
    margin-bottom: 2rem;
}

.header-content {
    text-align: center;
}

.header h1 {
    font-size: 2.5rem;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 0.5rem;
}

.header h1 i {
    color: #667eea;
    margin-right: 0.5rem;
}

.subtitle {
    font-size: 1.2rem;
    color: #7f8c8d;
    margin-bottom: 1rem;
}

.update-info {
    display: inline-flex;
    align-items: center;
    background: #ecf0f1;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.9rem;
    color: #34495e;
}

.update-info i {
    margin-right: 0.5rem;
    color: #667eea;
}

/* Stats Section */
.stats-section {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    padding: 1.5rem;
    border-radius: 15px;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    transition: transform 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-5px);
}

.stat-card i {
    font-size: 2rem;
    color: #667eea;
    margin-right: 1rem;
}

.stat-info {
    display: flex;
    flex-direction: column;
}

.stat-number {
    font-size: 2rem;
    font-weight: 700;
    color: #2c3e50;
}

.stat-label {
    font-size: 0.9rem;
    color: #7f8c8d;
}

/* Filters */
.filters {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
}

.filter-btn {
    background: rgba(255, 255, 255, 0.9);
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 25px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    color: #2c3e50;
}

.filter-btn:hover,
.filter-btn.active {
    background: #667eea;
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

/* News Grid */
.news-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 2rem;
    margin-bottom: 3rem;
}

/* News Cards */
.news-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.news-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.news-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.source-info {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.source {
    font-weight: 600;
    color: #667eea;
    font-size: 0.9rem;
}

.date {
    font-size: 0.8rem;
    color: #7f8c8d;
}

.relevancia-badge {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;
    font-size: 0.9rem;
}

.news-title {
    font-size: 1.3rem;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 1rem;
    line-height: 1.4;
}

.news-summary {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 1.5rem;
    font-style: italic;
    color: #34495e;
    border-left: 4px solid #667eea;
}

.analysis-sections {
    margin-bottom: 1.5rem;
}

.analysis-section {
    margin-bottom: 1.5rem;
}

.analysis-section h3 {
    font-size: 1rem;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.analysis-section h3 i {
    color: #667eea;
}

.analysis-section p {
    color: #34495e;
    line-height: 1.6;
}

.pontos-chave ul {
    list-style: none;
    padding-left: 0;
}

.pontos-chave li {
    padding: 0.25rem 0;
    position: relative;
    padding-left: 1.5rem;
}

.pontos-chave li:before {
    content: "▶";
    color: #667eea;
    position: absolute;
    left: 0;
}

.news-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 1rem;
    border-top: 1px solid #ecf0f1;
}

.read-more {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    color: #667eea;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.3s ease;
}

.read-more:hover {
    color: #5a6fd8;
}

.author {
    font-size: 0.9rem;
    color: #7f8c8d;
}

/* Footer */
.footer {
    background: rgba(44, 62, 80, 0.9);
    color: white;
    text-align: center;
    padding: 2rem 0;
    margin-top: 3rem;
}

/* Responsive */
@media (max-width: 768px) {
    .news-grid {
        grid-template-columns: 1fr;
    }
    
    .header h1 {
        font-size: 2rem;
    }
    
    .news-card {
        padding: 1.5rem;
    }
    
    .news-footer {
        flex-direction: column;
        gap: 1rem;
        align-items: flex-start;
    }
}

/* Animações */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.news-card {
    animation: fadeIn 0.6s ease forwards;
}

.news-card:nth-child(even) {
    animation-delay: 0.1s;
}

.news-card:nth-child(odd) {
    animation-delay: 0.2s;
}
"""
        
        with open(self.output_dir / "styles.css", 'w', encoding='utf-8') as f:
            f.write(css_content)
    
    def _generate_js(self):
        """Gerar arquivo JavaScript"""
        
        js_content = """
// Funcionalidade de filtros
document.addEventListener('DOMContentLoaded', function() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const newsCards = document.querySelectorAll('.news-card');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remover classe active de todos os botões
            filterButtons.forEach(btn => btn.classList.remove('active'));
            
            // Adicionar classe active ao botão clicado
            this.classList.add('active');
            
            const filter = this.getAttribute('data-filter');
            
            // Filtrar cards
            newsCards.forEach(card => {
                if (filter === 'all') {
                    card.style.display = 'block';
                } else {
                    const relevancia = card.getAttribute('data-relevancia');
                    if (relevancia === filter) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                }
            });
        });
    });
    
    // Animação suave para scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Adicionar efeito de loading
    const newsGrid = document.getElementById('newsGrid');
    if (newsGrid) {
        newsGrid.style.opacity = '0';
        setTimeout(() => {
            newsGrid.style.transition = 'opacity 0.5s ease';
            newsGrid.style.opacity = '1';
        }, 100);
    }
});

// Função para atualizar timestamp
function updateTimestamp() {
    const now = new Date();
    const timestamp = now.toLocaleString('pt-BR');
    const updateInfo = document.querySelector('.update-info');
    if (updateInfo) {
        updateInfo.innerHTML = `<i class="fas fa-clock"></i> Última atualização: ${timestamp}`;
    }
}

// Atualizar timestamp a cada minuto
setInterval(updateTimestamp, 60000);
"""
        
        with open(self.output_dir / "script.js", 'w', encoding='utf-8') as f:
            f.write(js_content)
    
    def _generate_json_api(self, analyzed_news: List[Dict]):
        """Gerar arquivo JSON para API"""
        
        api_data = {
            'timestamp': datetime.now().isoformat(),
            'total_news': len(analyzed_news),
            'sources': list(set([news['source'] for news in analyzed_news])),
            'news': analyzed_news
        }
        
        with open(self.output_dir / "api.json", 'w', encoding='utf-8') as f:
            json.dump(api_data, f, ensure_ascii=False, indent=2)