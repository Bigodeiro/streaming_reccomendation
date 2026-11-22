"""Peças de tela reaproveitadas por mais de uma página (DESIGN.md, seção 4)."""

from collections.abc import Callable
from html import escape

import streamlit as st

from models.filme import Filme
from servicos.busca_servico import onde_assistir
from ui.identidade import chips_generos, chips_streamings


def cartao_filme(filme: Filme, contexto: str, acoes: Callable[[], None] | None = None) -> None:
    """Card de um filme (4.3): título, gêneros, onde assistir e, à direita, os botões de `acoes`.

    `contexto` (ex.: "busca", "listas") só serve para deixar a chave do card única.
    No celular o Streamlit empilha as colunas, então o botão desce para baixo do conteúdo.
    """
    with st.container(border=True, key=f"qs-card-{contexto}-{filme.id}"):
        info, coluna_acoes = st.columns([4, 1.5], vertical_alignment="center")

        with info:
            ano = f' <span class="qs-filme-ano">({filme.ano})</span>' if filme.ano else ""
            partes = [f'<p class="qs-filme-titulo">{escape(filme.titulo)}{ano}</p>']

            if filme.generos:
                partes.append(
                    f'<div class="qs-chips" style="margin-top:0.5rem">{chips_generos(filme.generos)}</div>'
                )

            streamings = onde_assistir(filme.id)
            partes.append('<div class="qs-rotulo">Onde assistir</div>')
            if streamings:
                partes.append(f'<div class="qs-chips">{chips_streamings(streamings)}</div>')
            else:
                partes.append('<span class="qs-meta">Disponibilidade não informada</span>')

            st.html("".join(partes))

        if acoes:
            with coluna_acoes:
                acoes()


def botao_buscar_filmes(chave: str) -> None:
    """Ação dos estados vazios (4.5): leva para a página de busca."""
    _, meio, _ = st.columns([1, 1, 1])
    if meio.button("Buscar filmes", key=chave, icon=":material/search:", type="primary", width="stretch"):
        from ui.navegacao import PAGINA_BUSCA  # import tardio: navegacao importa as telas

        st.switch_page(PAGINA_BUSCA)


def formatar_preco(valor: float) -> str:
    """15.9 -> 'R$ 15,90'."""
    texto = f"{valor:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {texto}"


def formatar_afinidade(afinidade: float) -> str:
    """0.756 -> '76%'."""
    return f"{round(afinidade * 100)}%"
