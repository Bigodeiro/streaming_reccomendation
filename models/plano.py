from dataclasses import dataclass


@dataclass
class Plano:
    id: int
    streaming_id: int
    nome: str
    preco_mensal: float
