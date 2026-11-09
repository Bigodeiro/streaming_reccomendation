"""Ponto de entrada do sistema. Para rodar: streamlit run app.py
"""
import streamlit as st

from dados.conexao import inicializar_banco
from dados.carga_inicial import garantir_usuario_demo
from ui import busca, listas

st.set_page_config(page_title="Streaming Recommendation", page_icon="🎬")

inicializar_banco()

if "usuario_id" not in st.session_state:
    st.session_state["usuario_id"] = garantir_usuario_demo()

TELAS = {
    "Buscar filmes": busca.renderizar,
    "Minhas listas": listas.renderizar,
}

with st.sidebar:
    st.title("🎬 Streaming Recommendation")
    _, nome_usuario = st.session_state["usuario_id"]
    st.caption(f"Usuário: {nome_usuario}")
    tela_escolhida = st.radio("Navegação", list(TELAS))

TELAS[tela_escolhida]()
