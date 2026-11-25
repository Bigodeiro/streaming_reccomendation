from datetime import date
from pathlib import Path

from dados.conexao import CAMINHO_BANCO, obter_conexao
from models.plano import Plano
from models.streaming import Streaming


def listar_streamings_com_planos(caminho: Path = CAMINHO_BANCO) -> list[Streaming]:
    """Todos os streamings cadastrados, cada um com seus planos, do mais barato ao mais caro."""
    with obter_conexao(caminho) as conexao:
        streamings = {
            linha["id"]: Streaming(id=linha["id"], nome=linha["nome"])
            for linha in conexao.execute("SELECT id, nome FROM streamings ORDER BY nome")
        }
        planos = conexao.execute(
            "SELECT id, streaming_id, nome, preco_mensal, conferido_em "
            "FROM planos ORDER BY preco_mensal"
        )
        for linha in planos:
            conferido_em = linha["conferido_em"]
            streamings[linha["streaming_id"]].planos.append(
                Plano(
                    id=linha["id"],
                    streaming_id=linha["streaming_id"],
                    nome=linha["nome"],
                    preco_mensal=linha["preco_mensal"],
                    conferido_em=date.fromisoformat(conferido_em) if conferido_em else None,
                )
            )
    return list(streamings.values())