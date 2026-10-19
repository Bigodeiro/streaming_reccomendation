import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dados.conexao import inicializar_banco
from dados.carga_inicial import garantir_usuario_demo

def test_user_inicial():
    inicializar_banco()
    print("Banco inicializado.")

    usuario_id, usuario_nome = garantir_usuario_demo()
    print(f"Usuario demo garantido: id={usuario_id}, nome={usuario_nome}")
    assert usuario_id is not None, "None returned for usuario_id"
    assert usuario_nome is not None, "None returned for usuario_nome"

test_user_inicial()