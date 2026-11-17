from pathlib import Path

from dados.conexao import CAMINHO_BANCO, obter_conexao
from fabricas import criar_fonte_de_filmes
from models.filme import Filme


def marcar_favorito(
    usuario_id: int, filme_id: int, caminho: Path = CAMINHO_BANCO
) -> None:
    """Grava o filme na lista de favoritos do usuário (H2.4)."""
    with obter_conexao(caminho) as conexao:
        conexao.execute(
            "INSERT OR IGNORE INTO favoritos (usuario_id, filme_id) VALUES (?, ?)",
            (usuario_id, filme_id),
        )


def eh_favorito(usuario_id: int, filme_id: int, caminho: Path = CAMINHO_BANCO) -> bool:
    """Informa se o filme já está na lista de favoritos do usuário."""
    with obter_conexao(caminho) as conexao:
        linha = conexao.execute(
            "SELECT 1 FROM favoritos WHERE usuario_id = ? AND filme_id = ?",
            (usuario_id, filme_id),
        ).fetchone()
    return linha is not None


def listar_favoritos(usuario_id: int, caminho: Path = CAMINHO_BANCO) -> list[Filme]:
    """Lê os ids favoritos e devolve os filmes correspondentes da fonte (H2.4)."""
    with obter_conexao(caminho) as conexao:
        ids = [
            linha["filme_id"]
            for linha in conexao.execute(
                """SELECT filme_id FROM favoritos
                   WHERE usuario_id = ?
                   ORDER BY criado_em DESC, rowid DESC""",
                (usuario_id,),
            ).fetchall()
        ]

    fonte = criar_fonte_de_filmes()
    filmes = (fonte.obter_filme(filme_id) for filme_id in ids)
    return [filme for filme in filmes if filme is not None]


def remover_favorito(
    usuario_id: int, filme_id: int, caminho: Path = CAMINHO_BANCO
) -> None:
    """Remove o filme da lista de favoritos do usuário (H9)."""
    with obter_conexao(caminho) as conexao:
        conexao.execute(
            "DELETE FROM favoritos WHERE usuario_id = ? AND filme_id = ?",
            (usuario_id, filme_id),
        )
