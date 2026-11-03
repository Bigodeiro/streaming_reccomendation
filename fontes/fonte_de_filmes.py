from core.handle_body import Handle
from models.filme import Filme


class FonteDeFilmes(Handle):
    """Handle: o resto do sistema usa esta classe e não sabe de onde vêm os dados."""

    def buscar_por_titulo(self, titulo: str) -> list[Filme]:
        return self._corpo.buscar_por_titulo(titulo)

    def obter_filme(self, filme_id: int) -> Filme | None:
        return self._corpo.obter_filme(filme_id)

    def onde_assistir(self, filme_id: int) -> list[str]:
        return self._corpo.onde_assistir(filme_id)