from dataclasses import dataclass, field

from models.plano import Plano


@dataclass
class Streaming:
    id: int
    nome: str
    planos: list[Plano] = field(default_factory=list)