// Inicializa os ícones do Lucide
document.addEventListener("DOMContentLoaded", function () {

    if (window.lucide) {
        lucide.createIcons();
    }

});


// =========================================================
// ABRIR / FECHAR CARDS
// =========================================================

function toggleCard(card) {

    const cards = document.querySelectorAll(".card");

    cards.forEach(function (currentCard) {

        if (currentCard !== card) {
            currentCard.classList.remove("active");
        }

    });

    card.classList.toggle("active");

}


// =========================================================
// SAIR RÁPIDO
// =========================================================

function sairRapido() {

    document.body.innerHTML = "";

    window.location.replace(
        "https://www.google.com"
    );

}