import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import atualizar_catalogo as api


def _show(titulo: str, *, ano: int = 2008, opcoes=None) -> dict:
    return {
        "itemType": "show",
        "showType": "movie",
        "id": "1",
        "imdbId": "tt0000001",
        "tmdbId": "movie/1",
        "title": titulo,
        "releaseYear": ano,
        "genres": [{"id": "crime", "name": "Crime"}, {"id": "drama", "name": "Drama"}],
        "streamingOptions": {"br": opcoes or []},
    }


def _opcao(servico_id: str, nome: str, tipo: str = "subscription") -> dict:
    return {"type": tipo, "service": {"id": servico_id, "name": nome}}


def test_ler_titulos_ignora_comentarios_e_linhas_vazias(tmp_path):
    caminho = tmp_path / "titulos.txt"
    caminho.write_text("# comentário\n\nThe Godfather\n  The Dark Knight  \n", encoding="utf-8")

    assert api.ler_titulos(caminho) == ["The Godfather", "The Dark Knight"]


def test_normalizar_titulo_ignora_acentos_e_pontuacao():
    assert api.normalizar_titulo("Batman & Robin") == api.normalizar_titulo("batman robin")


def test_escolher_filme_prefere_titulo_exato():
    resultados = [_show("Batman Returns"), _show("Batman", ano=1989)]

    assert api.escolher_filme(resultados, "BATMAN")["title"] == "Batman"
    assert api.escolher_filme(resultados, "returns")["title"] == "Batman Returns"
    assert api.escolher_filme(resultados, "filme que não existe") is None


def test_streamings_do_show_so_aceita_assinatura_e_nomes_do_mapa(caplog):
    show = _show(
        "Exemplo",
        opcoes=[
            _opcao("hbo", "HBO Max"),
            _opcao("globoplay", "Globoplay"),
            _opcao("apple", "Apple TV", "rent"),
            _opcao("prime", "Prime Video"),
            _opcao("hbo", "HBO Max"),  # duplicata
        ],
    )

    assert api.streamings_do_show(show, "br") == ["Max", "Prime Video"]
    assert "Globoplay" in caplog.text


def test_para_registro_usa_formato_do_catalogo(tmp_path):
    show = _show("The Godfather", ano=1972, opcoes=[_opcao("paramount", "Paramount+")])

    registro = api.para_registro(show, 7, "br")

    assert registro == {
        "id": 7,
        "titulo": "The Godfather",
        "ano": 1972,
        "generos": ["Crime", "Drama"],
        "streamings": ["Paramount+"],
        "imdb_id": "tt0000001",
        "tmdb_id": "movie/1",
    }


def test_montar_catalogo_gera_ids_sequenciais_e_metadados():
    def buscar(titulo):
        return [_show(titulo)]

    catalogo = api.montar_catalogo(["Um filme", "Outro filme"], buscar, pais="br")

    assert catalogo["atualizado_em"] == date.today().isoformat()
    assert catalogo["pais"] == "br"
    assert catalogo["fonte"] == "Streaming Availability API v4"
    assert [filme["id"] for filme in catalogo["filmes"]] == [1, 2]
    assert [filme["titulo"] for filme in catalogo["filmes"]] == ["Um filme", "Outro filme"]


def test_montar_catalogo_ignora_titulo_sem_resultado(caplog):
    def buscar(titulo):
        return [] if titulo == "Inexistente" else [_show(titulo)]

    catalogo = api.montar_catalogo(["Inexistente", "The Godfather"], buscar)

    assert [filme["titulo"] for filme in catalogo["filmes"]] == ["The Godfather"]
    assert "Inexistente" in caplog.text


def test_gravar_catalogo_escreve_json(tmp_path):
    saida = tmp_path / "catalogo" / "filmes_local.json"
    catalogo = api.montar_catalogo(["The Godfather"], lambda titulo: [_show(titulo)])

    api.gravar_catalogo(catalogo, saida)

    assert json.loads(saida.read_text(encoding="utf-8")) == catalogo


def test_main_dry_run_nao_sobrescreve_o_arquivo(tmp_path, monkeypatch, capsys):
    titulos = tmp_path / "titulos.txt"
    titulos.write_text("The Godfather\n", encoding="utf-8")
    saida = tmp_path / "filmes_local.json"
    monkeypatch.setenv(api.VARIAVEL_CHAVE, "chave-de-teste")
    monkeypatch.setattr(
        api, "buscar_por_titulo", lambda titulo, chave, pais="br": [_show(titulo)]
    )

    codigo = api.main(
        ["--titulos", str(titulos), "--saida", str(saida), "--dry-run"]
    )

    assert codigo == 0
    assert not saida.exists()
    assert '"titulo": "The Godfather"' in capsys.readouterr().out


def test_buscar_por_filtros_manda_cursor_e_catalogos(monkeypatch):
    capturado = {}

    def falso_get_json(caminho, parametros, chave):
        capturado.update(caminho=caminho, parametros=parametros, chave=chave)
        return {"shows": [_show("The Godfather")], "hasMore": True, "nextCursor": "abc"}

    monkeypatch.setattr(api, "_get_json", falso_get_json)

    resposta = api.buscar_por_filtros(
        "minha-chave", pais="br", cursor="abc", ordem="release_date", catalogos="netflix.subscription"
    )

    assert resposta["nextCursor"] == "abc"
    assert capturado["caminho"] == "shows/search/filters"
    assert capturado["chave"] == "minha-chave"
    assert capturado["parametros"] == {
        "country": "br",
        "show_type": "movie",
        "order_by": "release_date",
        "cursor": "abc",
        "catalogs": "netflix.subscription",
    }
