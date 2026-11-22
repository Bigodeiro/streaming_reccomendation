"""Páginas do app. Ficam aqui para que uma tela possa levar a outra com st.switch_page."""

import streamlit as st

from ui import busca, listas

PAGINA_BUSCA = st.Page(
    busca.renderizar, title="Buscar", icon=":material/search:", url_path="busca", default=True
)
PAGINA_LISTAS = st.Page(
    listas.renderizar, title="Minhas listas", icon=":material/favorite:", url_path="listas"
)

PAGINAS = [PAGINA_BUSCA, PAGINA_LISTAS]
