from dataclasses import dataclass
from datetime import date


@dataclass
class Plano:
    id: int
    streaming_id: int
    nome: str
    preco_mensal: float
    # Dia em que o preço foi conferido no site do streaming (H3.1). None = ainda não conferido.
    conferido_em: date | None = None
