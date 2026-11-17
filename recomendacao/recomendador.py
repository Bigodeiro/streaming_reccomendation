from core.handle_body import Handle
from models.contexto_recomendacao import ContextoRecomendacao, StreamingRecomendado


class Recomendador(Handle):
    """Handle do padrão Bridge: representa o ponto de acesso para os serviços.

    Delega a execução real da recomendação para a implementação (_corpo)
    injetada pela Factory em tempo de execução.
    """

    def recomendar(self, contexto: ContextoRecomendacao) -> list[StreamingRecomendado]:
        return self._corpo.recomendar(contexto)
