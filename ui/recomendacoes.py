"""Tela de recomendações com planos e preços (H3.5 / H7, DESIGN.md 4.7, 4.8 e 5.4).

A tela só exibe o ranking que a lógica da H3.4 devolve (lista de StreamingRecomendado
já ordenada) e os planos de cada streaming. Não recalcula nada.
"""

from html import escape

import streamlit as st

from models.contexto_recomendacao import StreamingRecomendado
from models.plano import Plano
from servicos.favoritos_servico import listar_favoritos

# TODO (integração H3.3/H3.1): trocar pela versão definitiva e pôr PLANOS_DE_EXEMPLO = False.
from servicos.recomendacao_provisoria import planos_do_streaming, recomendar
from ui.componentes import botao_buscar_filmes, formatar_pontuacao, formatar_preco
from ui.identidade import cabecalho, estado_vazio, rodape, titulo_pagina

PLANOS_DE_EXEMPLO = True
CHAVE_RESULTADO = "recomendacao"
MAX_FILMES_SUGERIDOS = 5


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

    if PLANOS_DE_EXEMPLO:
        st.warning(
            "Os planos e preços abaixo são fictícios. Os valores reais chegam com a H3.1.",
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
            "Não encontramos filmes parecidos com seus favoritos nos serviços cadastrados. "
            "Favorite filmes de outros gêneros e tente de novo.",
            icon=":material/search_off:",
        )
        return

    st.html(
        '<p class="qs-results-caption">Ordenados pela pontuação de afinidade: cada filme que você '
        "ainda não favoritou soma pontos quando tem gêneros dos seus favoritos.</p>"
    )
    for posicao, item in enumerate(recomendados, 1):
        with st.container(border=True, key=f"qs-card-rank-{posicao}"):
            st.html(_html_item(posicao, item, planos_do_streaming(item.nome)))


def _html_item(posicao: int, item: StreamingRecomendado, planos: list[Plano]) -> str:
    partes = [
        '<div class="qs-rank"><div class="qs-rank-head">',
        f'<span class="qs-rank-pos" aria-label="Posição {posicao}">{posicao}º</span>',
        f'<span class="qs-rank-nome">{escape(item.nome)}</span>',
        f'<span class="qs-afinidade"><strong>{formatar_pontuacao(item.pontuacao)}</strong>'
        "<span>pontos de afinidade</span></span>",
        "</div>",
    ]

    if item.generos_principais:
        generos = ", ".join(escape(g) for g in item.generos_principais)
        partes.append(f'<p class="qs-rank-favs">Combina com: {generos}</p>')

    if item.filmes_compativeis:
        sugeridos = [escape(t) for t in item.filmes_compativeis[:MAX_FILMES_SUGERIDOS]]
        restantes = len(item.filmes_compativeis) - len(sugeridos)
        extra = f" e mais {restantes}" if restantes > 0 else ""
        partes.append(f'<p class="qs-rank-favs">Você pode gostar: {", ".join(sugeridos)}{extra}</p>')

    partes.append('<div class="qs-rotulo">Planos</div>')
    partes.append(_html_planos(planos))
    partes.append("</div>")
    return "".join(partes)


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
