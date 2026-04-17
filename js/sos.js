const botao = document.getElementById("btnSOS");
const barra = document.getElementById("barra");
const status = document.getElementById("status");

botao.addEventListener("click", () => {

  status.innerHTML = "Enviando localização...";
  barra.style.width = "30%";

  setTimeout(() => {
    status.innerHTML = "Contato de emergência acionado";
    barra.style.width = "70%";
  }, 1500);

  setTimeout(() => {
    status.innerHTML = "Ajuda a caminho ✔️";
    barra.style.width = "100%";
  }, 3000);

});