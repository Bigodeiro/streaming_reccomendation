"""Tela de recomendações com planos e preços (H3.5 / H7, DESIGN.md 4.7, 4.8 e 5.4).

A tela só exibe o que o serviço devolve (lista de StreamingRecomendado já ordenada).
Enquanto a H3.3/H3.4 não chegam, usa o recomendador provisório de exemplo.
"""

from html import escape

import streamlit as st

from models.plano import Plano
from models.recomendacao import StreamingRecomendado
from servicos.favoritos_servico import listar_favoritos

# TODO (integração H3.3/H3.4): trocar pelo serviço real e pôr USANDO_DADOS_DE_EXEMPLO = False.
from servicos.recomendacao_exemplo import recomendar_exemplo as recomendar
from ui.componentes import botao_buscar_filmes, formatar_afinidade, formatar_preco
from ui.identidade import cabecalho, estado_vazio, rodape, titulo_pagina

USANDO_DADOS_DE_EXEMPLO = True
CHAVE_RESULTADO = "recomendacao"


def renderizar() -> None:
    cabecalho(compacto=True)
    titulo_pagina("Recomendações", "Compare os serviços com base nos filmes que você favoritou.")

    usuario_id = st.session_state["usuario_id"][0]
    favoritos = listar_favoritos(usuario_id)

    if not favoritos:
        st.session_state.pop(CHAVE_RESULTADO, None)
        with st.container(border=True):
            estado_vazio(
                "movie",
                "Nenhum favorito ainda",
                "Adicione alguns favoritos para descobrir quais serviços combinam com você.",
            )
            botao_buscar_filmes("recomendacoes_buscar_filmes")
        rodape()
        return

    if USANDO_DADOS_DE_EXEMPLO:
        st.warning(
            "Pré-visualização: o ranking considera só quantos dos seus favoritos estão em cada "
            "serviço, e os planos e preços são fictícios. Os dados reais chegam com a H3.1 e a H3.4.",
            icon=":material/construction:",
        )

    ids_favoritos = tuple(f.id for f in favoritos)
    salvo = st.session_state.get(CHAVE_RESULTADO)
    if salvo and salvo[0] != ids_favoritos:
        # Os favoritos mudaram desde a última recomendação: o resultado antigo não vale mais.
        st.session_state.pop(CHAVE_RESULTADO)
        salvo = None

    if st.button("Recomendar serviços", key="recomendar", icon=":material/auto_awesome:", type="primary"):
        with st.spinner("Recomendando…"):
            try:
                resultado = recomendar(usuario_id)
            except Exception:
                st.error(
                    "Não foi possível gerar recomendações agora. Seus favoritos continuam salvos.",
                    icon=":material/error:",
                )
                rodape()
                return
        st.session_state[CHAVE_RESULTADO] = (ids_favoritos, resultado)
        salvo = st.session_state[CHAVE_RESULTADO]

    if salvo:
        _mostrar_ranking(salvo[1])
    else:
        quantidade = len(favoritos)
        sufixo = "s" if quantidade > 1 else ""
        st.caption(f"A recomendação usa seus {quantidade} filme{sufixo} favorito{sufixo}.")

    rodape()


def _mostrar_ranking(recomendados: list[StreamingRecomendado]) -> None:
    if not recomendados:
        st.info(
            "Nenhum dos serviços cadastrados tem seus favoritos no catálogo. "
            "Favorite outros filmes e tente de novo.",
            icon=":material/search_off:",
        )
        return

    st.html('<p class="qs-results-caption">Ordenados pela afinidade estimada com seus favoritos.</p>')
    for posicao, item in enumerate(recomendados, 1):
        with st.container(border=True, key=f"qs-card-rank-{posicao}"):
            st.html(_html_item(posicao, item))


def _html_item(posicao: int, item: StreamingRecomendado) -> str:
    titulos = ", ".join(escape(f.titulo) for f in item.filmes_em_comum)
    favoritos = (
        f'<p class="qs-rank-favs">Seus favoritos neste serviço: {titulos}</p>' if titulos else ""
    )
    return (
        '<div class="qs-rank">'
        '<div class="qs-rank-head">'
        f'<span class="qs-rank-pos" aria-label="Posição {posicao}">{posicao}º</span>'
        f'<span class="qs-rank-nome">{escape(item.streaming)}</span>'
        f'<span class="qs-afinidade"><strong>{formatar_afinidade(item.afinidade)}</strong>'
        "<span>afinidade estimada</span></span>"
        "</div>"
        f"{favoritos}"
        '<div class="qs-rotulo">Planos</div>'
        f"{_html_planos(item.planos)}"
        "</div>"
    )


def _html_planos(planos: list[Plano]) -> str:
    if not planos:
        return '<span class="qs-meta">Planos e preços não informados.</span>'

    linhas = []
    for plano in sorted(planos, key=lambda p: p.preco_mensal):
        if plano.conferido_em:
            meta = f"conferido em {plano.conferido_em:%d/%m/%Y}"
        else:
            meta = "data de conferência não informada"
        linhas.append(
            '<li class="qs-plano">'
            f'<span class="qs-plano-nome">{escape(plano.nome)}</span>'
            f'<span class="qs-price">{formatar_preco(plano.preco_mensal)}<span class="qs-price-period">/mês</span></span>'
            f'<span class="qs-price-meta">{meta}</span>'
            "</li>"
        )
    return f'<ul class="qs-planos">{"".join(linhas)}</ul>'
