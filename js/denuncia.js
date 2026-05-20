
const cards = document.querySelectorAll('.tipo-card');

cards.forEach(card => {

  card.addEventListener('click', () => {

    cards.forEach(c => {
      c.classList.remove('ativo');
    });

    card.classList.add('ativo');

  });

});

/* FORM */
const formulario = document.querySelector('.formulario');

formulario.addEventListener('submit', (e) => {

  e.preventDefault();

  const botao = document.querySelector('.btn-enviar');

  botao.innerHTML = 'Enviando denúncia...';

  botao.style.opacity = '0.8';

  setTimeout(() => {

    botao.innerHTML = 'Denúncia enviada ✓';

    botao.style.background =
      'linear-gradient(135deg, #22c55e, #16a34a)';

  }, 2500);

});

