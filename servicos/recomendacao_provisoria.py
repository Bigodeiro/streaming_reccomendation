"""Ponte PROVISÓRIA entre a tela (H3.5) e a lógica de recomendação (H3.4).

Faz o papel da H3.3 enquanto ela não chega: monta o ContextoRecomendacao e chama
o Recomendador criado pela Factory. A lógica é a real (RecomendaPorFavoritos).

O que ainda é provisório:
- Catálogo: a fonte de filmes ainda não tem um método para listar todos os filmes,
  então usamos uma busca por título vazia, que devolve tudo na FonteLocal (H3.2/H3.3).
- Planos e preços: FICTÍCIOS até a H3.1 (nomes terminam em "(exemplo)", sem data de conferência).

Quando a H3.3 e a H3.1 existirem, a tela troca os imports e este arquivo pode ser apagado.
"""

from pathlib import Path

from dados.conexao import CAMINHO_BANCO
from fabricas import criar_fonte_de_filmes, criar_recomendador
from models.contexto_recomendacao import ContextoRecomendacao, StreamingRecomendado
from models.plano import Plano
from servicos.favoritos_servico import listar_favoritos

_PLANOS_EXEMPLO = [("Básico (exemplo)", 20.0), ("Padrão (exemplo)", 40.0)]


def recomendar(usuario_id: int, caminho: Path = CAMINHO_BANCO) -> list[StreamingRecomendado]:
    favoritos = listar_favoritos(usuario_id, caminho)
    if not favoritos:
        return []

    fonte = criar_fonte_de_filmes()
    catalogo = fonte.buscar_por_titulo("")  # TODO (H3.2/H3.3): método próprio para listar o catálogo.
    contexto = ContextoRecomendacao(
        usuario_id=usuario_id,
        favoritos=favoritos,
        catalogo=catalogo,
        disponibilidade={filme.id: fonte.onde_assistir(filme.id) for filme in catalogo},
    )
    return criar_recomendador("favoritos").recomendar(contexto)


def planos_do_streaming(nome_streaming: str) -> list[Plano]:
    """Planos FICTÍCIOS de um streaming. TODO (H3.1): ler do banco."""
    streaming_id = sum(map(ord, nome_streaming))  # id estável só para os objetos de exemplo
    return [
        Plano(id=streaming_id * 10 + i, streaming_id=streaming_id, nome=nome, preco_mensal=preco)
        for i, (nome, preco) in enumerate(_PLANOS_EXEMPLO)
    ]
