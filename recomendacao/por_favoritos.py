"""Módulo da estratégia de recomendação baseada em favoritos (H3.4).

Implementa o algoritmo de filtragem baseada em conteúdo (Content-Based Filtering):
1. Constrói o perfil de preferências a partir da frequência de gêneros dos filmes favoritados.
2. Atribui uma nota de afinidade para cada filme do catálogo ainda não favoritado.
3. Agrega as notas de afinidade dos filmes disponíveis em cada streaming.
4. Gera um ranking ordenado com a pontuação e justificativa da recomendação.
"""

from collections import Counter, defaultdict

from models.contexto_recomendacao import ContextoRecomendacao, StreamingRecomendado
from models.filme import Filme
from recomendacao.corpo_recomendacao import CorpoRecomendacao


class RecomendaPorFavoritos(CorpoRecomendacao):
    """Body concreto do padrão Bridge para recomendação baseada nos favoritos."""

    def recomendar(self, contexto: ContextoRecomendacao) -> list[StreamingRecomendado]:
        if not contexto.favoritos or not contexto.catalogo:
            return []

        # 1. Perfil de interesse do usuário: frequência de cada gênero nos favoritos
        perfil_generos = self._calcular_perfil_generos(contexto.favoritos)
        if not perfil_generos:
            return []

        ids_favoritos = {f.id for f in contexto.favoritos}

        # 2. Avaliar afinidade de cada filme do catálogo que o usuário ainda não favoritou
        afinidades_filmes: dict[int, tuple[float, Filme]] = {}
        for filme in contexto.catalogo:
            if filme.id in ids_favoritos:
                continue

            pontos = sum(perfil_generos[g] for g in filme.generos if g in perfil_generos)
            if pontos > 0:
                afinidades_filmes[filme.id] = (pontos, filme)

        # 3. Mapear pontuação e filmes compatíveis para cada serviço de streaming
        pontuacao_streaming: dict[str, float] = defaultdict(float)
        filmes_por_streaming: dict[str, list[tuple[float, str]]] = defaultdict(list)
        generos_por_streaming: dict[str, Counter] = defaultdict(Counter)

        for filme_id, (pontos, filme) in afinidades_filmes.items():
            streamings = contexto.disponibilidade.get(filme_id, [])
            for streaming in streamings:
                pontuacao_streaming[streaming] += pontos
                filmes_por_streaming[streaming].append((pontos, filme.titulo))
                for g in filme.generos:
                    if g in perfil_generos:
                        generos_por_streaming[streaming][g] += perfil_generos[g]

        # 4. Montar os objetos de resultado e ordenar pelo ranking de afinidade
        resultados: list[StreamingRecomendado] = []
        for streaming, pontuacao in pontuacao_streaming.items():
            # Ordena filmes do streaming pelos de maior afinidade primeiro
            filmes_ordenados = [
                titulo for _, titulo in sorted(filmes_por_streaming[streaming], reverse=True)
            ]
            # Principais gêneros que contribuíram para a nota do streaming
            principais_generos = [
                g for g, _ in generos_por_streaming[streaming].most_common(3)
            ]

            resultados.append(
                StreamingRecomendado(
                    nome=streaming,
                    pontuacao=round(pontuacao, 1),
                    filmes_compativeis=filmes_ordenados,
                    generos_principais=principais_generos,
                )
            )

        # Ordenar do streaming mais recomendado para o menos recomendado
        resultados.sort(key=lambda r: r.pontuacao, reverse=True)
        return resultados

    @staticmethod
    def _calcular_perfil_generos(favoritos: list[Filme]) -> Counter:
        """Gera um mapa de frequência de gêneros a partir dos favoritos."""
        contagem = Counter()
        for filme in favoritos:
            for genero in filme.generos:
                contagem[genero] += 1
        return contagem
