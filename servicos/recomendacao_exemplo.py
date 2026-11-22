"""Recomendador PROVISÓRIO, só para a tela da H3.5 funcionar antes da H3.1/H3.3/H3.4.

- O ranking usa dados reais: a fração dos favoritos do usuário disponível em cada streaming.
  Não é o critério da H3.4; serve só para a tela ter algo coerente para mostrar.
- Os planos e preços são FICTÍCIOS (nomes terminam em "(exemplo)" e não têm data de conferência).

Quando o serviço real existir, a tela troca o import de `recomendar_exemplo` pelo dele
e este arquivo pode ser apagado.
"""

from collections import defaultdict
from pathlib import Path

from dados.conexao import CAMINHO_BANCO
from fabricas import criar_fonte_de_filmes
from models.filme import Filme
from models.plano import Plano
from models.recomendacao import StreamingRecomendado
from servicos.favoritos_servico import listar_favoritos

_PLANOS_EXEMPLO = [("Básico (exemplo)", 20.0), ("Padrão (exemplo)", 40.0)]


def _planos_exemplo(streaming_id: int) -> list[Plano]:
    return [
        Plano(id=streaming_id * 10 + i, streaming_id=streaming_id, nome=nome, preco_mensal=preco)
        for i, (nome, preco) in enumerate(_PLANOS_EXEMPLO)
    ]


def recomendar_exemplo(usuario_id: int, caminho: Path = CAMINHO_BANCO) -> list[StreamingRecomendado]:
    favoritos = listar_favoritos(usuario_id, caminho)
    if not favoritos:
        return []

    fonte = criar_fonte_de_filmes()
    por_streaming: dict[str, list[Filme]] = defaultdict(list)
    for filme in favoritos:
        for streaming in fonte.onde_assistir(filme.id):
            por_streaming[streaming].append(filme)

    recomendados = [
        StreamingRecomendado(
            streaming=streaming,
            afinidade=len(filmes) / len(favoritos),
            filmes_em_comum=filmes,
            planos=_planos_exemplo(indice),
        )
        for indice, (streaming, filmes) in enumerate(sorted(por_streaming.items()), 1)
    ]
    return sorted(recomendados, key=lambda r: (-r.afinidade, r.streaming))
