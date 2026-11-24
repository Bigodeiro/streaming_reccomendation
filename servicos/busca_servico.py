from fabricas import criar_fonte_de_filmes
from models.filme import Filme


def buscar_filmes(titulo: str) -> list[Filme]:
    """Busca filmes por título usando a fonte configurada (H2.2)."""
    titulo = titulo.strip()
    if not titulo:
        return []
    fonte = criar_fonte_de_filmes()
    return fonte.buscar_por_titulo(titulo)


def streamings_do_filme(filme_id: int) -> list[str]:
    """Nomes canônicos dos streamings de assinatura em que o filme está disponível."""
    fonte = criar_fonte_de_filmes()
    return fonte.streamings_do_filme(filme_id)


def onde_assistir(filme_id: int) -> list[str]:
    """Alias de `streamings_do_filme`."""
    return streamings_do_filme(filme_id)
