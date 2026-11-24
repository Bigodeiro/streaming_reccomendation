import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import atualizar_catalogo as api
from scripts import construcao_inicial as construcao


def _show(titulo: str, imdb: str, *, tipo: str = "movie", ano: int = 2008) -> dict:
    return {
        "itemType": "show",
        "showType": tipo,
        "id": imdb,
        "imdbId": imdb,
        "tmdbId": f"movie/{imdb[-3:]}",
        "title": titulo,
        "releaseYear": ano,
        "genres": [{"id": "drama", "name": "Drama"}],
        "streamingOptions": {"br": []},
    }


def _pagina(shows: list[dict], *, proximo: str | None = None) -> dict:
    return {"shows": shows, "hasMore": proximo is not None, "nextCursor": proximo}


def _buscador(paginas: dict[str | None, dict]):
    chamadas: list[str | None] = []

    def buscar(cursor: str | None):
        chamadas.append(cursor)
        if cursor not in paginas:
            raise AssertionError(f"Cursor inesperado: {cursor!r}")
        return paginas[cursor]

    return buscar, chamadas


def _catalogo_vazio() -> dict:
    return {"atualizado_em": "2026-01-01", "fonte": api.FONTE, "pais": "br", "filmes": []}


def _salvo(caminho: Path) -> dict:
    return json.loads(caminho.read_text(encoding="utf-8"))


def _argumentos() -> dict:
    return {
        "pais": "br",
        "ordem": construcao.ORDEM_PADRAO,
        "catalogos": construcao.catalogos_canonicos(),
    }


def test_processar_adiciona_filmes_e_salva_cursor_ate_o_fim(tmp_path):
    catalogo_path = tmp_path / "catalogo.json"
    progresso_path = tmp_path / "progresso.json"
    paginas = {
        None: _pagina(
            [_show("Filme A", "tt001"), _show("Série", "tt999", tipo="series")],
            proximo="cursor-2",
        ),
        "cursor-2": _pagina([_show("Filme B", "tt002")]),
    }
    buscar, chamadas = _buscador(paginas)

    resultado = construcao.processar(
        _catalogo_vazio(),
        {},
        buscar,
        caminho_catalogo=catalogo_path,
        caminho_progresso=progresso_path,
        **_argumentos(),
    )

    assert chamadas == [None, "cursor-2"]
    assert resultado.adicionados == 2
    assert resultado.ignorados == 1
    assert resultado.concluido
    assert [f["titulo"] for f in _salvo(catalogo_path)["filmes"]] == ["Filme A", "Filme B"]
    progresso = _salvo(progresso_path)
    assert progresso["cursor"] is None
    assert progresso["paginas"] == 2
    assert progresso["concluido"] is True


def test_quota_esgotada_pausa_e_mantem_o_cursor(tmp_path):
    catalogo_path = tmp_path / "catalogo.json"
    progresso_path = tmp_path / "progresso.json"
    progresso = construcao.progresso_vazio("br")

    def buscar(cursor):
        if cursor is None:
            return _pagina([_show("Filme A", "tt001")], proximo="cursor-2")
        raise api.ErroAPI("HTTP 429: quota exceeded", codigo=429, corpo="quota")

    resultado = construcao.processar(
        _catalogo_vazio(),
        progresso,
        buscar,
        caminho_catalogo=catalogo_path,
        caminho_progresso=progresso_path,
        **_argumentos(),
    )

    assert resultado.pausado
    assert [f["titulo"] for f in _salvo(catalogo_path)["filmes"]] == ["Filme A"]
    salvo = _salvo(progresso_path)
    assert salvo["cursor"] == "cursor-2"
    assert salvo["concluido"] is False


