from dados.conexao import CAMINHO_BANCO, obter_conexao

NOME_USUARIO_DEMO = "Jow"


def garantir_usuario_demo(caminho=CAMINHO_BANCO) -> tuple:
    # Perfil simulado usado até a autenticação real Devolve o id e o nome.
    with obter_conexao(caminho) as conexao:
        conexao.execute(
            "INSERT OR IGNORE INTO usuarios (nome) VALUES (?)", (NOME_USUARIO_DEMO,)
        )
        linha = conexao.execute(
            "SELECT id, nome FROM usuarios WHERE nome = ?", (NOME_USUARIO_DEMO,)
        ).fetchone()
        return linha["id"], linha["nome"]

