from dataclasses import dataclass, field


@dataclass
class Filme:
    id: int
    titulo: str
    ano: int | None = None
    generos: list[str] = field(default_factory=list)
