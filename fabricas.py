"""Factory: decide qual Corpo (implementação) usar e devolve o Handle pronto.

A tela e os serviços pedem "o que querem" (um texto como "favoritos") e esta
fábrica entrega o objeto montado. Ninguém mais precisa saber qual classe
concreta está por baixo.
"""

from fontes.fonte_de_filmes import FonteDeFilmes
from fontes.fonte_local import FonteLocal
from recomendacao.por_favoritos import RecomendaPorFavoritos
from recomendacao.recomendador import Recomendador

_CORPOS_FONTE = {
    "local": FonteLocal,
}

_CORPOS_RECOMENDACAO = {
    "favoritos": RecomendaPorFavoritos,
}


def criar_fonte_de_filmes(tipo: str = "local") -> FonteDeFilmes:
    if tipo not in _CORPOS_FONTE:
        raise ValueError(f"Tipo de fonte desconhecido: {tipo!r}")
    return FonteDeFilmes(_CORPOS_FONTE[tipo]())


def criar_recomendador(tipo: str = "favoritos") -> Recomendador:
    if tipo not in _CORPOS_RECOMENDACAO:
        raise ValueError(f"Tipo de recomendação desconhecido: {tipo!r}")
    return Recomendador(_CORPOS_RECOMENDACAO[tipo]())
