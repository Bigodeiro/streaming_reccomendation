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
