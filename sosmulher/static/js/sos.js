const btnSOS = document.getElementById("btnSOS");
const barra = document.getElementById("barra");
const statusTexto = document.getElementById("status");

const loc = document.getElementById("loc");
const contatos = document.getElementById("contatos");
const ajuda = document.getElementById("ajuda");
const geral = document.getElementById("geral");

const cancelar = document.querySelector(".cancelar");

let sistemaAtivo = false;
let localizacaoObtida = false;
let latitudeAtual = null;
let longitudeAtual = null;


/* ==========================================
   ESTADO INICIAL
========================================== */

resetarSistema();


/* ==========================================
   BOTÃO SOS
========================================== */

btnSOS.addEventListener("click", () => {

    console.log("BOTÃO SOS FOI CLICADO!");

    if (sistemaAtivo) {
        return;
    }

    sistemaAtivo = true;

    ativarBotao();

    statusTexto.innerHTML =
        "Solicitando sua localização...";

    geral.innerHTML = "🟡 Localizando";

    loc.innerHTML = "🟡 Detectando localização";


    /* ==========================================
       VERIFICA SE O NAVEGADOR POSSUI GEOLOCALIZAÇÃO
    ========================================== */

    if (!navigator.geolocation) {

        console.error(
            "Este navegador não suporta geolocalização."
        );

        localizacaoFalhou(
            "Seu navegador não suporta localização."
        );

        return;
    }


    /* ==========================================
       SOLICITA A LOCALIZAÇÃO
    ========================================== */

    navigator.geolocation.getCurrentPosition(

        (posicao) => {

            latitudeAtual = posicao.coords.latitude;
            longitudeAtual = posicao.coords.longitude;

            localizacaoObtida = true;

            console.log("=================================");
            console.log("LOCALIZAÇÃO OBTIDA COM SUCESSO!");
            console.log("Latitude:", latitudeAtual);
            console.log("Longitude:", longitudeAtual);
            console.log("Precisão:", posicao.coords.accuracy);
            console.log("=================================");


            /* Atualiza interface */

            barra.style.width = "20%";

            loc.innerHTML = "🟢 Localização detectada";

            statusTexto.innerHTML =
                "Localização obtida. Registrando emergência...";

            geral.innerHTML = "🟢 Localização obtida";


            /* ==========================================
               ENVIA O SOS PARA O FLASK
            ========================================== */

            registrarSOS(
                latitudeAtual,
                longitudeAtual
            );

        },


        (erro) => {

            console.error("=================================");
            console.error("ERRO DE GEOLOCALIZAÇÃO");
            console.error("Código:", erro.code);
            console.error("Mensagem:", erro.message);
            console.error("=================================");


            if (erro.code === 1) {

                console.error(
                    "PERMISSÃO NEGADA: o navegador não permitiu acesso à localização."
                );

                localizacaoFalhou(
                    "Permissão de localização negada."
                );

            } else if (erro.code === 2) {

                console.error(
                    "LOCALIZAÇÃO INDISPONÍVEL: não foi possível determinar sua posição."
                );

                localizacaoFalhou(
                    "Não foi possível determinar sua localização."
                );

            } else if (erro.code === 3) {

                console.error(
                    "TEMPO ESGOTADO: a localização demorou demais para ser obtida."
                );

                localizacaoFalhou(
                    "Não foi possível obter sua localização a tempo."
                );

            } else {

                localizacaoFalhou(
                    "Não foi possível obter sua localização."
                );

            }

        },


        {
            enableHighAccuracy: true,
            timeout: 30000,
            maximumAge: 60000
        }

    );

});


/* ==========================================
   QUANDO A LOCALIZAÇÃO FALHA
========================================== */

function localizacaoFalhou(mensagem) {

    localizacaoObtida = false;

    latitudeAtual = null;
    longitudeAtual = null;

    barra.style.width = "0%";

    loc.innerHTML = "🔴 Indisponível";

    contatos.innerHTML = "Aguardando";

    ajuda.innerHTML = "Aguardando";

    geral.innerHTML = "🔴 Erro";

    statusTexto.innerHTML =
        mensagem +
        " O pedido SOS não foi enviado.";

    sistemaAtivo = false;

    btnSOS.style.transform = "scale(1)";

    btnSOS.style.boxShadow =
        "0 25px 60px rgba(255, 77, 109, 0.35)";

    btnSOS.innerHTML = "SOS";

}


/* ==========================================
   REGISTRAR SOS NO SERVIDOR
========================================== */

