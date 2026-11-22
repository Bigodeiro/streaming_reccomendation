import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fabricas import criar_recomendador
from models.contexto_recomendacao import ContextoRecomendacao
from models.filme import Filme
from recomendacao.por_favoritos import RecomendaPorFavoritos
from recomendacao.recomendador import Recomendador


def _criar_dados_teste():
    f1 = Filme(id=1, titulo="Interestelar", generos=["Ficção Científica", "Drama"])
    f2 = Filme(id=2, titulo="Matrix", generos=["Ficção Científica", "Ação"])
    f3 = Filme(id=3, titulo="Duna", generos=["Ficção Científica", "Aventura"])
    f4 = Filme(id=4, titulo="O Poderoso Chefão", generos=["Crime", "Drama"])
    f5 = Filme(id=5, titulo="Superbad", generos=["Comédia"])

    catalogo = [f1, f2, f3, f4, f5]
    disponibilidade = {
        1: ["Max"],
        2: ["Max", "Prime Video"],
        3: ["Max"],
        4: ["Prime Video"],
        5: ["Netflix"],
    }
    return [f1, f2], catalogo, disponibilidade


def test_recomendacao_ranking_por_favoritos():
    favoritos, catalogo, disponibilidade = _criar_dados_teste()
    # Usuário favoritou Interestelar e Matrix.
    # Perfil: Ficção Científica: 2, Drama: 1, Ação: 1.
    # Filmes candidatos não favoritados:
    # f3 (Duna): Ficção Científica (2) -> Score = 2. No streaming Max.
    # f4 (O Poderoso Chefão): Drama (1) -> Score = 1. No streaming Prime Video.
    # f5 (Superbad): Comédia (0) -> Score = 0.
    # Portanto, Max deve ter pontuação 2.0 e Prime Video 1.0; Netflix não tem filmes afins.

    contexto = ContextoRecomendacao(
        usuario_id=1,
        favoritos=favoritos,
        catalogo=catalogo,
        disponibilidade=disponibilidade,
    )

    recomendador = RecomendaPorFavoritos()
    ranking = recomendador.recomendar(contexto)

    assert len(ranking) >= 2
    assert ranking[0].nome == "Max"
    assert ranking[0].pontuacao == 2.0
    assert "Duna" in ranking[0].filmes_compativeis
    assert "Ficção Científica" in ranking[0].generos_principais

    assert ranking[1].nome == "Prime Video"
    assert ranking[1].pontuacao == 1.0
    assert "O Poderoso Chefão" in ranking[1].filmes_compativeis


def test_filmes_ja_favoritados_nao_pontuam_novamente():
    favoritos, catalogo, disponibilidade = _criar_dados_teste()
    # Se o catálogo contiver apenas os filmes que o usuário já favoritou,
    # não deve haver recomendação, pois não há filmes novos para indicar.
    contexto = ContextoRecomendacao(
        usuario_id=1,
        favoritos=favoritos,
        catalogo=favoritos,  # apenas filmes já favoritados
        disponibilidade=disponibilidade,
    )

    recomendador = RecomendaPorFavoritos()
    ranking = recomendador.recomendar(contexto)
    assert ranking == []


def test_contexto_sem_favoritos_retorna_vazio():
    _, catalogo, disponibilidade = _criar_dados_teste()
    contexto = ContextoRecomendacao(
        usuario_id=1,
        favoritos=[],
        catalogo=catalogo,
        disponibilidade=disponibilidade,
    )
    recomendador = RecomendaPorFavoritos()
    assert recomendador.recomendar(contexto) == []


def test_integracao_handle_body_e_factory():
    favoritos, catalogo, disponibilidade = _criar_dados_teste()
    contexto = ContextoRecomendacao(
        usuario_id=1,
        favoritos=favoritos,
        catalogo=catalogo,
        disponibilidade=disponibilidade,
    )

    handle = criar_recomendador("favoritos")
    assert isinstance(handle, Recomendador)
    assert isinstance(handle._corpo, RecomendaPorFavoritos)

    ranking = handle.recomendar(contexto)
    assert len(ranking) > 0
    assert ranking[0].nome == "Max"
