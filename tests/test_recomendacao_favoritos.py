import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fabricas import criar_recomendador
from models.contexto_recomendacao import MIN_FAVORITOS, ContextoRecomendacao
from models.filme import Filme
from recomendacao.por_favoritos import RecomendaPorFavoritos
from recomendacao.recomendador import Recomendador


def _criar_dados_teste():
    f1 = Filme(id=1, titulo="Interestelar", generos=["Ficção científica", "Drama"])
    f2 = Filme(id=2, titulo="Matrix", generos=["Ficção científica", "Ação"])
    f3 = Filme(id=3, titulo="Duna", generos=["Ficção científica", "Aventura"])
    f4 = Filme(id=4, titulo="O Poderoso Chefão", generos=["Crime", "Drama"])
    f5 = Filme(id=5, titulo="Superbad", generos=["Comédia"])

    catalogo = [f1, f2, f3, f4, f5]
    disponibilidade = {
        1: ["Max", "Netflix"],
        2: ["Max", "Prime Video"],
        3: ["Max", "Netflix"],
        4: ["Prime Video"],
        5: ["Netflix"],
    }
    return [f1, f2, f3], catalogo, disponibilidade


def _contexto(favoritos, catalogo, disponibilidade):
    return ContextoRecomendacao(
        usuario_id=1,
        favoritos=favoritos,
        catalogo=catalogo,
        disponibilidade=disponibilidade,
    )


def test_genero_favorito_e_ranking_por_quantidade_de_filmes():
    favoritos, catalogo, disponibilidade = _criar_dados_teste()
    # Ficção científica aparece nos 3 favoritos (Ação e Drama, em apenas 1 cada um).
    # Max: 3 filmes do gênero; Netflix: 2; Prime Video: 1.

    ranking = RecomendaPorFavoritos().recomendar(_contexto(favoritos, catalogo, disponibilidade))

    assert [(r.nome, r.pontuacao) for r in ranking] == [
        ("Max", 3.0),
        ("Netflix", 2.0),
        ("Prime Video", 1.0),
    ]
    assert "Duna" in ranking[0].filmes_compativeis
    assert ranking[0].generos_principais == ["Ficção científica"]
    assert "Superbad" not in [titulo for r in ranking for titulo in r.filmes_compativeis]


def test_menos_de_tres_favoritos_nao_recomenda():
    favoritos, catalogo, disponibilidade = _criar_dados_teste()
    assert MIN_FAVORITOS == 3

    contexto = _contexto(favoritos[: MIN_FAVORITOS - 1], catalogo, disponibilidade)
    assert RecomendaPorFavoritos().recomendar(contexto) == []


def test_contexto_sem_favoritos_retorna_vazio():
    _, catalogo, disponibilidade = _criar_dados_teste()
    contexto = _contexto([], catalogo, disponibilidade)
    assert RecomendaPorFavoritos().recomendar(contexto) == []


def test_favoritos_sem_genero_nao_recomendam():
    _, catalogo, disponibilidade = _criar_dados_teste()
    sem_genero = [Filme(id=i, titulo=f"Sem gênero {i}") for i in range(10, 10 + MIN_FAVORITOS)]
    contexto = _contexto(sem_genero, catalogo, disponibilidade)
    assert RecomendaPorFavoritos().recomendar(contexto) == []


def test_genero_favorito_ignora_caixa_e_espacos():
    favoritos = [
        Filme(id=1, titulo="A", generos=["  Ação ", "Drama"]),
        Filme(id=2, titulo="B", generos=["ação", "Comédia"]),
        Filme(id=3, titulo="C", generos=["AÇÃO"]),
    ]
    assert RecomendaPorFavoritos.genero_favorito(favoritos) == "Ação"


def test_integracao_handle_body_e_factory():
    favoritos, catalogo, disponibilidade = _criar_dados_teste()
    contexto = _contexto(favoritos, catalogo, disponibilidade)

    handle = criar_recomendador("favoritos")
    assert isinstance(handle, Recomendador)
    assert isinstance(handle._corpo, RecomendaPorFavoritos)

    ranking = handle.recomendar(contexto)
    assert ranking[0].nome == "Max"
    assert ranking[0].pontuacao == 3.0
