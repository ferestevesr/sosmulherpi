// Inicializa ícones
lucide.createIcons();

// Função de abrir/fechar cards
function toggleCard(card) {

    const cards = document.querySelectorAll('.card');

    cards.forEach(currentCard => {

        if (currentCard !== card) {
            currentCard.classList.remove('active');
        }

    });

    card.classList.toggle('active');
}

// Botão sair rápido
function sairRapido() {

    document.body.innerHTML = "";

    window.location.replace("https://www.google.com");
}