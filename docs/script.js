
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
