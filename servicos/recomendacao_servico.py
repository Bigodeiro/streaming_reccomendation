"""Serviço de recomendação: monta o contexto, usa a Factory e devolve o resultado.

Fluxo:
1. lê os favoritos do usuário e aplica o mínimo de MIN_FAVORITOS mídias;
2. carrega o catálogo (cada filme traz seus gêneros) e a disponibilidade por filme;
3. monta o ContextoRecomendacao;
4. cria o Recomendador pela Factory e devolve o ranking para a tela.

A lógica da recomendação fica no Body escolhido pela Factory; este módulo só
prepara os dados e entrega o resultado.
"""

from pathlib import Path

from dados.conexao import CAMINHO_BANCO
from fabricas import criar_fonte_de_filmes, criar_recomendador
from models.contexto_recomendacao import (
    MIN_FAVORITOS,
    ContextoRecomendacao,
    StreamingRecomendado,
)
from models.plano import Plano
from servicos.favoritos_servico import listar_favoritos

# TODO (H7): ler planos e preços reais do banco.
_PLANOS_EXEMPLO = [("Básico (exemplo)", 20.0), ("Padrão (exemplo)", 40.0)]


def recomendar(usuario_id: int, caminho: Path = CAMINHO_BANCO) -> list[StreamingRecomendado]:
    """Devolve os streamings ordenados por filmes do gênero favorito do usuário."""
    favoritos = listar_favoritos(usuario_id, caminho)
    if len(favoritos) < MIN_FAVORITOS:
        return []

    fonte = criar_fonte_de_filmes()
    catalogo = fonte.listar_filmes()
    contexto = ContextoRecomendacao(
        usuario_id=usuario_id,
        favoritos=favoritos,
        catalogo=catalogo,
        disponibilidade={filme.id: fonte.streamings_do_filme(filme.id) for filme in catalogo},
    )
    return criar_recomendador("favoritos").recomendar(contexto)


def planos_do_streaming(nome_streaming: str) -> list[Plano]:
    """Planos FICTÍCIOS de um streaming, usados só enquanto a H7 não chega."""
    streaming_id = sum(map(ord, nome_streaming))  # id estável só para os objetos de exemplo
    return [
        Plano(id=streaming_id * 10 + i, streaming_id=streaming_id, nome=nome, preco_mensal=preco)
        for i, (nome, preco) in enumerate(_PLANOS_EXEMPLO)
    ]


__all__ = ["MIN_FAVORITOS", "planos_do_streaming", "recomendar"]
