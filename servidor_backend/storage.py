# (SQLite + funções de persistência)

import sqlite3, json, os, time

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

DDL = """
CREATE TABLE IF NOT EXISTS medidas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sala TEXT NOT NULL,
  ts INTEGER NOT NULL,
  temperatura REAL NOT NULL,
  umidade REAL NOT NULL,
  poeira INTEGER NOT NULL,
  seq INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_medidas_sala_ts ON medidas(sala, ts);
"""

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.executescript(DDL)

def salvar(doc: dict):
    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            "INSERT INTO medidas (sala, ts, temperatura, umidade, poeira, seq) VALUES (?,?,?,?,?,?)",
            (doc["sala"], int(doc["timestamp"]), float(doc["temperatura"]),
             float(doc["umidade"]), int(doc["poeira"]), int(doc["seq"]))
        )
        con.commit()

def get_all(limit=200) -> list[dict]:
    """Busca as N últimas medidas do banco de dados."""
    registros = []
    # Usamos sqlite3.Row para poder converter o resultado em dict facilmente
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row 
        cursor = con.execute(
            """
            SELECT id, sala, ts, temperatura, umidade, poeira, seq 
            FROM medidas 
            ORDER BY id DESC 
            LIMIT ?
            """,
            (limit,)
        )
        for row in cursor.fetchall():
            registros.append(dict(row)) # Converte a Row em um dict
    return registros
