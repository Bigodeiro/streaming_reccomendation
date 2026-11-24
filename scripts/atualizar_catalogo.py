"""Gera `fontes/filmes_local.json` a partir da Streaming Availability API.

Uso:
    STREAMING_AVAILABILITY_API_KEY=... python -m scripts.atualizar_catalogo
    python -m scripts.atualizar_catalogo --dry-run

A chave vai na variável de ambiente (ou `.env`, nunca no Git). O script usa
apenas o endpoint de busca por título: a resposta já traz gêneros, ano, ids
externos e a disponibilidade no país escolhido. Só entram no catálogo opções
do tipo `subscription` — aluguel, compra e canais addon ficam de fora.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Iterable
from datetime import date
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

load_dotenv()

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from fontes.streamings import normalizar_streaming  # noqa: E402

API_BASE = "https://api.movieofthenight.com/v4"
VARIAVEL_CHAVE = "STREAMING_AVAILABILITY_API_KEY"
CAMINHO_TITULOS = RAIZ / "scripts" / "titulos_para_buscar.txt"
CAMINHO_SAIDA = RAIZ / "fontes" / "filmes_local.json"
PAIS_PADRAO = "br"
FONTE = "Streaming Availability API v4"

logger = logging.getLogger(__name__)

Buscador = Callable[[str], list[dict[str, Any]]]


class ErroAPI(RuntimeError):
    """Falha ao consultar a API (chave inválida, quota, rede, etc.)."""

    def __init__(
        self, mensagem: str, *, codigo: int | None = None, corpo: str = ""
    ) -> None:
        super().__init__(mensagem)
        self.codigo = codigo
        self.corpo = corpo


def ler_titulos(caminho: Path) -> list[str]:
    """Lê a lista de títulos, ignorando comentários e linhas vazias."""
    with open(caminho, encoding="utf-8") as arquivo:
        return [linha.strip() for linha in arquivo if linha.strip() and not linha.lstrip().startswith("#")]


def normalizar_titulo(texto: str) -> str:
    """Minúsculas, sem acento e sem pontuação, para comparar títulos da API."""
    decomposto = unicodedata.normalize("NFD", texto)
    sem_acento = "".join(c for c in decomposto if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", sem_acento.casefold()).strip()


def escolher_filme(resultados: Iterable[dict[str, Any]], titulo: str) -> dict[str, Any] | None:
    """Prefere o filme com título exato; aceita um título que contenha a busca."""
    alvo = normalizar_titulo(titulo)
    filmes = [item for item in resultados if item.get("showType") == "movie"]
    if not filmes:
        return None

    for filme in filmes:
        if normalizar_titulo(str(filme.get("title", ""))) == alvo:
            return filme
    for filme in filmes:
        encontrado = normalizar_titulo(str(filme.get("title", "")))
        if alvo in encontrado or encontrado in alvo:
            return filme
    return None


def streamings_do_show(show: dict[str, Any], pais: str) -> list[str]:
    """Nomes canônicos dos streamings de assinatura disponíveis em `pais`."""
    opcoes = show.get("streamingOptions", {}).get(pais, [])
    nomes: list[str] = []
    for opcao in opcoes:
        if opcao.get("type") != "subscription":
            continue
        servico = opcao.get("service") or {}
        nome = normalizar_streaming(str(servico.get("id", "")), avisar=False)
        if nome is None:
            nome = normalizar_streaming(str(servico.get("name", "")))
        if nome and nome not in nomes:
            nomes.append(nome)
    return nomes


def para_registro(show: dict[str, Any], filme_id: int, pais: str) -> dict[str, Any]:
    """Converte um `show` da API no formato usado por `filmes_local.json`."""
    return {
        "id": filme_id,
        "titulo": show.get("title", ""),
        "ano": show.get("releaseYear"),
        "generos": [
            genero["name"] for genero in show.get("genres", []) if genero.get("name")
        ],
        "streamings": streamings_do_show(show, pais),
        "imdb_id": show.get("imdbId"),
        "tmdb_id": show.get("tmdbId"),
    }


def montar_catalogo(
    titulos: Iterable[str], buscar: Buscador, pais: str = PAIS_PADRAO
) -> dict[str, Any]:
    """Busca cada título e devolve o catálogo pronto para gravação."""
    filmes: list[dict[str, Any]] = []
    for titulo in titulos:
        resultados = buscar(titulo)
        show = escolher_filme(resultados, titulo)
        if show is None:
            logger.warning("Nenhum filme encontrado para %r; título ignorado.", titulo)
            continue
        filmes.append(para_registro(show, len(filmes) + 1, pais))

    return {
        "atualizado_em": date.today().isoformat(),
        "fonte": FONTE,
        "pais": pais,
        "filmes": filmes,
    }


def _get_json(caminho: str, parametros: dict[str, str], chave: str) -> Any:
    """GET autenticado na API, com X-API-Key no header."""
    url = f"{API_BASE}/{caminho.lstrip('/')}?{urllib.parse.urlencode(parametros)}"
    requisicao = urllib.request.Request(
        url,
        headers={"X-API-Key": chave, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(requisicao, timeout=30) as resposta:
            return json.load(resposta)
    except urllib.error.HTTPError as erro:
        corpo = erro.read().decode("utf-8", errors="replace")
        raise ErroAPI(
            f"API devolveu HTTP {erro.code} para {url}: {corpo[:200]}",
            codigo=erro.code,
            corpo=corpo,
        ) from erro
    except urllib.error.URLError as erro:
        raise ErroAPI(f"Não foi possível acessar a API: {erro.reason}") from erro


def buscar_por_titulo(
    titulo: str, chave: str, pais: str = PAIS_PADRAO
) -> list[dict[str, Any]]:
    """Consulta `/shows/search/title` filtrando filmes do país escolhido."""
    resposta = _get_json(
        "shows/search/title",
        {"title": titulo, "country": pais, "show_type": "movie"},
        chave,
    )
    if not isinstance(resposta, list):
        raise ErroAPI(f"Resposta inesperada da API para {titulo!r}")
    return resposta


def buscar_por_filtros(
    chave: str,
    pais: str = PAIS_PADRAO,
    cursor: str | None = None,
    ordem: str = "original_title",
    catalogos: str | None = None,
) -> dict[str, Any]:
    """Consulta `/shows/search/filters`, paginando sem precisar de títulos.

    Sem `catalogos`, a API varre todos os serviços do país. Com a lista padrão
    dos streamings canônicos, evita trazer mídia que seria descartada depois.
    """
    parametros: dict[str, str] = {
        "country": pais,
        "show_type": "movie",
        "order_by": ordem,
    }
    if cursor:
        parametros["cursor"] = cursor
    if catalogos:
        parametros["catalogs"] = catalogos

    resposta = _get_json("shows/search/filters", parametros, chave)
    if not isinstance(resposta, dict) or not isinstance(resposta.get("shows"), list):
        raise ErroAPI("Resposta inesperada da API em /shows/search/filters")
    return resposta


def gravar_catalogo(catalogo: dict[str, Any], caminho: Path) -> None:
    """Escreve o JSON por completo, trocando o arquivo só depois de válido."""
    texto = json.dumps(catalogo, ensure_ascii=False, indent=2) + "\n"
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=caminho.parent, delete=False, suffix=".tmp"
    ) as temporario:
        temporario.write(texto)
        nome_temporario = Path(temporario.name)
    nome_temporario.replace(caminho)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--titulos", type=Path, default=CAMINHO_TITULOS)
    parser.add_argument("--saida", type=Path, default=CAMINHO_SAIDA)
    parser.add_argument("--pais", default=PAIS_PADRAO)
    parser.add_argument(
        "--dry-run", action="store_true", help="mostra o JSON sem sobrescrever o arquivo"
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    chave = os.getenv(VARIAVEL_CHAVE)
    if not chave:
        parser.error(f"Defina {VARIAVEL_CHAVE} com sua chave da Streaming Availability API")

    titulos = ler_titulos(args.titulos)
    catalogo = montar_catalogo(
        titulos,
        lambda titulo: buscar_por_titulo(titulo, chave, args.pais),
        args.pais,
    )

    if args.dry_run:
        print(json.dumps(catalogo, ensure_ascii=False, indent=2))
        return 0

    gravar_catalogo(catalogo, args.saida)
    print(f"{len(catalogo['filmes'])} filmes gravados em {args.saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
