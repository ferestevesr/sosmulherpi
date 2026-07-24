const formulario = document.querySelector('.formulario');

formulario.addEventListener('submit', (e) => {

  e.preventDefault();

  const botao = document.querySelector('.btn-enviar');

  botao.innerHTML = 'Enviando denúncia...';

  botao.style.opacity = '0.8';

  setTimeout(() => {

    botao.innerHTML = 'Denúncia enviada com sucesso ✓';

    botao.style.background =
      'linear-gradient(135deg, #22c55e, #16a34a)';

  }, 2500);

});