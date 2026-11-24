from abc import abstractmethod

from core.handle_body import Corpo
from models.filme import Filme


class CorpoFonte(Corpo):
    """Contrato que toda fonte de filmes precisa cumprir."""

    @abstractmethod
    def buscar_por_titulo(self, titulo: str) -> list[Filme]:
        """Filmes cujo título contém o texto buscado."""

    @abstractmethod
    def obter_filme(self, filme_id: int) -> Filme | None:
        """Um filme pelo id, ou None se não existir."""

    @abstractmethod
    def streamings_do_filme(self, filme_id: int) -> list[str]:
        """Nomes canônicos dos streamings em que o filme está disponível."""

    def onde_assistir(self, filme_id: int) -> list[str]:
        """Alias de `streamings_do_filme` usado pelas telas antigas."""
        return self.streamings_do_filme(filme_id)

    def listar_filmes(self) -> list[Filme]:
        """Todos os filmes do catálogo (padrão: busca com termo vazio)."""
        return self.buscar_por_titulo("")
