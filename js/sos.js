const btn = document.getElementById("btnSOS");
const barra = document.getElementById("barra");
const status = document.getElementById("status");

const wrapper = document.getElementById("cardsWrapper");

const loc = document.getElementById("loc");
const contatos = document.getElementById("contatos");
const ajuda = document.getElementById("ajuda");
const geral = document.getElementById("geral");

let ativo = false;

btn.addEventListener("click", () => {
  if (ativo) return;
  ativo = true;

  // ATIVA SEGUNDO CARD
  wrapper.classList.add("ativo");

  // ETAPA 1
  status.innerHTML = "Enviando localização...";
  barra.style.width = "30%";
  loc.innerText = "🟡 Enviando...";
  geral.innerText = "Ativo";

  setTimeout(() => {
    // ETAPA 2
    status.innerHTML = "Notificando contatos...";
    barra.style.width = "60%";
    loc.innerText = "🟢 Enviado";
    contatos.innerText = "2 contatos ✔";
  }, 1500);

  setTimeout(() => {
    // ETAPA 3
    status.innerHTML = "Ajuda a caminho 🚨";
    barra.style.width = "100%";
    ajuda.innerText = "A caminho ✔";
    geral.innerText = "Finalizado";
  }, 3000);
});