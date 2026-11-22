import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest

from dados.carga_inicial import garantir_usuario_demo
from dados.conexao import inicializar_banco
from servicos.favoritos_servico import marcar_favorito
from servicos.recomendacao_exemplo import recomendar_exemplo
from ui.componentes import formatar_afinidade, formatar_preco


def _banco_de_teste(tmp_path: Path) -> tuple[int, Path]:
    caminho = tmp_path / "recomendacao.db"
    inicializar_banco(caminho)
    usuario_id, _ = garantir_usuario_demo(caminho)
    return usuario_id, caminho


# --- Recomendador provisório ---

def test_exemplo_sem_favoritos_nao_recomenda(tmp_path):
    usuario_id, caminho = _banco_de_teste(tmp_path)
    assert recomendar_exemplo(usuario_id, caminho) == []


def test_exemplo_ordena_pela_fracao_de_favoritos_no_streaming(tmp_path):
    usuario_id, caminho = _banco_de_teste(tmp_path)
    marcar_favorito(usuario_id, 1, caminho)  # Matrix: Max, Prime Video
    marcar_favorito(usuario_id, 2, caminho)  # Interestelar: Netflix, Prime Video

    resultado = recomendar_exemplo(usuario_id, caminho)

    assert [(r.streaming, r.afinidade) for r in resultado] == [
        ("Prime Video", 1.0),
        ("Max", 0.5),
        ("Netflix", 0.5),
    ]
    assert {f.titulo for f in resultado[0].filmes_em_comum} == {"Matrix", "Interestelar"}
    assert all(r.planos for r in resultado)


# --- Formatação ---

def test_formatar_preco_no_padrao_brasileiro():
    assert formatar_preco(39.9) == "R$ 39,90"
    assert formatar_preco(1234.5) == "R$ 1.234,50"


def test_formatar_afinidade_em_porcentagem():
    assert formatar_afinidade(1.0) == "100%"
    assert formatar_afinidade(0.756) == "76%"


# --- Tela (H3.5) ---
# As funções abaixo rodam dentro do AppTest. Elas substituem os favoritos e o recomendador
# por valores fixos, para a tela não depender do banco real.

def _tela_sem_favoritos():
    import sys
    from pathlib import Path

    import streamlit as st

    sys.path.insert(0, str(Path.cwd()))
    import ui.recomendacoes as tela

    tela.listar_favoritos = lambda usuario_id: []
    st.session_state["usuario_id"] = (1, "teste")
    tela.renderizar()


def _tela_com_favoritos():
    import sys
    from datetime import date
    from pathlib import Path

    import streamlit as st

    sys.path.insert(0, str(Path.cwd()))
    import ui.recomendacoes as tela
    from models.filme import Filme
    from models.plano import Plano
    from models.recomendacao import StreamingRecomendado

    matrix = Filme(id=1, titulo="Matrix", ano=1999)
    tela.listar_favoritos = lambda usuario_id: [matrix]
    tela.recomendar = lambda usuario_id: [
        StreamingRecomendado(
            streaming="Max",
            afinidade=0.8,
            filmes_em_comum=[matrix],
            planos=[Plano(1, 1, "Básico", 29.9, date(2026, 11, 10)), Plano(2, 1, "Premium", 55.9)],
        )
    ]
    st.session_state["usuario_id"] = (1, "teste")
    tela.renderizar()


def _textos_html(app: AppTest) -> str:
    return " ".join(str(el.proto) for el in app.get("html"))


def test_tela_sem_favoritos_mostra_estado_vazio():
    app = AppTest.from_function(_tela_sem_favoritos, default_timeout=15)
    app.run()
    assert not app.exception
    assert [b.label for b in app.button] == ["Buscar filmes"]
    assert "Nenhum favorito ainda" in _textos_html(app)


def test_tela_recomenda_e_mostra_planos_com_preco_e_data():
    app = AppTest.from_function(_tela_com_favoritos, default_timeout=15)
    app.run()
    assert not app.exception
    assert [b.label for b in app.button] == ["Recomendar serviços"]

    assert "Max" not in _textos_html(app)  # nada é mostrado antes de clicar

    app.button(key="recomendar").click().run()
    assert not app.exception

    html = _textos_html(app)
    assert "Max" in html and "80%" in html
    assert "Seus favoritos neste serviço: Matrix" in html
    assert "R$ 29,90" in html and "conferido em 10/11/2026" in html
    assert "data de conferência não informada" in html
