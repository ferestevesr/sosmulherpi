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
let idSOS = null;


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

    geral.innerHTML =
        "🟡 Localizando";

    loc.innerHTML =
        "🟡 Detectando localização";


    /* ==========================================
       VERIFICA GEOLOCALIZAÇÃO
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
       OBTÉM LOCALIZAÇÃO
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


            barra.style.width = "20%";

            loc.innerHTML =
                "🟢 Localização detectada";

            statusTexto.innerHTML =
                "Localização obtida. Enviando pedido de emergência...";

            geral.innerHTML =
                "🟡 Enviando";


            /* ==========================================
               REGISTRA O SOS NO BANCO
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

                localizacaoFalhou(
                    "Permissão de localização negada."
                );

            } else if (erro.code === 2) {

                localizacaoFalhou(
                    "Não foi possível determinar sua localização."
                );

            } else if (erro.code === 3) {

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
   LOCALIZAÇÃO FALHOU
========================================== */

function localizacaoFalhou(mensagem) {

    localizacaoObtida = false;

    latitudeAtual = null;
    longitudeAtual = null;

    barra.style.width = "0%";

    loc.innerHTML =
        "🔴 Indisponível";

    contatos.innerHTML =
        "Aguardando";

    ajuda.innerHTML =
        "Aguardando";

    geral.innerHTML =
        "🔴 Erro";

    statusTexto.innerHTML =
        mensagem +
        " O pedido SOS não foi enviado.";

    sistemaAtivo = false;

    btnSOS.style.transform =
        "scale(1)";

    btnSOS.style.boxShadow =
        "0 25px 60px rgba(255, 77, 109, 0.35)";

    btnSOS.innerHTML =
        "SOS";
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


    console.log(
        "Enviando SOS para o servidor..."
    );


    statusTexto.innerHTML =
        "Registrando pedido de emergência...";

    geral.innerHTML =
        "🟡 Registrando";


    try {

        const resposta = await fetch(
            "/sos/acionar",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    latitude: latitude,
                    longitude: longitude
                })
            }
        );


        /* ==========================================
           LÊ RESPOSTA
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
           VERIFICA ERRO
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
           SOS REGISTRADO
        ========================================== */

        idSOS = dados.id_sos;

        console.log(
            "SOS registrado com sucesso!"
        );

        console.log(
            "ID do SOS:",
            idSOS
        );

        console.log(
            "Status:",
            dados.status
        );

        console.log(
            "Contatos vinculados:",
            dados.contatos
        );


        barra.style.width =
            "45%";


        statusTexto.innerHTML =
            "Pedido de emergência enviado. Aguardando acionamento dos contatos.";


        /* ==========================================
           LOCALIZAÇÃO
        ========================================== */

        loc.innerHTML =
            "🟢 Localização enviada";


        /* ==========================================
           CONTATOS
           IMPORTANTE:
           ainda NÃO foram avisados.
        ========================================== */

        if (dados.contatos > 0) {

            contatos.innerHTML =
                "🟡 Aguardando acionamento";

        } else {

            contatos.innerHTML =
                "🟡 Nenhum contato cadastrado";

        }


        /* ==========================================
           AJUDA
        ========================================== */

        ajuda.innerHTML =
            "🟡 Aguardando";


        /* ==========================================
           SISTEMA
        ========================================== */

        geral.innerHTML =
            "🟢 Chamado enviado";


        barra.style.width =
            "60%";


        /*
         * A partir daqui NÃO finalizamos
         * automaticamente o chamado.
         *
         * O status só mudará quando o
         * administrador acionar os contatos.
         */


        console.log(
            "Chamado aguardando ação do administrador."
        );


        /*
         * Começa a consultar o status do chamado.
         */

        iniciarMonitoramentoStatus();


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

        contatos.innerHTML =
            "🔴 Não registrado";

        sistemaAtivo = false;

        btnSOS.style.transform =
            "scale(1)";

        btnSOS.style.boxShadow =
            "0 25px 60px rgba(255, 77, 109, 0.35)";

        btnSOS.innerHTML =
            "SOS";
    }

}


