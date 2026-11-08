import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from servicos.busca_servico import buscar_filmes, onde_assistir


def test_busca_ignora_maiusculas_e_acentos():
    titulos = [f.titulo for f in buscar_filmes("ANEIS")]
    assert titulos == ["O Senhor dos Anéis: A Sociedade do Anel"]


def test_busca_por_parte_do_titulo():
    titulos = {f.titulo for f in buscar_filmes("a ")}
    assert "A Origem" in titulos
    assert "A Viagem de Chihiro" in titulos


def test_busca_vazia_nao_retorna_nada():
    assert buscar_filmes("   ") == []


def test_busca_sem_resultado():
    assert buscar_filmes("filme que não existe") == []


def test_onde_assistir():
    assert onde_assistir(1) == ["Max", "Prime Video"]
    assert onde_assistir(9999) == []
