import json
import unicodedata
from pathlib import Path

from fontes.corpo_fonte import CorpoFonte
from models.filme import Filme

CAMINHO_PADRAO = Path(__file__).parent / "filmes_local.json"


def _normalizar(texto: str) -> str:
    """Minúsculas e sem acento, para 'ceu' achar 'Céu'."""
    decomposto = unicodedata.normalize("NFD", texto)
    sem_acento = "".join(c for c in decomposto if unicodedata.category(c) != "Mn")
    return sem_acento.casefold()


class FonteLocal(CorpoFonte):
    """Lê os filmes de um arquivo JSON que vem junto com o projeto."""

    def __init__(self, caminho: Path = CAMINHO_PADRAO):
        with open(caminho, encoding="utf-8") as arquivo:
            self._registros = json.load(arquivo)

    def buscar_por_titulo(self, titulo: str) -> list[Filme]:
        termo = _normalizar(titulo)
        return [
            self._para_filme(r)
            for r in self._registros
            if termo in _normalizar(r["titulo"])
        ]

    def obter_filme(self, filme_id: int) -> Filme | None:
        registro = self._achar(filme_id)
        return self._para_filme(registro) if registro else None

    def onde_assistir(self, filme_id: int) -> list[str]:
        registro = self._achar(filme_id)
        return list(registro.get("streamings", [])) if registro else []

    def _achar(self, filme_id: int) -> dict | None:
        for registro in self._registros:
            if registro["id"] == filme_id:
                return registro
        return None

    @staticmethod
    def _para_filme(registro: dict) -> Filme:
        return Filme(
            id=registro["id"],
            titulo=registro["titulo"],
            ano=registro.get("ano"),
            generos=registro.get("generos", []),
        )