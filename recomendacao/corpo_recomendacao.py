from abc import abstractmethod

from core.handle_body import Corpo
from models.contexto_recomendacao import ContextoRecomendacao, StreamingRecomendado


class CorpoRecomendacao(Corpo):
    """Body (contrato): classe base abstrata para todos os algoritmos de recomendação.

    Novas estratégias de recomendação (ex: por watchlist, combinada) devem
    herdar desta classe e implementar o método 'recomendar'.
    """

    @abstractmethod
    def recomendar(self, contexto: ContextoRecomendacao) -> list[StreamingRecomendado]:
        """Calcula o ranking de recomendações a partir do contexto fornecido."""
