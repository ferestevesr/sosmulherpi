document.addEventListener("DOMContentLoaded", function () {

    /* =========================================================
       CONFIGURAÇÃO VINDO DO SOS.HTML
    ========================================================= */

    const sosConfigElemento = document.getElementById("sosConfig");

    const SOS_CONFIG = {
        autenticado:
            sosConfigElemento &&
            sosConfigElemento.dataset.autenticado === "1",

        criarUrl:
            sosConfigElemento
                ? sosConfigElemento.dataset.criarUrl
                : "",

        cancelarUrl:
            sosConfigElemento
                ? sosConfigElemento.dataset.cancelarUrl
                : "",

        statusUrl:
            sosConfigElemento
                ? sosConfigElemento.dataset.statusUrl
                : ""
    };


    /* =========================================================
       ELEMENTOS
    ========================================================= */

    const btnSOS = document.getElementById("btnSOS");
    const btnCancelar = document.getElementById("btnCancelar");

    const barra = document.getElementById("barra");
    const status = document.getElementById("status");

    const statusBadge = document.getElementById("statusBadge");

    const loc = document.getElementById("loc");
    const contatos = document.getElementById("contatos");
    const ajuda = document.getElementById("ajuda");
    const geral = document.getElementById("geral");

    const gpsStatus = document.getElementById("gpsStatus");

    const mapa = document.getElementById("mapa");
    const mapaPlaceholder = document.getElementById("mapaPlaceholder");

    const coordenadas = document.getElementById("coordenadas");

    const latitudeTexto = document.getElementById("latitude");
    const longitudeTexto = document.getElementById("longitude");


    /* =========================================================
       VARIÁVEIS
    ========================================================= */

    let alertaAtivo = false;

    let watchId = null;

    let pedidoSosId = null;

    let pedidoRegistrado = false;


    /* =========================================================
       EVENTO BOTÃO SOS
    ========================================================= */

    btnSOS.addEventListener("click", function () {

        if (alertaAtivo) {
            return;
        }

        iniciarAlerta();

    });


    /* =========================================================
       EVENTO CANCELAR
    ========================================================= */

    btnCancelar.addEventListener("click", function () {

        cancelarAlerta();

    });


    /* =========================================================
       INICIAR ALERTA
    ========================================================= */

    function iniciarAlerta() {

        alertaAtivo = true;

        pedidoRegistrado = false;

        pedidoSosId = null;


        /* BOTÃO */

        btnSOS.disabled = true;

        btnSOS.style.opacity = "0.85";

        btnSOS.querySelector("span").textContent =
            "LOCALIZANDO";


        /* BARRA */

        barra.style.width = "20%";


        /* STATUS */

        status.textContent =
            "Solicitando acesso à sua localização...";

        statusBadge.textContent =
            "Iniciando";

        loc.textContent =
            "Solicitando";

        ajuda.textContent =
            "Iniciando";

        geral.textContent =
            "Ativo";

        gpsStatus.textContent =
            "Solicitando acesso";


        /* VERIFICA GEOLOCALIZAÇÃO */

        if (!navigator.geolocation) {

            erroGeolocalizacao(
                "Seu navegador não oferece suporte à localização."
            );

            return;

        }


        /* ACOMPANHA LOCALIZAÇÃO */

        watchId = navigator.geolocation.watchPosition(

            localizacaoObtida,

            localizacaoErro,

            {
                enableHighAccuracy: true,
                timeout: 15000,
                maximumAge: 5000
            }

        );

    }


    /* =========================================================
       LOCALIZAÇÃO OBTIDA
    ========================================================= */

    async function localizacaoObtida(position) {

        if (!alertaAtivo) {
            return;
        }


        const latitude =
            position.coords.latitude;

        const longitude =
            position.coords.longitude;


        /* COORDENADAS */

        latitudeTexto.textContent =
            latitude.toFixed(6);

        longitudeTexto.textContent =
            longitude.toFixed(6);

        coordenadas.hidden = false;


        /* STATUS GPS */

        loc.textContent =
            "Obtida";

        gpsStatus.textContent =
            "GPS ativo";

        geral.textContent =
            "Ativo";


        /* MAPA */

        atualizarMapa(
            latitude,
            longitude
        );


        /*
           watchPosition pode chamar essa função várias vezes.
           O pedido SOS só deve ser criado uma vez.
        */

        if (!pedidoRegistrado) {

            pedidoRegistrado = true;

            await registrarPedidoSOS(
                latitude,
                longitude
            );

        }

    }


    /* =========================================================
       REGISTRAR SOS NO FLASK
    ========================================================= */

    async function registrarPedidoSOS(latitude, longitude) {

        barra.style.width = "55%";


        /* USUÁRIO NÃO LOGADO */

        if (!SOS_CONFIG.autenticado) {

            status.textContent =
                "Localização obtida. Entre na sua conta para registrar o alerta.";

            statusBadge.textContent =
                "Login necessário";

            ajuda.textContent =
                "Não registrado";

            geral.textContent =
                "Localização ativa";

            barra.style.width =
                "100%";

            btnSOS.querySelector("span").textContent =
                "LOCALIZAÇÃO ATIVA";

            return;

        }


        /* USUÁRIO LOGADO */

        status.textContent =
            "Localização obtida. Registrando alerta...";

        statusBadge.textContent =
            "Registrando";


        try {

            const resposta = await fetch(
                SOS_CONFIG.criarUrl,
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


            const dados =
                await resposta.json();


            if (!resposta.ok || !dados.sucesso) {

                throw new Error(
                    dados.mensagem ||
                    "Não foi possível registrar o alerta."
                );

            }


            /* SALVA ID DO PEDIDO */

            pedidoSosId =
                dados.id_sos;


            /* INTERFACE */

            barra.style.width =
                "100%";

            status.textContent =
                "Alerta registrado com sucesso.";

            statusBadge.textContent =
                "Ativo";

            ajuda.textContent =
                "Registrado";

            geral.textContent =
                "Ativo";


            /* QUANTIDADE DE CONTATOS */

            if (contatos) {

                if (dados.contatos === 1) {

                    contatos.textContent =
                        "1 vinculado";

                } else {

                    contatos.textContent =
                        dados.contatos + " vinculados";

                }

            }


            btnSOS.querySelector("span").textContent =
                "ALERTA ATIVO";

            acompanharStatus();


        } catch (erro) {

            console.error(
                "Erro ao registrar SOS:",
                erro
            );


            status.textContent =
                "Localização obtida, mas o alerta não pôde ser registrado.";

            statusBadge.textContent =
                "Erro no registro";

            ajuda.textContent =
                "Não registrado";

            geral.textContent =
                "Disponível";


            btnSOS.disabled =
                false;

            btnSOS.style.opacity =
                "1";

            btnSOS.querySelector("span").textContent =
                "TENTAR NOVAMENTE";


            pedidoRegistrado =
                false;

            alertaAtivo =
                false;


            pararLocalizacao();

        }

    }

    async function acompanharStatus() {
        if (!pedidoSosId || !SOS_CONFIG.statusUrl) {
            return;
        }

        try {
            const resposta = await fetch(
                SOS_CONFIG.statusUrl.replace(/0$/, pedidoSosId)
            );
            const dados = await resposta.json();

            if (resposta.ok && dados.sucesso) {
                const texto = dados.status.replace("_", " ");
                statusBadge.textContent = texto;
                ajuda.textContent = texto;

                if (dados.status === "finalizado" || dados.status === "cancelado") {
                    pararLocalizacao();
                } else {
                    window.setTimeout(acompanharStatus, 30000);
                }
            }
        } catch (erro) {
            console.error("Não foi possível atualizar o status do SOS:", erro);
        }
    }


    /* =========================================================
       ATUALIZAR MAPA
    ========================================================= */

    function atualizarMapa(latitude, longitude) {

        const url =
            "https://www.google.com/maps?q=" +
            latitude +
            "," +
            longitude +
            "&z=16&output=embed";


        mapa.src =
            url;

        mapa.hidden =
            false;

        mapaPlaceholder.hidden =
            true;

    }


    /* =========================================================
       ERRO DE LOCALIZAÇÃO
    ========================================================= */

    function localizacaoErro(error) {

        let mensagem;


        switch (error.code) {

            case error.PERMISSION_DENIED:

                mensagem =
                    "A permissão de localização foi negada.";

                break;


            case error.POSITION_UNAVAILABLE:

                mensagem =
                    "Não foi possível identificar sua localização.";

                break;


            case error.TIMEOUT:

                mensagem =
                    "A localização demorou mais que o esperado.";

                break;


            default:

                mensagem =
                    "Não foi possível acessar sua localização.";

        }


        erroGeolocalizacao(
            mensagem
        );

    }


    /* =========================================================
       TRATAR ERRO DE GEOLOCALIZAÇÃO
    ========================================================= */

    function erroGeolocalizacao(mensagem) {

        barra.style.width =
            "0%";

        status.textContent =
            mensagem;

        statusBadge.textContent =
            "Sem localização";

        loc.textContent =
            "Indisponível";

        gpsStatus.textContent =
            "GPS indisponível";

        ajuda.textContent =
            "Não iniciado";

        geral.textContent =
            "Disponível";


        btnSOS.disabled =
            false;

        btnSOS.style.opacity =
            "1";

        btnSOS.querySelector("span").textContent =
            "TENTAR NOVAMENTE";


        pararLocalizacao();

        alertaAtivo =
            false;

    }


    /* =========================================================
       CANCELAR ALERTA
    ========================================================= */

    async function cancelarAlerta() {

        /*
           Se existe um PedidoSOS registrado no banco,
           atualiza o status para cancelado.
        */

        if (
            pedidoSosId !== null &&
            SOS_CONFIG.autenticado &&
            SOS_CONFIG.cancelarUrl
        ) {

            status.textContent =
                "Cancelando alerta...";

            statusBadge.textContent =
                "Cancelando";


            try {

                const resposta = await fetch(
                    SOS_CONFIG.cancelarUrl,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type": "application/json"
                        },

                        body: JSON.stringify({
                            id_sos: pedidoSosId
                        })
                    }
                );


                const dados =
                    await resposta.json();


                if (!resposta.ok || !dados.sucesso) {

                    console.error(
                        "Erro ao cancelar pedido:",
                        dados
                    );

                }


            } catch (erro) {

                console.error(
                    "Erro ao cancelar SOS:",
                    erro
                );

            }

        }


        resetarInterface();

    }


    /* =========================================================
       RESETAR INTERFACE
    ========================================================= */

    function resetarInterface() {

        pararLocalizacao();


        alertaAtivo =
            false;

        pedidoRegistrado =
            false;

        pedidoSosId =
            null;


        /* BOTÃO */

        btnSOS.disabled =
            false;

        btnSOS.style.opacity =
            "1";

        btnSOS.querySelector("span").textContent =
            "ACIONAR ALERTA";


        /* BARRA */

        barra.style.width =
            "0%";


        /* STATUS */

        status.textContent =
            "Pressione SOS para iniciar.";

        statusBadge.textContent =
            "Aguardando";

        loc.textContent =
            "Aguardando";

        ajuda.textContent =
            "Não iniciado";

        geral.textContent =
            "Disponível";

        gpsStatus.textContent =
            "Não iniciado";


        /* MAPA */

        mapa.src =
            "";

        mapa.hidden =
            true;

        mapaPlaceholder.hidden =
            false;


        /* COORDENADAS */

        coordenadas.hidden =
            true;

        latitudeTexto.textContent =
            "-";

        longitudeTexto.textContent =
            "-";

    }


    /* =========================================================
       PARAR GPS
    ========================================================= */

    function pararLocalizacao() {

        if (watchId !== null) {

            navigator.geolocation.clearWatch(
                watchId
            );

            watchId =
                null;

        }

    }


    /* =========================================================
       ENCERRAR GPS AO SAIR DA PÁGINA
    ========================================================= */

    window.addEventListener(
        "beforeunload",
        function () {

            pararLocalizacao();

        }
    );

});
