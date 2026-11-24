"""Varredura incremental da base de filmes, sem lista manual de títulos.

Usa `/shows/search/filters` da Streaming Availability API para percorrer o
catálogo do país, acrescentando ao `fontes/filmes_local.json` apenas filmes que
ainda não estão nele. O ponto de retomada (cursor da paginação) fica em
`scripts/progresso_construcao.json`; quando a cota acaba, o progresso é salvo e
a próxima execução continua de onde parou.

Uso:
    python -m scripts.construcao_inicial --status
    python -m scripts.construcao_inicial
    python -m scripts.construcao_inicial --max-paginas 5
    python -m scripts.construcao_inicial --reiniciar-progresso
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from fontes.streamings import catalogos_canonicos  # noqa: E402
from scripts import atualizar_catalogo as api  # noqa: E402

CAMINHO_PROGRESSO = RAIZ / "scripts" / "progresso_construcao.json"
ORDEM_PADRAO = "original_title"
TODOS_CATALOGOS = "todos"
ORDENS = (
    "original_title",
    "release_date",
    "rating",
    "popularity_alltime",
    "popularity_1year",
    "popularity_1month",
    "popularity_1week",
)
logger = logging.getLogger(__name__)

BuscadorPaginado = Callable[[str | None], dict[str, Any]]

# Palavras que aparecem nas mensagens da API quando a cota/token acaba.
_PALAVRAS_LIMITE = (
    "quota",
    "limit",
    "token",
    "credit",
    "usage",
    "rate limit",
    "request limit",
    "daily",
    "monthly",
    "plan",
)


@dataclass
class Resultado:
    paginas: int = 0
    filmes_vistos: int = 0
    adicionados: int = 0
    duplicados: int = 0
    ignorados: int = 0
    pausado: bool = False
    concluido: bool = False
    motivo: str = ""

    def resumo(self) -> str:
        partes = [
            f"{self.paginas} páginas consultadas",
            f"{self.filmes_vistos} filmes vistos",
            f"{self.adicionados} adicionados",
            f"{self.duplicados} duplicados ignorados",
        ]
        if self.ignorados:
            partes.append(f"{self.ignorados} itens não-filme ignorados")
        if self.pausado:
            partes.append("pausado: cota da API esgotada")
        elif self.concluido:
            partes.append("varredura concluída")
        return ", ".join(partes)


def progresso_vazio(
    pais: str, ordem: str = ORDEM_PADRAO, catalogos: str | None = None
) -> dict[str, Any]:
    """Estrutura inicial do arquivo de retomada."""
    return {
        "atualizado_em": date.today().isoformat(),
        "pais": pais,
        "ordem": ordem,
        "catalogos": catalogos or TODOS_CATALOGOS,
        "cursor": None,
        "paginas": 0,
        "filmes_vistos": 0,
        "adicionados": 0,
        "concluido": False,
    }


def carregar_progresso(caminho: Path) -> dict[str, Any]:
    """Lê o progresso; aceita arquivos antigos sem cursor como nova varredura."""
    if not caminho.exists():
        return {}
    with open(caminho, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    if not isinstance(dados, dict):
        raise ValueError(f"Arquivo de progresso inválido: {caminho}")
    if "cursor" not in dados:
        logger.warning(
            "Progresso antigo detectado em %s; iniciando varredura do zero.", caminho
        )
        return {}
    return dados


def salvar_progresso(progresso: dict[str, Any], caminho: Path) -> None:
    progresso["atualizado_em"] = date.today().isoformat()
    api.gravar_catalogo(progresso, caminho)


def carregar_catalogo(caminho: Path, pais: str) -> dict[str, Any]:
    """Carrega o catálogo atual para acrescentar filmes sem apagar os existentes."""
    if not caminho.exists():
        return {
            "atualizado_em": date.today().isoformat(),
            "fonte": api.FONTE,
            "pais": pais,
            "filmes": [],
        }
    with open(caminho, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    if isinstance(dados, list):
        dados = {"filmes": dados}
    if not isinstance(dados, dict) or not isinstance(dados.get("filmes"), list):
        raise ValueError(f"Catálogo inválido: {caminho}")
    dados.setdefault("fonte", api.FONTE)
    dados.setdefault("pais", pais)
    return dados


def chaves_do_registro(registro: dict[str, Any]) -> set[tuple[str, ...]]:
    """Ids externos e título+ano identificam o mesmo filme entre execuções."""
    chaves: set[tuple[str, ...]] = set()
    for campo in ("imdb_id", "tmdb_id"):
        valor = str(registro.get(campo) or "").strip().casefold()
        if valor:
            chaves.add((campo, valor))
    titulo = api.normalizar_titulo(str(registro.get("titulo", "")))
    if titulo:
        chaves.add(("titulo+ano", titulo, str(registro.get("ano") or "")))
    return chaves


def chaves_do_catalogo(catalogo: dict[str, Any]) -> set[tuple[str, ...]]:
    chaves: set[tuple[str, ...]] = set()
    for filme in catalogo.get("filmes", []):
        chaves |= chaves_do_registro(filme)
    return chaves


def proximo_id(catalogo: dict[str, Any]) -> int:
    ids = [
        int(filme["id"])
        for filme in catalogo.get("filmes", [])
        if str(filme.get("id", "")).isdigit()
    ]
    return max(ids, default=0) + 1


def e_limite_de_tokens(erro: api.ErroAPI) -> bool:
    """Reconhece quotas esgotadas sem confundir com chave inválida (401)."""
    if erro.codigo in (402, 429):
        return True
    if erro.codigo == 401:
        return False
    texto = f"{erro.corpo} {erro}".casefold()
    return any(palavra in texto for palavra in _PALAVRAS_LIMITE)


def _ultimo_titulo(shows: list[dict[str, Any]]) -> str | None:
    for show in reversed(shows):
        titulo = show.get("title")
        if titulo:
            return str(titulo)
    return None


def salvar_tudo(
    catalogo: dict[str, Any],
    progresso: dict[str, Any],
    caminho_catalogo: Path,
    caminho_progresso: Path,
    pais: str,
) -> None:
    catalogo["atualizado_em"] = date.today().isoformat()
    catalogo["pais"] = pais
    api.gravar_catalogo(catalogo, caminho_catalogo)
    salvar_progresso(progresso, caminho_progresso)


def processar(
    catalogo: dict[str, Any],
    progresso: dict[str, Any],
    buscar: BuscadorPaginado,
    *,
    pais: str,
    ordem: str = ORDEM_PADRAO,
    catalogos: str | None = None,
    caminho_catalogo: Path | None = None,
    caminho_progresso: Path | None = None,
    gravar: bool = True,
    max_novos: int | None = None,
    max_paginas: int | None = None,
) -> Resultado:
    """Varre páginas da API, acumulando filmes novos e salvando o cursor."""
    progresso.update(
        {
            "pais": pais,
            "ordem": ordem,
            "catalogos": catalogos or TODOS_CATALOGOS,
        }
    )
    progresso.setdefault("cursor", None)
    progresso.setdefault("paginas", 0)
    progresso.setdefault("filmes_vistos", 0)
    progresso.setdefault("adicionados", 0)

    resultado = Resultado()
    existentes = chaves_do_catalogo(catalogo)
    paginas_anteriores = int(progresso["paginas"])
    vistos_anteriores = int(progresso["filmes_vistos"])
    adicionados_anteriores = int(progresso["adicionados"])

    def salvar() -> None:
        if gravar and caminho_catalogo and caminho_progresso:
            salvar_tudo(catalogo, progresso, caminho_catalogo, caminho_progresso, pais)

    while True:
        if max_paginas is not None and resultado.paginas >= max_paginas:
            break
        if max_novos is not None and resultado.adicionados >= max_novos:
            break

        try:
            resposta = buscar(progresso.get("cursor"))
        except api.ErroAPI as erro:
            if not e_limite_de_tokens(erro):
                raise
            # As páginas anteriores já foram gravadas; este cursor ainda não
            # avançou, então a próxima execução repete exatamente esta consulta.
            resultado.pausado = True
            resultado.motivo = str(erro)
            salvar()
            logger.warning("Cota da API esgotada. Progresso salvo no cursor atual.")
            return resultado

        shows = resposta.get("shows", [])
        if not isinstance(shows, list):
            raise ValueError("Resposta da API sem lista de shows")
        resultado.paginas += 1

        for show in shows:
            if show.get("showType") != "movie":
                resultado.ignorados += 1
                continue
            resultado.filmes_vistos += 1
            registro = api.para_registro(show, proximo_id(catalogo), pais)
            novas_chaves = chaves_do_registro(registro)
            if novas_chaves & existentes:
                resultado.duplicados += 1
                continue
            catalogo.setdefault("filmes", []).append(registro)
            existentes |= novas_chaves
            resultado.adicionados += 1
            logger.info("Adicionado: %s", registro["titulo"])

        progresso["paginas"] = paginas_anteriores + resultado.paginas
        progresso["filmes_vistos"] = vistos_anteriores + resultado.filmes_vistos
        progresso["adicionados"] = adicionados_anteriores + resultado.adicionados
        titulo = _ultimo_titulo(shows)
        if titulo:
            progresso["ultimo_titulo"] = titulo

        tem_mais = bool(resposta.get("hasMore"))
        proximo_cursor = resposta.get("nextCursor")
        if tem_mais and proximo_cursor:
            progresso["cursor"] = proximo_cursor
            progresso["concluido"] = False
            salvar()
            continue
        if tem_mais and not proximo_cursor:
            resultado.pausado = True
            resultado.motivo = (
                "A API indicou mais páginas, mas não devolveu nextCursor."
            )
            salvar()
            logger.warning("%s", resultado.motivo)
            return resultado

        progresso["cursor"] = None
        progresso["concluido"] = True
        resultado.concluido = True
        salvar()
        break

    salvar()
    return resultado


def _mostrar_status(progresso: dict[str, Any], catalogo: dict[str, Any]) -> None:
    print(f"Filmes no catálogo: {len(catalogo.get('filmes', []))}")
    print(
        f"País/ordem: {progresso.get('pais', api.PAIS_PADRAO)}/"
        f"{progresso.get('ordem', ORDEM_PADRAO)}"
    )
    print(f"Catálogos: {progresso.get('catalogos') or catalogos_canonicos()}")
    print(f"Páginas processadas: {progresso.get('paginas', 0)}")
    print(f"Filmes vistos na varredura: {progresso.get('filmes_vistos', 0)}")
    print(f"Adicionados pela varredura: {progresso.get('adicionados', 0)}")
    if progresso.get("concluido"):
        print("Varredura: concluída")
    elif progresso.get("cursor"):
        print("Varredura: pausada; retoma no cursor salvo")
    else:
        print("Varredura: ainda não iniciada")
    if progresso.get("ultimo_titulo"):
        print(f"Último título visto: {progresso['ultimo_titulo']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalogo", type=Path, default=api.CAMINHO_SAIDA)
    parser.add_argument("--progresso", type=Path, default=CAMINHO_PROGRESSO)
    parser.add_argument("--pais", default=api.PAIS_PADRAO)
    parser.add_argument("--ordem", choices=ORDENS, default=ORDEM_PADRAO)
    parser.add_argument(
        "--catalogos",
        help="catálogos da API (ex.: netflix.subscription,prime.subscription). "
        "Padrão: streamings canônicos de assinatura.",
    )
    parser.add_argument(
        "--todos-catalogos",
        action="store_true",
        help="varre todos os catálogos do país, inclusive aluguel, compra e canais",
    )
    parser.add_argument("--max-novos", type=int, help="limita filmes novos nesta execução")
    parser.add_argument("--max-paginas", type=int, help="limita páginas nesta execução")
    parser.add_argument("--dry-run", action="store_true", help="não grava nada")
    parser.add_argument("--status", action="store_true", help="mostra o progresso e sai")
    parser.add_argument(
        "--reiniciar-progresso",
        action="store_true",
        help="descarta o cursor e começa a varredura do zero",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    progresso = carregar_progresso(args.progresso)
    if args.status:
        _mostrar_status(progresso, carregar_catalogo(args.catalogo, args.pais))
        return 0

    if args.todos_catalogos and args.catalogos:
        parser.error("Use --catalogos ou --todos-catalogos, não ambos")
    catalogos = None if args.todos_catalogos else (args.catalogos or catalogos_canonicos())
    valor_catalogos = catalogos or TODOS_CATALOGOS
    if not args.reiniciar_progresso:
        for campo, valor, rotulo in (
            ("pais", args.pais, "--pais"),
            ("ordem", args.ordem, "--ordem"),
            ("catalogos", valor_catalogos, "--catalogos/--todos-catalogos"),
        ):
            anterior = progresso.get(campo)
            if anterior and anterior != valor:
                parser.error(
                    f"O progresso usa {campo}={anterior!r}; use {rotulo}={anterior!r} "
                    "ou --reiniciar-progresso"
                )
    else:
        progresso = progresso_vazio(args.pais, args.ordem, catalogos)
        if not args.dry_run:
            salvar_progresso(progresso, args.progresso)

    if not progresso:
        progresso = progresso_vazio(args.pais, args.ordem, catalogos)

    chave = os.getenv(api.VARIAVEL_CHAVE)
    if not chave:
        parser.error(f"Defina {api.VARIAVEL_CHAVE} com sua chave da Streaming Availability API")

    resultado = processar(
        carregar_catalogo(args.catalogo, args.pais),
        progresso,
        lambda cursor: api.buscar_por_filtros(
            chave, args.pais, cursor=cursor, ordem=args.ordem, catalogos=catalogos
        ),
        pais=args.pais,
        ordem=args.ordem,
        catalogos=catalogos,
        caminho_catalogo=args.catalogo,
        caminho_progresso=args.progresso,
        gravar=not args.dry_run,
        max_novos=args.max_novos,
        max_paginas=args.max_paginas,
    )

    print(resultado.resumo())
    if resultado.pausado:
        if resultado.motivo:
            print(f"Detalhe: {resultado.motivo}")
        print("Rode o script de novo quando os tokens voltarem; ele retoma do cursor salvo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
