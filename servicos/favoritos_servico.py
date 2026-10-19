from models.filme import Filme


def marcar_favorito(usuario_id: int, filme_id: int) -> None:
    # TODO (Sprint 1, H2.4): gravar na tabela favoritos (dados/schema.sql).
    raise NotImplementedError("H2.4: marcar filme como favorito")


def listar_favoritos(usuario_id: int) -> list[Filme]:
    # TODO (Sprint 1, H2.4): ler os ids da tabela e buscar os filmes na fonte.
    raise NotImplementedError("H2.4: listar favoritos")


def remover_favorito(usuario_id: int, filme_id: int) -> None:
    # TODO: opcional, se sobrar tempo.
    raise NotImplementedError("remover favorito")
