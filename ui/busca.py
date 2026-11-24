"""Home do app: busca de filmes no estilo de site de buscas (H2.3 / H6, DESIGN.md 5.1).

Sem nada digitado, mostra a marca grande, a barra de busca (com exemplos no
placeholder) e "Como funciona". Com uma busca, a marca encolhe e os resultados aparecem.
"""

from html import escape

import streamlit as st

from models.filme import Filme
from servicos.busca_servico import buscar_filmes
from servicos.favoritos_servico import eh_favorito, marcar_favorito, remover_favorito
from ui.componentes import cartao_filme
from ui.identidade import cabecalho, rodape

CHAVE_BUSCA = "termo_busca"
# Os exemplos do placeholder existem no catálogo (DESIGN.md: não inventar catálogo).
PLACEHOLDER = "Busque um filme, ex.: The Dark Knight"

PASSOS = [
    ("Busque", "Encontre os filmes que você já viu ou quer ver."),
    ("Favorite", "Marque os títulos de que você gostou."),
    ("Descubra", "Compare os serviços e planos que combinam com você."),
]


def renderizar() -> None:
    termo = st.session_state.get(CHAVE_BUSCA, "").strip()

    cabecalho(compacto=bool(termo))

    with st.container(key="qs-search"):
        st.text_input(
            "Buscar filme",
            key=CHAVE_BUSCA,
            placeholder=PLACEHOLDER,
            label_visibility="collapsed",
            icon=":material/search:",
        )

    if termo:
        _resultados(termo)
    else:
        _como_funciona()

    rodape()


def _como_funciona() -> None:
    st.html('<div class="qs-section"><h2 class="qs-section-title" style="text-align:center">Como funciona</h2></div>')
    for coluna, (indice, (titulo, texto)) in zip(st.columns(len(PASSOS)), enumerate(PASSOS, 1)):
        with coluna:
            st.html(
                f'<div class="qs-passo"><span class="qs-passo-num">{indice}</span>'
                f'<p class="qs-passo-titulo">{escape(titulo)}</p><p>{escape(texto)}</p></div>'
            )


def _resultados(termo: str) -> None:
    resultados = buscar_filmes(termo)

    if not resultados:
        st.info(
            f'Não encontramos filmes para "{termo}". Tente outro nome.',
            icon=":material/search_off:",
        )
        return

    quantidade = len(resultados)
    plural = "s" if quantidade > 1 else ""
    st.html(
        f'<p class="qs-results-caption">Resultados para “{escape(termo)}” · '
        f"{quantidade} filme{plural}</p>"
    )

    for filme in resultados:
        cartao_filme(filme, "busca", acoes=lambda f=filme: _botao_favorito(f))


def _botao_favorito(filme: Filme) -> None:
    usuario_id = st.session_state["usuario_id"][0]
    if eh_favorito(usuario_id, filme.id):
        if st.button(
            "Favorito",
            key=f"busca_remover_fav_{filme.id}",
            icon=":material/favorite:",
            help="Clique para remover dos favoritos",
        ):
            remover_favorito(usuario_id, filme.id)
            st.rerun()
    elif st.button(
        "Favoritar",
        key=f"busca_favoritar_{filme.id}",
        icon=":material/favorite_border:",
        type="primary",
    ):
        marcar_favorito(usuario_id, filme.id)
        st.rerun()

    # TODO (Sprint 3, H4.2): botão "Quero ver" (watchlist).
