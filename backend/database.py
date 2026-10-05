"""Small parameter-bound SQL adapter for local SQLite and hosted PostgreSQL."""
from contextlib import contextmanager
from pathlib import Path
import sqlite3
import psycopg
from psycopg.rows import dict_row

class Row(dict):
    def __getitem__(self,key):
        return list(self.values())[key] if isinstance(key,int) else super().__getitem__(key)

class Cursor:
    def __init__(self,cursor): self.cursor=cursor
    def fetchone(self):
        row=self.cursor.fetchone()
        return Row(row) if row is not None else None
    def fetchall(self): return [Row(row) for row in self.cursor.fetchall()]
    def __iter__(self): return iter(self.fetchall())

class PostgresConnection:
    def __init__(self,connection): self.connection=connection
    def execute(self,sql,parameters=()):
        # All queries are application-owned SQL; customer values stay bound parameters.
        if sql.startswith("INSERT OR IGNORE INTO "):
            sql=sql.replace("INSERT OR IGNORE INTO ","INSERT INTO ",1)+" ON CONFLICT DO NOTHING"
        return Cursor(self.connection.execute(sql.replace("?","%s"),parameters))
    def executescript(self,script):
        for statement in script.split(";"):
            if statement.strip():self.execute(statement)
    def commit(self): self.connection.commit()
    def rollback(self): self.connection.rollback()

@contextmanager
def connect(path,url=""):
    if url:
        with psycopg.connect(url,row_factory=dict_row,connect_timeout=10) as connection:
            yield PostgresConnection(connection)
    else:
        path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
        connection=sqlite3.connect(path,timeout=15)
        connection.row_factory=sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA journal_mode=WAL")
        try: yield connection
        finally: connection.close()
