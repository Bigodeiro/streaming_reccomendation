"""Contrato entre o serviço de recomendação (H3.3/H3.4) e a tela (H3.5).

O serviço devolve uma lista de StreamingRecomendado já ORDENADA do mais para o
menos recomendado. A tela só exibe; não recalcula nada.
"""

from dataclasses import dataclass, field

from models.filme import Filme
from models.plano import Plano


@dataclass
class StreamingRecomendado:
    streaming: str
    # Nota de afinidade com os favoritos do usuário, de 0.0 a 1.0 (a tela mostra em %).
    afinidade: float
    # Favoritos do usuário disponíveis neste streaming.
    filmes_em_comum: list[Filme] = field(default_factory=list)
    planos: list[Plano] = field(default_factory=list)
