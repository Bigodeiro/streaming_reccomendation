"""Testes de fumaça da interface: o app abre e a busca da home funciona."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

CAMINHO_APP = str(Path(__file__).resolve().parent.parent / "app.py")


def _abrir_app() -> AppTest:
    app = AppTest.from_file(CAMINHO_APP, default_timeout=15)
    app.run()
    assert not app.exception
    return app


def test_home_abre_com_busca_vazia_e_exemplos_no_placeholder():
    app = _abrir_app()
    busca = app.text_input(key="termo_busca")
    assert busca.value == ""
    assert "The Dark Knight" in busca.placeholder


def test_busca_na_home_mostra_resultado_com_botao_de_favorito():
    app = _abrir_app()
    app.text_input(key="termo_busca").input("dark knight").run()
    assert not app.exception
    chaves = {b.key for b in app.button}
    assert {"busca_favoritar_2", "busca_remover_fav_2"} & chaves


def _tela_listas_sem_favoritos():
    import sys
    from pathlib import Path

    import streamlit as st

    sys.path.insert(0, str(Path.cwd()))
    from dados.conexao import inicializar_banco
    from ui import listas
    from ui.identidade import aplicar_estilo

    inicializar_banco()
    st.session_state["usuario_id"] = (-1, "sem favoritos")  # id que nunca existe no banco
    aplicar_estilo()
    listas.renderizar()


def test_listas_vazia_mostra_acao_de_buscar():
    app = AppTest.from_function(_tela_listas_sem_favoritos, default_timeout=15)
    app.run()
    assert not app.exception
    assert [b.label for b in app.button] == ["Buscar filmes"]
