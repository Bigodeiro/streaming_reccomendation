"""Ponto de entrada do sistema. Para rodar: streamlit run app.py
"""
import streamlit as st

from dados.conexao import inicializar_banco
from dados.carga_inicial import garantir_usuario_demo


inicializar_banco()

if "usuario_id" not in st.session_state:
    st.session_state["usuario_id"] = garantir_usuario_demo()
