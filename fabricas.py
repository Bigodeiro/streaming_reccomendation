"""Factory: decide qual Corpo (implementação) usar e devolve o Handle pronto.

A tela e os serviços pedem "o que querem" (um texto como "favoritos") e esta
fábrica entrega o objeto montado. Ninguém mais precisa saber qual classe
concreta está por baixo.
"""

from fontes.fonte_de_filmes import FonteDeFilmes
from fontes.fonte_local import FonteLocal

_CORPOS_FONTE = {
    "local": FonteLocal,
}


def criar_fonte_de_filmes(tipo: str = "local") -> FonteDeFilmes:
    if tipo not in _CORPOS_FONTE:
        raise ValueError(f"Tipo de fonte desconhecido: {tipo!r}")
    return FonteDeFilmes(_CORPOS_FONTE[tipo]())

"""Trocar para TMDB no futuro é criar fonte_tmdb.py,
registrar nesse dicionário e mudar o padrão do parâmetro.
O .gitkeep de fontes/ pode ser apagado, já que agora a pasta
tem arquivos.
"""