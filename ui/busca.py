import streamlit as st

from models.filme import Filme
from servicos.busca_servico import buscar_filmes, onde_assistir


def renderizar() -> None:
    st.header("Buscar filmes")

    titulo = st.text_input(
        "Título do filme",
        placeholder="Ex.: Matrix, Cidade de Deus...",
    )

    if not titulo.strip():
        st.caption("Digite parte do título para começar. Maiúsculas e acentos não importam.")
        return

    resultados = buscar_filmes(titulo)

    if not resultados:
        st.warning(f'Nenhum filme encontrado para "{titulo.strip()}".')
        return

    quantidade = len(resultados)
    st.write(f"**{quantidade}** filme{'s' if quantidade > 1 else ''} encontrado{'s' if quantidade > 1 else ''}:")

    for filme in resultados:
        _mostrar_resultado(filme)


def _mostrar_resultado(filme: Filme) -> None:
    with st.container(border=True):
        titulo = f"{filme.titulo} ({filme.ano})" if filme.ano else filme.titulo
        st.subheader(titulo)

        if filme.generos:
            st.write("**Gêneros:** " + ", ".join(filme.generos))

        streamings = onde_assistir(filme.id)
        if streamings:
            st.write("**Onde assistir:** " + ", ".join(streamings))
        else:
            st.write("**Onde assistir:** não disponível nos streamings cadastrados")

        # TODO (Sprint 1, H2.4 / issue #14): botão "Favoritar" aqui.
        # TODO (Sprint 3, H4.2): botão "Quero ver" (watchlist).