def test_segunda_execucao_retoma_e_nao_duplica(tmp_path):
    catalogo_path = tmp_path / "catalogo.json"
    progresso_path = tmp_path / "progresso.json"
    argumentos = _argumentos()
    paginas = {None: _pagina([_show("Filme A", "tt001")], proximo="cursor-2")}

    def buscar_com_quota(cursor):
        if cursor == "cursor-2":
            raise api.ErroAPI("quota exceeded", codigo=429, corpo="quota")
        return paginas[cursor]

    construcao.processar(
        _catalogo_vazio(),
        construcao.progresso_vazio("br"),
        buscar_com_quota,
        caminho_catalogo=catalogo_path,
        caminho_progresso=progresso_path,
        **argumentos,
    )

    # O filme A volta no início da página retomada: não pode ser adicionado de novo.
    buscar, chamadas = _buscador(
        {
            "cursor-2": _pagina(
                [_show("Filme A", "tt001"), _show("Filme B", "tt002")],
                proximo="cursor-3",
            ),
            "cursor-3": _pagina([]),
        }
    )
    resultado = construcao.processar(
        construcao.carregar_catalogo(catalogo_path, "br"),
        construcao.carregar_progresso(progresso_path),
        buscar,
        caminho_catalogo=catalogo_path,
        caminho_progresso=progresso_path,
        **argumentos,
    )

    assert chamadas[0] == "cursor-2"  # não começa do zero
    assert resultado.adicionados == 1
    assert resultado.duplicados == 1
    filmes = _salvo(catalogo_path)["filmes"]
    assert [f["titulo"] for f in filmes] == ["Filme A", "Filme B"]
    assert [f["id"] for f in filmes] == [1, 2]


def test_duplicata_por_id_externo_e_ignorada(tmp_path):
    catalogo_path = tmp_path / "catalogo.json"
    progresso_path = tmp_path / "progresso.json"
    catalogo = _catalogo_vazio()
    catalogo["filmes"] = [
        {
            "id": 1,
            "titulo": "Movie",
            "ano": 2000,
            "generos": ["Drama"],
            "streamings": [],
            "imdb_id": "tt111",
            "tmdb_id": "movie/111",
        }
    ]
    buscar, _ = _buscador({None: _pagina([_show("Movie again", "tt111")])})

    resultado = construcao.processar(
        catalogo,
        construcao.progresso_vazio("br"),
        buscar,
        caminho_catalogo=catalogo_path,
        caminho_progresso=progresso_path,
        **_argumentos(),
    )

    assert resultado.adicionados == 0
    assert resultado.duplicados == 1
    assert len(_salvo(catalogo_path)["filmes"]) == 1


def test_duplicata_dentro_da_mesma_pagina_e_ignorada(tmp_path):
    catalogo_path = tmp_path / "catalogo.json"
    progresso_path = tmp_path / "progresso.json"
    buscar, _ = _buscador(
        {
            None: _pagina(
                [_show(" mes titulo ", "tt001"), _show("Mes titulo", "tt001")]
            )
        }
    )

    resultado = construcao.processar(
        _catalogo_vazio(),
        construcao.progresso_vazio("br"),
        buscar,
        caminho_catalogo=catalogo_path,
        caminho_progresso=progresso_path,
        **_argumentos(),
    )

    assert resultado.adicionados == 1
    assert resultado.duplicados == 1
    assert len(_salvo(catalogo_path)["filmes"]) == 1


def test_progresso_antigo_sem_cursor_comeca_varredura_nova(tmp_path, caplog):
    caminho = tmp_path / "progresso.json"
    caminho.write_text(
        json.dumps({"pais": "br", "processados": [{"titulo": "Antigo"}]}),
        encoding="utf-8",
    )

    assert construcao.carregar_progresso(caminho) == {}
    assert "Progresso antigo" in caplog.text


def test_erro_de_limite_nao_confunde_chave_invalida():
    assert construcao.e_limite_de_tokens(
        api.ErroAPI("HTTP 429", codigo=429, corpo="rate limit")
    )
    assert construcao.e_limite_de_tokens(
        api.ErroAPI("HTTP 403", codigo=403, corpo="You exceeded your monthly quota")
    )
    assert not construcao.e_limite_de_tokens(
        api.ErroAPI("HTTP 401", codigo=401, corpo="provide a valid API Key")
    )


