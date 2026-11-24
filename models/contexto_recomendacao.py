from dataclasses import dataclass, field
from models.filme import Filme

# Regra de negócio da recomendação: só faz sentido recomendar a partir de 3 mídias favoritas.
MIN_FAVORITOS = 3


@dataclass
class StreamingRecomendado:
    """Resultado da recomendação para um serviço de streaming."""

    nome: str
    pontuacao: float
    filmes_compativeis: list[str] = field(default_factory=list)
    generos_principais: list[str] = field(default_factory=list)


@dataclass
class ContextoRecomendacao:
    """Contrato de entrada para os corpos de recomendação (Handle/Body).

    Isola completamente os algoritmos de recomendação do banco de dados e APIs
    externas, garantindo testabilidade e divisão limpa entre as tarefas (H3.3 e H3.4).
    """

    usuario_id: int
    # Filmes que o usuário marcou como favoritos (cada um traz seus gêneros).
    favoritos: list[Filme] = field(default_factory=list)
    # Catálogo completo: cada Filme traz os gêneros usados para achar o gênero favorito.
    catalogo: list[Filme] = field(default_factory=list)
    # Mapeamento filme_id -> lista de nomes de streaming onde o filme está disponível.
    disponibilidade: dict[int, list[str]] = field(default_factory=dict)