/* ==========================================
   MONITORAMENTO DO STATUS
========================================== */

function iniciarMonitoramentoStatus() {

    if (!idSOS) {
        return;
    }

    console.log(
        "Iniciando monitoramento do SOS:",
        idSOS
    );


    /*
     * Consulta o servidor a cada 5 segundos.
     *
     * Enquanto estiver em andamento:
     * - contatos aguardando
     * - ajuda aguardando
     *
     * Quando o admin acionar:
     * - chamado finalizado
     * - contatos acionados
     * - ajuda a caminho
     */

    const intervalo = setInterval(
        async () => {

            try {

                const resposta = await fetch(
                    `/sos/status/${idSOS}`
                );


                if (!resposta.ok) {
                    return;
                }


                const dados =
                    await resposta.json();


                if (!dados.sucesso) {
                    return;
                }


                console.log(
                    "Status atual do SOS:",
                    dados.status
                );


                atualizarStatusInterface(
                    dados
                );


                /*
                 * Quando finalizar, não precisa
                 * continuar consultando.
                 */

                if (
                    dados.status === "finalizado" ||
                    dados.status === "cancelado"
                ) {

                    clearInterval(intervalo);
                }


            } catch (erro) {

                console.error(
                    "Erro ao consultar status do SOS:",
                    erro
                );

            }

        },
        5000
    );
}


/* ==========================================
   ATUALIZA INTERFACE CONFORME BANCO
========================================== */

function atualizarStatusInterface(dados) {

    /* ==========================================
       EM ANDAMENTO
    ========================================== */

    if (dados.status === "em_andamento") {

        barra.style.width =
            "60%";

        statusTexto.innerHTML =
            "Pedido registrado. Aguardando acionamento dos contatos de emergência.";

        contatos.innerHTML =
            dados.contatos > 0
                ? "🟡 Aguardando acionamento"
                : "🟡 Nenhum contato cadastrado";

        ajuda.innerHTML =
            "🟡 Aguardando";

        geral.innerHTML =
            "🟢 Chamado em andamento";

        return;
    }


    /* ==========================================
       FINALIZADO
    ========================================== */

    if (dados.status === "finalizado") {

        barra.style.width =
            "100%";

        statusTexto.innerHTML =
            "Ajuda acionada e a caminho 🚨";

        contatos.innerHTML =
            dados.contatos > 0
                ? "🟢 Contatos acionados"
                : "🟡 Nenhum contato cadastrado";

        ajuda.innerHTML =
            "🟢 Ajuda acionada e a caminho";

        geral.innerHTML =
            "🟢 Emergência acionada";

        efeitoFinal();

        return;
    }


    /* ==========================================
       CANCELADO
    ========================================== */

    if (dados.status === "cancelado") {

        barra.style.width =
            "0%";

        statusTexto.innerHTML =
            "O pedido de emergência foi cancelado.";

        contatos.innerHTML =
            "Cancelado";

        ajuda.innerHTML =
            "Cancelada";

        geral.innerHTML =
            "Cancelado";

    }

}


/* ==========================================
   CANCELAR
========================================== */

cancelar.addEventListener(
    "click",
    () => {

        console.log(
            "SOS cancelado."
        );

        /*
         * Neste momento apenas limpamos
         * a interface.
         *
         * O cancelamento no banco será
         * implementado separadamente para
         * não misturar as duas funções.
         */

        sistemaAtivo = false;

        localizacaoObtida = false;

        latitudeAtual = null;
        longitudeAtual = null;

        idSOS = null;

        resetarSistema();

    }
);


/* ==========================================
   RESET
========================================== */

function resetarSistema() {

    barra.style.width =
        "0%";


    statusTexto.innerHTML =
        "Pressione o botão para iniciar o pedido de ajuda.";


    loc.innerHTML =
        "Aguardando";


    contatos.innerHTML =
        "Aguardando";


    ajuda.innerHTML =
        "Aguardando";


    geral.innerHTML =
        "Inativo";


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