"""Vocabulário único dos streamings usados pelo catálogo.

Os ids abaixo são os mesmos devolvidos pela Streaming Availability API
(`netflix`, `prime`, `hbo`, ...). Eles também são o que a Pessoa A deve usar
como `slug` na tabela `streamings` da H3.1 — assim a fonte e o banco falam a
mesma língua sem depender de texto digitado à mão.

Qualquer serviço fora deste mapa é ignorado. É assim que Globoplay (ausente
da API no Brasil) desaparece do catálogo quando ele é regenerado.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# id da API -> nome de exibição (mesmo nome usado em ui/identidade.py).
SERVICOS_POR_ID: dict[str, str] = {
    "netflix": "Netflix",
    "prime": "Prime Video",
    "hbo": "Max",
    "disney": "Disney+",
    "apple": "Apple TV+",
    "paramount": "Paramount+",
    "crunchyroll": "Crunchyroll",
    "mubi": "Mubi",
}

# Nomes que aparecem na API ou em catálogos antigos e precisam virar o nome canônico.
_ALIASES: dict[str, str] = {
    "hbo max": "Max",
    "max": "Max",
    "amazon prime video": "Prime Video",
    "prime video": "Prime Video",
    "disney plus": "Disney+",
    "disney+": "Disney+",
    "apple tv": "Apple TV+",
    "apple tv+": "Apple TV+",
    "paramount plus": "Paramount+",
    "paramount+": "Paramount+",
    "crunchyroll": "Crunchyroll",
    "mubi": "Mubi",
    "netflix": "Netflix",
}


def normalizar_streaming(identificador: str, *, avisar: bool = True) -> str | None:
    """Devolve o nome canônico de um id ou nome de serviço; None se não existir."""
    texto = identificador.strip()
    if not texto:
        return None

    chave = texto.casefold()
    if chave in SERVICOS_POR_ID:
        return SERVICOS_POR_ID[chave]
    if chave in _ALIASES:
        return _ALIASES[chave]
    for nome in SERVICOS_POR_ID.values():
        if nome.casefold() == chave:
            return nome

    if avisar:
        logger.warning("Streaming %r não está no mapa canônico e foi ignorado.", identificador)
    return None


def normalizar_streamings(identificadores: list[str]) -> list[str]:
    """Normaliza uma lista, removendo duplicatas e serviços desconhecidos."""
    nomes: list[str] = []
    for identificador in identificadores:
        nome = normalizar_streaming(str(identificador))
        if nome and nome not in nomes:
            nomes.append(nome)
    return nomes


def streamings_canonicos() -> list[tuple[str, str]]:
    """Pares (slug, nome) para popular a tabela `streamings` da H3.1."""
    return sorted(SERVICOS_POR_ID.items())


def catalogos_canonicos() -> str:
    """Lista de catálogos da API para varrer só os streamings do mapa.

    O formato é `id.subscription`, aceito por `/shows/search/filters`. Assim a
    varredura não gasta token com serviços que seriam descartados depois.
    """
    return ",".join(f"{servico}.subscription" for servico in sorted(SERVICOS_POR_ID))