async function registrarSOS(latitude, longitude) {

    if (
        latitude === null ||
        longitude === null ||
        latitude === undefined ||
        longitude === undefined
    ) {

        console.error(
            "SOS não enviado: localização inválida."
        );

        localizacaoFalhou(
            "Localização inválida."
        );

        return;
    }


    console.log("Enviando SOS para o servidor...");

    statusTexto.innerHTML =
        "Registrando pedido de emergência...";

    geral.innerHTML = "🟡 Registrando";


    try {

        const resposta = await fetch("/sos/acionar", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                latitude: latitude,
                longitude: longitude
            })

        });


        /* ==========================================
           TENTA LER A RESPOSTA
        ========================================== */

        let dados;

        try {

            dados = await resposta.json();

        } catch (erroJSON) {

            console.error(
                "O servidor não retornou JSON válido."
            );

            console.error(
                "Status HTTP:",
                resposta.status
            );

            throw new Error(
                "Resposta inválida do servidor."
            );

        }


        /* ==========================================
           ERRO RETORNADO PELO FLASK
        ========================================== */

        if (!resposta.ok || !dados.sucesso) {

            console.error(
                "Erro retornado pelo servidor:",
                dados.erro
            );

            throw new Error(
                dados.erro ||
                "Não foi possível registrar o SOS."
            );

        }


        /* ==========================================
           SOS REGISTRADO COM SUCESSO
        ========================================== */

        console.log(
            "SOS registrado com sucesso!"
        );

        console.log(
            "ID do SOS:",
            dados.id_sos
        );

        console.log(
            "Contatos:",
            dados.contatos
        );


        barra.style.width = "45%";

        statusTexto.innerHTML =
            "Pedido de emergência registrado.";


        /* CONTATOS */

        if (dados.contatos > 0) {

            contatos.innerHTML =
                "🟢 " +
                dados.contatos +
                " contatos avisados";

        } else {

            contatos.innerHTML =
                "🟡 Nenhum contato cadastrado";

        }


        /* ==========================================
           ETAPA DE AJUDA
        ========================================== */

        setTimeout(() => {

            barra.style.width = "70%";

            statusTexto.innerHTML =
                "Contatos de emergência processados.";

            ajuda.innerHTML =
                "🟡 Equipe analisando situação";

        }, 1500);


        /* ==========================================
           FINALIZAÇÃO
        ========================================== */

        setTimeout(() => {

            barra.style.width = "100%";

            statusTexto.innerHTML =
                "Ajuda acionada com sucesso 🚨";

            ajuda.innerHTML =
                "🟢 Ajuda a caminho";

            geral.innerHTML =
                "🟢 Emergência ativa";

            efeitoFinal();

        }, 3000);


    } catch (erro) {

        console.error(
            "Erro ao registrar SOS:",
            erro
        );

        statusTexto.innerHTML =
            "Erro ao registrar o pedido de emergência.";

        geral.innerHTML =
            "🔴 Erro";

        ajuda.innerHTML =
            "🔴 Não registrado";

        sistemaAtivo = false;

        btnSOS.style.transform = "scale(1)";

        btnSOS.style.boxShadow =
            "0 25px 60px rgba(255, 77, 109, 0.35)";

        btnSOS.innerHTML = "SOS";

    }

}


/* ==========================================
   CANCELAR
========================================== */

cancelar.addEventListener("click", () => {

    console.log("SOS cancelado.");

    sistemaAtivo = false;

    localizacaoObtida = false;

    latitudeAtual = null;
    longitudeAtual = null;

    resetarSistema();

});


/* ==========================================
   RESET
========================================== */

function resetarSistema() {

    barra.style.width = "0%";

    statusTexto.innerHTML =
        "Pressione o botão para iniciar o pedido de ajuda.";

    loc.innerHTML = "Aguardando";

    contatos.innerHTML = "Aguardando";

    ajuda.innerHTML = "Aguardando";

    geral.innerHTML = "Inativo";


    btnSOS.style.transform =
        "scale(1)";

    btnSOS.style.boxShadow =
        "0 25px 60px rgba(255, 77, 109, 0.35)";

    btnSOS.innerHTML =
        "SOS";

}


/* ==========================================
   EFEITO BOTÃO ATIVO
========================================== */

function ativarBotao() {

    btnSOS.style.transform =
        "scale(1.05)";

    btnSOS.style.boxShadow =
        `
        0 0 25px rgba(255,77,109,0.7),
        0 0 60px rgba(255,77,109,0.4)
        `;

    btnSOS.innerHTML =
        "ATIVO";

}


/* ==========================================
   EFEITO FINAL
========================================== */

function efeitoFinal() {

    btnSOS.animate(

        [
            {
                transform: "scale(1)"
            },

            {
                transform: "scale(1.05)"
            },

            {
                transform: "scale(1)"
            }
        ],

        {
            duration: 1200,
            iterations: Infinity
        }

    );

}
