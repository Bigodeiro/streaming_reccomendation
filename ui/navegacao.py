"""Páginas do app. Ficam aqui para que uma tela possa levar a outra com st.switch_page."""

import streamlit as st

from ui import busca, listas, recomendacoes

PAGINA_BUSCA = st.Page(
    busca.renderizar, title="Buscar", icon=":material/search:", url_path="busca", default=True
)
PAGINA_LISTAS = st.Page(
    listas.renderizar, title="Minhas listas", icon=":material/favorite:", url_path="listas"
)
PAGINA_RECOMENDACOES = st.Page(
    recomendacoes.renderizar,
    title="Recomendações",
    icon=":material/auto_awesome:",
    url_path="recomendacoes",
)

PAGINAS = [PAGINA_BUSCA, PAGINA_LISTAS, PAGINA_RECOMENDACOES]
