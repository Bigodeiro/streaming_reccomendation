"""Estratégia simples de recomendação a partir dos favoritos.

Regra da Sprint 2:
1. O gênero favorito é o mais frequente entre os gêneros dos filmes favoritados.
2. Para cada streaming, contamos quantos filmes desse gênero estão disponíveis.
3. O ranking vai do serviço com mais filmes do gênero para o que tem menos.

A recomendação só acontece com pelo menos MIN_FAVORITOS filmes favoritos.
"""

from collections import Counter, defaultdict

from models.contexto_recomendacao import (
    MIN_FAVORITOS,
    ContextoRecomendacao,
    StreamingRecomendado,
)
from models.filme import Filme
from recomendacao.corpo_recomendacao import CorpoRecomendacao


class RecomendaPorFavoritos(CorpoRecomendacao):
    """Body concreto do padrão Bridge para recomendação baseada nos favoritos."""

    def recomendar(self, contexto: ContextoRecomendacao) -> list[StreamingRecomendado]:
        if len(contexto.favoritos) < MIN_FAVORITOS or not contexto.catalogo:
            return []

        genero_favorito = self.genero_favorito(contexto.favoritos)
        if genero_favorito is None:
            return []

        # Contagem de filmes do gênero por streaming. A ordem de inserção (a do
        # catálogo) desempata serviços com a mesma quantidade de filmes.
        quantidade_por_streaming: Counter[str] = Counter()
        filmes_por_streaming: dict[str, list[str]] = defaultdict(list)
        for filme in contexto.catalogo:
            if not self._tem_genero(filme, genero_favorito):
                continue
            for streaming in contexto.disponibilidade.get(filme.id, []):
                quantidade_por_streaming[streaming] += 1
                filmes_por_streaming[streaming].append(filme.titulo)

        return [
            StreamingRecomendado(
                nome=streaming,
                pontuacao=float(quantidade),
                filmes_compativeis=filmes_por_streaming[streaming],
                generos_principais=[genero_favorito],
            )
            for streaming, quantidade in quantidade_por_streaming.most_common()
        ]

    @staticmethod
    def genero_favorito(favoritos: list[Filme]) -> str | None:
        """Gênero mais frequente nos favoritos, ou None se não houver gêneros.

        A comparação ignora caixa e espaços, mas o nome devolvido é o que veio
        dos filmes. Em empate, vale o primeiro gênero encontrado.
        """
        contagem: Counter[str] = Counter()
        nomes: dict[str, str] = {}
        for filme in favoritos:
            for genero in filme.generos:
                chave = genero.strip().casefold()
                if not chave:
                    continue
                nomes.setdefault(chave, genero.strip())
                contagem[chave] += 1

        if not contagem:
            return None
        chave, _ = contagem.most_common(1)[0]
        return nomes[chave]

    @staticmethod
    def _tem_genero(filme: Filme, genero: str) -> bool:
        alvo = genero.strip().casefold()
        return any(g.strip().casefold() == alvo for g in filme.generos)
