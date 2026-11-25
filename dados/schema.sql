CREATE TABLE IF NOT EXISTS usuarios (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS favoritos (
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    filme_id   INTEGER NOT NULL,
    criado_em  TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (usuario_id, filme_id)
);

CREATE TABLE IF NOT EXISTS streamings (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS planos (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    streaming_id INTEGER NOT NULL REFERENCES streamings(id) ON DELETE CASCADE,
    nome         TEXT NOT NULL,
    preco_mensal REAL NOT NULL,
    conferido_em TEXT,
    UNIQUE (streaming_id, nome)
);