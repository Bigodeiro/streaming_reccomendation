import json
import unicodedata
from pathlib import Path

from fontes.corpo_fonte import CorpoFonte
from fontes.streamings import normalizar_streamings
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
            dados = json.load(arquivo)
        # Formato novo: {"filmes": [...]}. O formato antigo (lista) ainda é aceito.
        self._registros = dados.get("filmes", []) if isinstance(dados, dict) else dados

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

    def streamings_do_filme(self, filme_id: int) -> list[str]:
        registro = self._achar(filme_id)
        if not registro:
            return []
        return normalizar_streamings(registro.get("streamings", []))

    def listar_filmes(self) -> list[Filme]:
        return [self._para_filme(registro) for registro in self._registros]

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