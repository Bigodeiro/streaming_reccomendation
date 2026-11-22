import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest

from dados.carga_inicial import garantir_usuario_demo
from dados.conexao import inicializar_banco
from servicos.favoritos_servico import marcar_favorito
from servicos.recomendacao_provisoria import planos_do_streaming, recomendar
from ui.componentes import formatar_pontuacao, formatar_preco


def _banco_de_teste(tmp_path: Path) -> tuple[int, Path]:
    caminho = tmp_path / "recomendacao.db"
    inicializar_banco(caminho)
    usuario_id, _ = garantir_usuario_demo(caminho)
    return usuario_id, caminho


# --- Ponte provisória para a lógica da H3.4 ---

def test_sem_favoritos_nao_recomenda(tmp_path):
    usuario_id, caminho = _banco_de_teste(tmp_path)
    assert recomendar(usuario_id, caminho) == []


def test_recomenda_com_o_catalogo_real_e_a_logica_da_h3_4(tmp_path):
    usuario_id, caminho = _banco_de_teste(tmp_path)
    marcar_favorito(usuario_id, 1, caminho)  # Matrix: Ficção científica, Ação

    ranking = recomendar(usuario_id, caminho)

    assert ranking, "deveria recomendar ao menos um streaming"
    pontuacoes = [r.pontuacao for r in ranking]
    assert pontuacoes == sorted(pontuacoes, reverse=True)
    # A Origem tem os mesmos gêneros de Matrix e está na Netflix e na Max.
    assert any("A Origem" in r.filmes_compativeis for r in ranking)
    # Filme já favoritado não é sugerido de novo.
    assert all("Matrix" not in r.filmes_compativeis for r in ranking)


def test_planos_de_exemplo_sao_marcados_como_exemplo():
    planos = planos_do_streaming("Max")
    assert planos and all("(exemplo)" in p.nome for p in planos)
    assert all(p.conferido_em is None for p in planos)


# --- Formatação ---

def test_formatar_preco_no_padrao_brasileiro():
    assert formatar_preco(39.9) == "R$ 39,90"
    assert formatar_preco(1234.5) == "R$ 1.234,50"


def test_formatar_pontuacao_com_virgula():
    assert formatar_pontuacao(2.0) == "2,0"
    assert formatar_pontuacao(3.25) == "3,2"


# --- Tela (H3.5) ---
# As funções abaixo rodam dentro do AppTest. Elas substituem os favoritos, o recomendador
# e os planos por valores fixos, para a tela não depender do banco real.

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
    from models.contexto_recomendacao import StreamingRecomendado
    from models.filme import Filme
    from models.plano import Plano

    tela.listar_favoritos = lambda usuario_id: [Filme(id=1, titulo="Matrix", ano=1999)]
    tela.recomendar = lambda usuario_id: [
        StreamingRecomendado(
            nome="Max",
            pontuacao=4.0,
            filmes_compativeis=["A Origem", "Duna"],
            generos_principais=["Ficção científica", "Ação"],
        )
    ]
    tela.planos_do_streaming = lambda nome: [
        Plano(1, 1, "Básico", 29.9, date(2026, 11, 10)),
        Plano(2, 1, "Premium", 55.9),
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
    assert "Max" not in _textos_html(app)  # nada é mostrado antes de clicar

    app.button(key="recomendar").click().run()
    assert not app.exception

    html = _textos_html(app)
    assert "Max" in html and "4,0" in html and "pontos de afinidade" in html
    assert "Combina com: Ficção científica, Ação" in html
    assert "Você pode gostar: A Origem, Duna" in html
    assert "R$ 29,90" in html and "conferido em 10/11/2026" in html
    assert "data de conferência não informada" in html
