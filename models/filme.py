from dataclasses import dataclass, field


@dataclass
class Filme:
    """Um título do catálogo; os streamings vêm de `streamings_do_filme(id)`."""

    id: int
    titulo: str
    ano: int | None = None
    generos: list[str] = field(default_factory=list)
