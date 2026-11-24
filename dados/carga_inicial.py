from dados.conexao import CAMINHO_BANCO, obter_conexao

NOME_USUARIO_DEMO = "Jow"

# Preço mensal em reais, sem promoções nem combos. Conferir nos sites oficiais.
DATA_CONFERENCIA = "2026-11-24"  # ajuste para o dia em que você conferir de fato

CATALOGO_STREAMINGS = {
    "Netflix": [
        ("Padrão com anúncios", 25.90),
        ("Padrão", 51.90),
        ("Premium", 71.90),
    ],
    "HBO Max": [
        ("Básico com anúncios", 29.90),
        ("Standard", 44.90),
        ("Platinum", 55.90),
    ],
    "Prime Video": [
        ("Com anúncios", 19.90),
        ("Sem anúncios", 29.90),
    ],
    "Disney+": [
        ("Padrão com anúncios", 29.90),
        ("Padrão", 49.90),
        ("Premium", 69.90),
    ],
    "Apple TV+": [
        ("Mensal", 34.90),
    ],
    "Paramount+": [
        ("Padrão", 34.90),
        ("Premium", 44.90),
    ],
    "Crunchyroll": [
        ("Fan", 19.90),
        ("Mega Fan", 24.90),
    ],
    "Mubi": [
        ("Mensal", 34.90),  # CONFERIR: fontes divergem (R$ 27,90 x R$ 34,90)
    ],
    "Globoplay": [
        ("Padrão com anúncios", 29.90),
        ("Premium", 39.90),
    ],
}


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


def garantir_streamings_e_planos(caminho=CAMINHO_BANCO) -> None:
    """Cadastra (ou atualiza) streamings e planos. Pode rodar quantas vezes quiser."""
    with obter_conexao(caminho) as conexao:
        for nome, planos in CATALOGO_STREAMINGS.items():
            conexao.execute("INSERT OR IGNORE INTO streamings (nome) VALUES (?)", (nome,))
            streaming_id = conexao.execute(
                "SELECT id FROM streamings WHERE nome = ?", (nome,)
            ).fetchone()["id"]
            for nome_plano, preco in planos:
                conexao.execute(
                    """
                    INSERT INTO planos (streaming_id, nome, preco_mensal, conferido_em)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT (streaming_id, nome) DO UPDATE SET
                        preco_mensal = excluded.preco_mensal,
                        conferido_em = excluded.conferido_em
                    """,
                    (streaming_id, nome_plano, preco, DATA_CONFERENCIA),
                )