def test_status_mostra_cursor_e_totais(capsys):
    progresso = {
        "paginas": 3,
        "filmes_vistos": 60,
        "adicionados": 12,
        "cursor": "abc",
        "concluido": False,
        "ultimo_titulo": "The Godfather",
    }
    catalogo = _catalogo_vazio()
    catalogo["filmes"] = [{"id": 1, "titulo": "The Godfather"}]

    construcao._mostrar_status(progresso, catalogo)

    saida = capsys.readouterr().out
    assert "Filmes no catálogo: 1" in saida
    assert "País/ordem: br/original_title" in saida
    assert "Páginas processadas: 3" in saida
    assert "Adicionados pela varredura: 12" in saida
    assert "retoma no cursor salvo" in saida
    assert "Último título visto: The Godfather" in saida


def test_max_paginas_limita_chamadas(tmp_path):
    catalogo_path = tmp_path / "catalogo.json"
    progresso_path = tmp_path / "progresso.json"
    paginas = {
        None: _pagina([_show("Filme A", "tt001")], proximo="cursor-2"),
        "cursor-2": _pagina([_show("Filme B", "tt002")], proximo="cursor-3"),
    }
    buscar, chamadas = _buscador(paginas)

    resultado = construcao.processar(
        _catalogo_vazio(),
        construcao.progresso_vazio("br"),
        buscar,
        caminho_catalogo=catalogo_path,
        caminho_progresso=progresso_path,
        max_paginas=1,
        **_argumentos(),
    )

    assert chamadas == [None]
    assert resultado.paginas == 1
    assert _salvo(progresso_path)["cursor"] == "cursor-2"


def test_main_nao_pede_lista_de_titulos_e_usa_busca_por_filtros(
    tmp_path, monkeypatch, capsys
):
    catalogo_path = tmp_path / "catalogo.json"
    progresso_path = tmp_path / "progresso.json"
    monkeypatch.setenv(api.VARIAVEL_CHAVE, "chave-de-teste")

    chamadas: list[dict] = []

    def buscar_falso(chave, pais, cursor=None, ordem="original_title", catalogos=None):
        chamadas.append({"pais": pais, "cursor": cursor, "ordem": ordem})
        return _pagina([_show("Novo filme", "tt001")])

    monkeypatch.setattr(api, "buscar_por_filtros", buscar_falso)

    codigo = construcao.main(
        ["--catalogo", str(catalogo_path), "--progresso", str(progresso_path)]
    )

    assert codigo == 0
    assert chamadas == [{"pais": "br", "cursor": None, "ordem": "original_title"}]
    assert [f["titulo"] for f in _salvo(catalogo_path)["filmes"]] == ["Novo filme"]
    assert "varredura concluída" in capsys.readouterr().out


def test_todos_catalogos_omite_o_filtro_e_guarda_marcador(tmp_path, monkeypatch):
    catalogo_path = tmp_path / "catalogo.json"
    progresso_path = tmp_path / "progresso.json"
    monkeypatch.setenv(api.VARIAVEL_CHAVE, "chave-de-teste")
    catalogos_recebidos = []

    def buscar_falso(chave, pais, cursor=None, ordem="original_title", catalogos=None):
        catalogos_recebidos.append(catalogos)
        return _pagina([])

    monkeypatch.setattr(api, "buscar_por_filtros", buscar_falso)

    codigo = construcao.main(
        [
            "--catalogo",
            str(catalogo_path),
            "--progresso",
            str(progresso_path),
            "--todos-catalogos",
        ]
    )

    assert codigo == 0
    assert catalogos_recebidos == [None]
    assert _salvo(progresso_path)["catalogos"] == construcao.TODOS_CATALOGOS
