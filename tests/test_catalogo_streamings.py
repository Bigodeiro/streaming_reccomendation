import json
from pathlib import Path

from dados.carga_inicial import garantir_streamings_e_planos
from dados.conexao import inicializar_banco, obter_conexao

CATALOGO = Path(__file__).resolve().parent.parent / "fontes" / "filmes_local.json"


def test_todo_streaming_do_catalogo_esta_cadastrado(tmp_path):
    banco = tmp_path / "teste.db"
    inicializar_banco(banco)
    garantir_streamings_e_planos(banco)

    with obter_conexao(banco) as conexao:
        cadastrados = {l["nome"] for l in conexao.execute("SELECT nome FROM streamings")}

    dados = json.loads(CATALOGO.read_text(encoding="utf-8"))
    usados = {s for filme in dados["filmes"] for s in filme.get("streamings", [])}
    assert usados <= cadastrados, f"Sem cadastro: {sorted(usados - cadastrados)}"