"""Ponto de entrada do sistema. Para rodar: streamlit run app.py
"""
import streamlit as st

from dados.conexao import inicializar_banco
from dados.carga_inicial import garantir_usuario_demo
from ui.identidade import CAMINHO_LOGO, NOME_APP, aplicar_estilo
from ui.navegacao import PAGINAS

st.set_page_config(page_title=NOME_APP, page_icon=":material/travel_explore:")

inicializar_banco()

if "usuario_id" not in st.session_state:
    st.session_state["usuario_id"] = garantir_usuario_demo()

aplicar_estilo()
st.logo(str(CAMINHO_LOGO), size="large")

st.navigation(PAGINAS, position="top").run()
