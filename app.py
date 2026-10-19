"""Ponto de entrada do sistema. Para rodar: streamlit run app.py
"""
import streamlit as st

from dados.conexao import inicializar_banco
from dados.carga_inicial import garantir_usuario_demo
from ui import busca, listas, recomendacoes

st.set_page_config(page_title="Streaming Recommendation", page_icon="🎬", layout="wide")

inicializar_banco()

# Perfil simulado (Sprints 1 a 4). Na Sprint 5 (H1) isto é trocado pelo login real.
if "usuario_id" not in st.session_state:
    st.session_state["usuario_id"] = garantir_usuario_demo()

st.title("Streaming Recommendation")

aba_busca, aba_listas, aba_recomendacoes = st.tabs(
    ["Buscar filmes", "Minhas listas", "Recomendações"]
)
with aba_busca:
    busca.renderizar()
with aba_listas:
    listas.renderizar()
with aba_recomendacoes:
    recomendacoes.renderizar()
