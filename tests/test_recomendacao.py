import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest

from dados.carga_inicial import garantir_usuario_demo
from dados.conexao import inicializar_banco
from fontes.fonte_de_filmes import FonteDeFilmes
from fontes.fonte_local import FonteLocal
from models.contexto_recomendacao import MIN_FAVORITOS
from servicos.favoritos_servico import marcar_favorito
from servicos.recomendacao_servico import planos_do_streaming, recomendar
from ui.componentes import formatar_pontuacao, formatar_preco


def _banco_de_teste(tmp_path: Path) -> tuple[int, Path]:
    caminho = tmp_path / "recomendacao.db"
    inicializar_banco(caminho)
    usuario_id, _ = garantir_usuario_demo(caminho)
    return usuario_id, caminho


def _catalogo_de_teste():
    return {
        "filmes": [
            {
                "id": 1,
                "titulo": "The Godfather",
                "ano": 1972,
                "generos": ["Crime", "Drama"],
                "streamings": ["Paramount+"],
            },
            {
                "id": 2,
                "titulo": "The Dark Knight",
                "ano": 2008,
                "generos": ["Crime", "Thriller"],
                "streamings": ["Prime Video", "Max"],
            },
            {
                "id": 3,
                "titulo": "The Dark Knight Rises",
                "ano": 2012,
                "generos": ["Crime", "Thriller"],
                "streamings": ["Prime Video"],
            },
            {
                "id": 4,
                "titulo": "Batman Begins",
                "ano": 2005,
                "generos": ["Crime"],
                "streamings": ["Max"],
            },
        ]
    }


def _usar_catalogo_de_teste(servico, monkeypatch, tmp_path):
    caminho = tmp_path / "catalogo.json"
    caminho.write_text(json.dumps(_catalogo_de_teste()), encoding="utf-8")
    monkeypatch.setattr(
        servico, "criar_fonte_de_filmes", lambda: FonteDeFilmes(FonteLocal(caminho))
    )


# --- Serviço de recomendação ---

def test_menos_de_tres_favoritos_nao_recomenda(tmp_path):
    usuario_id, caminho = _banco_de_teste(tmp_path)
    marcar_favorito(usuario_id, 1, caminho)
    marcar_favorito(usuario_id, 3, caminho)
    assert recomendar(usuario_id, caminho) == []


def test_recomenda_com_o_catalogo_da_fonte_e_a_regra_do_genero_favorito(tmp_path, monkeypatch):
    import servicos.recomendacao_servico as servico

    usuario_id, caminho = _banco_de_teste(tmp_path)
    # Os três favoritos têm "Crime": a fonte informa 2 filmes do gênero na
    # Prime Video e na Max, e 1 na Paramount+.
    for filme_id in (1, 2, 3):
        marcar_favorito(usuario_id, filme_id, caminho)
    _usar_catalogo_de_teste(servico, monkeypatch, tmp_path)

    ranking = servico.recomendar(usuario_id, caminho)

    assert [(item.nome, item.pontuacao) for item in ranking] == [
        ("Prime Video", 2.0),
        ("Max", 2.0),
        ("Paramount+", 1.0),
    ]
    assert ranking[0].generos_principais == ["Crime"]
    assert "The Dark Knight" in ranking[0].filmes_compativeis
    assert "Batman Begins" not in ranking[0].filmes_compativeis


def test_servico_monta_contexto_e_chama_a_factory(tmp_path, monkeypatch):
    import servicos.recomendacao_servico as servico
    from models.contexto_recomendacao import StreamingRecomendado

    usuario_id, caminho = _banco_de_teste(tmp_path)
    for filme_id in (1, 2, 3):
        marcar_favorito(usuario_id, filme_id, caminho)
    _usar_catalogo_de_teste(servico, monkeypatch, tmp_path)

    capturado = {}

    class RecomendadorFalso:
        def recomendar(self, contexto):
            capturado["contexto"] = contexto
            return [StreamingRecomendado(nome="Prime Video", pontuacao=2.0)]

    def criar_recomendador_falso(tipo):
        capturado["tipo"] = tipo
        return RecomendadorFalso()

    monkeypatch.setattr(servico, "criar_recomendador", criar_recomendador_falso)

    assert servico.recomendar(usuario_id, caminho)[0].nome == "Prime Video"
    assert capturado["tipo"] == "favoritos"

    contexto = capturado["contexto"]
    assert contexto.usuario_id == usuario_id
    assert [f.id for f in contexto.favoritos] == [3, 2, 1]  # mais recentes primeiro
    assert all(f.generos for f in contexto.catalogo)
    assert contexto.disponibilidade[1] == ["Paramount+"]
    assert contexto.disponibilidade[2] == ["Prime Video", "Max"]


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
# As funções abaixo rodam dentro do AppTest. Elas substituem os favoritos, o
# recomendador e os planos por valores fixos, para a tela não depender do banco.

def _tela_sem_favoritos():
    import streamlit as st

    import ui.recomendacoes as tela

    tela.listar_favoritos = lambda usuario_id: []
    st.session_state["usuario_id"] = (1, "teste")
    tela.renderizar()


def _tela_com_menos_de_tres_favoritos():
    import streamlit as st

    import ui.recomendacoes as tela
    from models.filme import Filme

    tela.listar_favoritos = lambda usuario_id: [
        Filme(id=1, titulo="The Godfather"),
        Filme(id=2, titulo="The Dark Knight"),
    ]
    st.session_state["usuario_id"] = (1, "teste")
    tela.renderizar()


def _tela_com_favoritos():
    import streamlit as st
    from datetime import date

    import ui.recomendacoes as tela
    from models.contexto_recomendacao import StreamingRecomendado
    from models.filme import Filme
    from models.plano import Plano

    tela.listar_favoritos = lambda usuario_id: [
        Filme(id=1, titulo="The Godfather"),
        Filme(id=2, titulo="The Dark Knight"),
        Filme(id=3, titulo="The Dark Knight Rises"),
    ]
    tela.recomendar = lambda usuario_id: [
        StreamingRecomendado(
            nome="Prime Video",
            pontuacao=4.0,
            filmes_compativeis=["The Dark Knight", "The Batman"],
            generos_principais=["Crime"],
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
    assert f"Adicione mais {MIN_FAVORITOS}" in _textos_html(app)


def test_tela_com_menos_de_tres_favoritos_nao_tem_botao_de_recomendar():
    app = AppTest.from_function(_tela_com_menos_de_tres_favoritos, default_timeout=15)
    app.run()
    assert not app.exception
    assert [b.label for b in app.button] == ["Buscar filmes"]
    html = _textos_html(app)
    assert "Faltam favoritos" in html
    assert "Adicione mais 1" in html


def test_tela_recomenda_e_mostra_planos_com_preco_e_data():
    app = AppTest.from_function(_tela_com_favoritos, default_timeout=15)
    app.run()
    assert not app.exception
    assert "Prime Video" not in _textos_html(app)  # nada é mostrado antes de clicar

    app.button(key="recomendar").click().run()
    assert not app.exception

    html = _textos_html(app)
    assert "Prime Video" in html and "4,0" in html and "filmes do gênero" in html
    assert "Gênero favorito: Crime" in html
    assert "Filmes desse gênero: The Dark Knight, The Batman" in html
    assert "R$ 29,90" in html and "conferido em 10/11/2026" in html
    assert "data de conferência não informada" in html
