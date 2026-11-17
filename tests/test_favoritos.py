import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dados.carga_inicial import garantir_usuario_demo
from dados.conexao import inicializar_banco
from servicos.favoritos_servico import (
    eh_favorito,
    listar_favoritos,
    marcar_favorito,
    remover_favorito,
)


def _banco_de_teste(tmp_path: Path) -> tuple[int, Path]:
    caminho = tmp_path / "favoritos.db"
    inicializar_banco(caminho)
    usuario_id, _ = garantir_usuario_demo(caminho)
    return usuario_id, caminho


def test_marcar_e_listar_favoritos(tmp_path):
    usuario_id, caminho = _banco_de_teste(tmp_path)

    marcar_favorito(usuario_id, 1, caminho)
    marcar_favorito(usuario_id, 3, caminho)

    titulos = [filme.titulo for filme in listar_favoritos(usuario_id, caminho)]
    assert titulos == ["A Origem", "Matrix"]


def test_marcar_favorito_duplicado_nao_repete(tmp_path):
    usuario_id, caminho = _banco_de_teste(tmp_path)

    marcar_favorito(usuario_id, 2, caminho)
    marcar_favorito(usuario_id, 2, caminho)

    assert [f.id for f in listar_favoritos(usuario_id, caminho)] == [2]


def test_eh_favorito(tmp_path):
    usuario_id, caminho = _banco_de_teste(tmp_path)

    assert not eh_favorito(usuario_id, 5, caminho)
    marcar_favorito(usuario_id, 5, caminho)
    assert eh_favorito(usuario_id, 5, caminho)
    assert not eh_favorito(usuario_id, 6, caminho)


def test_remover_favorito(tmp_path):
    usuario_id, caminho = _banco_de_teste(tmp_path)

    marcar_favorito(usuario_id, 1, caminho)
    marcar_favorito(usuario_id, 3, caminho)
    remover_favorito(usuario_id, 1, caminho)

    assert [f.id for f in listar_favoritos(usuario_id, caminho)] == [3]


def test_listar_favoritos_ignora_ids_fora_do_catalogo(tmp_path):
    usuario_id, caminho = _banco_de_teste(tmp_path)

    marcar_favorito(usuario_id, 9999, caminho)
    marcar_favorito(usuario_id, 8, caminho)

    assert [f.titulo for f in listar_favoritos(usuario_id, caminho)] == ["Toy Story"]
