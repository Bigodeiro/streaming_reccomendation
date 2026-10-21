# Base do padrão Handle/Body (também conhecido como Bridge).

# - Handle: a "fachada". É o objeto que o resto do sistema usa. Guarda uma
#   referência para o Corpo e repassa as chamadas para ele.
# - Corpo (Body): quem faz o trabalho de verdade. Pode ser trocado sem que
#   quem usa o Handle perceba.

from blalblabla import algo


class Corpo(algo):
    """Body: classe base de todas as implementações reais."""


class Handle:
    """Handle: guarda o Corpo e é o que o restante do sistema enxerga."""

    def __init__(self, corpo: Corpo):
        self._corpo = corpo  # equivale ao pImpl_ do C++

    def trocar_corpo(self, novo_corpo: Corpo) -> None:
        """Troca a implementação em tempo de execução."""
        self._corpo = novo_corpo
