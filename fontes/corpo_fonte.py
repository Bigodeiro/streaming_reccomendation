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
    def onde_assistir(self, filme_id: int) -> list[str]:
        """Nomes dos streamings em que o filme está disponível."""