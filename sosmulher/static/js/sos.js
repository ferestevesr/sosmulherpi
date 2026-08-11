const btnSOS = document.getElementById("btnSOS");
const barra = document.getElementById("barra");
const statusTexto = document.getElementById("status");

const loc = document.getElementById("loc");
const contatos = document.getElementById("contatos");
const ajuda = document.getElementById("ajuda");
const geral = document.getElementById("geral");

const cancelar = document.querySelector(".cancelar");

let sistemaAtivo = false;

/* ESTADO INICIAL */
resetarSistema();

/* BOTÃO SOS */
btnSOS.addEventListener("click", () => {

  if (sistemaAtivo) return;

  sistemaAtivo = true;

  ativarBotao();

  statusTexto.innerHTML =
    "Iniciando protocolo de emergência...";

  geral.innerHTML = "🟢 Ativo";

  /* ETAPA 1 */
  setTimeout(() => {

    barra.style.width = "20%";

    statusTexto.innerHTML =
      "Solicitando localização da vítima...";

    loc.innerHTML = "🟡 Detectando localização";

  }, 1000);

  /* ETAPA 2 */
  setTimeout(() => {

    barra.style.width = "45%";

    statusTexto.innerHTML =
      "Conectando sistema de segurança...";

    loc.innerHTML = "🟢 Localização detectada";

    contatos.innerHTML = "🟡 Notificando contatos";

  }, 2500);

  /* ETAPA 3 */
  setTimeout(() => {

    barra.style.width = "70%";

    statusTexto.innerHTML =
      "Contatos de emergência avisados.";

    contatos.innerHTML = "🟢 2 contatos avisados";

    ajuda.innerHTML = "🟡 Equipe analisando situação";

  }, 4500);

  /* ETAPA 4 */
  setTimeout(() => {

    barra.style.width = "100%";

    statusTexto.innerHTML =
      "Ajuda acionada com sucesso 🚨";

    ajuda.innerHTML = "🟢 Ajuda a caminho";

    geral.innerHTML = "🟢 Emergência ativa";

    efeitoFinal();

  }, 6500);

});

/* CANCELAR */
cancelar.addEventListener("click", () => {

  sistemaAtivo = false;

  resetarSistema();

});

/* RESET */
function resetarSistema() {

  barra.style.width = "0%";

  statusTexto.innerHTML =
    "Pressione o botão para iniciar o pedido de ajuda.";

  loc.innerHTML = "Aguardando";
  contatos.innerHTML = "Aguardando";
  ajuda.innerHTML = "Aguardando";
  geral.innerHTML = "Inativo";

  btnSOS.style.transform = "scale(1)";
  btnSOS.style.boxShadow =
    "0 25px 60px rgba(255, 77, 109, 0.35)";

  btnSOS.innerHTML = "SOS";

}

/* EFEITO BOTÃO */
function ativarBotao() {

  btnSOS.style.transform = "scale(1.05)";

  btnSOS.style.boxShadow =
    `
    0 0 25px rgba(255,77,109,0.7),
    0 0 60px rgba(255,77,109,0.4)
    `;

  btnSOS.innerHTML = "ATIVO";

}

/* EFEITO FINAL */
function efeitoFinal() {

  btnSOS.animate(
    [
      { transform: "scale(1)" },
      { transform: "scale(1.05)" },
      { transform: "scale(1)" }
    ],
    {
      duration: 1200,
      iterations: Infinity
    }
  );

}

/* GEOLOCALIZAÇÃO REAL */
if (navigator.geolocation) {

  navigator.geolocation.getCurrentPosition(
    (posicao) => {

      const latitude = posicao.coords.latitude;
      const longitude = posicao.coords.longitude;

      console.log("Latitude:", latitude);
      console.log("Longitude:", longitude);

    },

    (erro) => {
      console.log("Localização negada.");
    }

  );

}