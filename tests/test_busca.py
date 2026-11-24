import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fabricas import criar_fonte_de_filmes
from fontes.fonte_local import FonteLocal
from servicos.busca_servico import buscar_filmes, onde_assistir, streamings_do_filme


def test_busca_ignora_maiusculas_e_acentos():
    titulos = [f.titulo for f in buscar_filmes("PHILOSOPHER")]
    assert titulos == ["Harry Potter and the Philosopher's Stone"]


def test_busca_por_parte_do_titulo():
    titulos = {f.titulo for f in buscar_filmes("dark knight")}
    assert {"The Dark Knight", "The Dark Knight Rises"} <= titulos


def test_busca_vazia_nao_retorna_nada():
    assert buscar_filmes("   ") == []


def test_busca_sem_resultado():
    assert buscar_filmes("filme que não existe") == []


def test_streamings_do_filme_devolve_disponibilidade_da_fonte():
    assert streamings_do_filme(2) == ["Prime Video", "Max"]
    assert streamings_do_filme(1) == ["Paramount+"]
    assert streamings_do_filme(9999) == []
    assert onde_assistir(2) == streamings_do_filme(2)


def test_listar_filmes_devolve_o_catalogo_com_generos():
    filmes = criar_fonte_de_filmes().listar_filmes()
    assert len(filmes) > 3
    assert all(filme.generos for filme in filmes)
    assert len({filme.id for filme in filmes}) == len(filmes)


def test_fonte_normaliza_nomes_e_descarta_streamings_fora_do_mapa(tmp_path):
    caminho = tmp_path / "catalogo.json"
    caminho.write_text(
        json.dumps(
            {
                "filmes": [
                    {
                        "id": 1,
                        "titulo": "Exemplo",
                        "ano": 2020,
                        "generos": ["Drama"],
                        "streamings": ["hbo max", "Globoplay", "prime", "Max"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    fonte = FonteLocal(caminho)
    assert fonte.streamings_do_filme(1) == ["Max", "Prime Video"]
    assert fonte.listar_filmes()[0].generos == ["Drama"]
