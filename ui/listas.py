"""Minhas listas (H8/H9, DESIGN.md 5.3). A watchlist entra na Sprint 3."""

import streamlit as st

from models.filme import Filme
from servicos.favoritos_servico import listar_favoritos, remover_favorito
from ui.componentes import botao_buscar_filmes, cartao_filme
from ui.identidade import cabecalho, estado_vazio, rodape, titulo_pagina


def renderizar() -> None:
    cabecalho(compacto=True)
    titulo_pagina("Minhas listas", "Filmes salvos para consultar depois")

    usuario_id = st.session_state["usuario_id"][0]
    filmes = listar_favoritos(usuario_id)

    if not filmes:
        with st.container(border=True):
            estado_vazio(
                "favorite_border",
                "Sua lista está vazia",
                "Busque um título e favorite-o para encontrá-lo aqui depois.",
            )
            botao_buscar_filmes("listas_buscar_filmes")
    else:
        quantidade = len(filmes)
        sufixo = "s" if quantidade > 1 else ""
        st.caption(f"Favoritos · {quantidade} filme{sufixo}")

        for filme in filmes:
            cartao_filme(filme, "listas", acoes=lambda f=filme: _botao_remover(usuario_id, f))

    # TODO (Sprint 3, H4.3): lista da watchlist.
    rodape()


def _botao_remover(usuario_id: int, filme: Filme) -> None:
    if st.button(
        "Remover",
        key=f"lista_remover_fav_{filme.id}",
        icon=":material/delete:",
        type="tertiary",
        help="Remover dos favoritos",
    ):
        remover_favorito(usuario_id, filme.id)
        st.rerun()
