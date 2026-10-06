"""Backup/recovery drill on disposable CI databases, never the live Neon database."""
import os
from pathlib import Path
import secrets
import tempfile
from urllib.parse import urlparse, urlunparse
import psycopg
from psycopg import sql
from backend.postgres_backup import backup, restore
from backend.app import SCHEMA

admin_url = os.environ["TEST_POSTGRES_URL"]
suffix = secrets.token_hex(8)
names = ["backup_source_" + suffix, "backup_restore_" + suffix]
parsed = urlparse(admin_url)
urls = [urlunparse(parsed._replace(path="/" + name)) for name in names]
def rows(url, table):
    with psycopg.connect(url) as db:
        return db.execute(sql.SQL("SELECT * FROM {} ORDER BY 1").format(sql.Identifier(table))).fetchall()
try:
    with psycopg.connect(admin_url, autocommit=True) as admin:
        for name in names:
            admin.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
    with psycopg.connect(urls[0]) as db:
        db.execute(SCHEMA)
        db.execute("INSERT INTO users VALUES (%s,%s,%s,%s)", ("fixture-user","restore@example.invalid","test-hash",1))
        db.execute("INSERT INTO sessions VALUES (%s,%s,%s)", ("test-token-hash","fixture-user",2000000000))
        db.execute("INSERT INTO profiles VALUES (%s,%s)", ("fixture-user",'{"name":"Wiederherstellungsbetrieb","trades":["electrical"]}'))
        db.execute("INSERT INTO watches VALUES (%s,%s,%s)", ("fixture-user","fixture-project",1))
    with tempfile.TemporaryDirectory() as folder:
        archive = Path(folder) / "accounts.dump"
        backup(urls[0], archive)
        assert archive.stat().st_mode & 0o777 == 0o600
        try:
            backup(urls[0], archive)
            raise AssertionError("Backup overwritten")
        except FileExistsError:
            pass
        try:
            restore(urls[0], archive, urls[0])
            raise AssertionError("Source restore permitted")
        except ValueError:
            pass
        restore(urls[1], archive, urls[0])
        for table in ("users","sessions","profiles","watches"):
            assert rows(urls[0],table) == rows(urls[1],table), table
        try:
            restore(urls[1], archive, urls[0])
            raise AssertionError("Nonempty restore permitted")
        except ValueError:
            pass
    print("PostgreSQL backup/restore verified: private archive, exact account data, separate empty target, overwrite guards.")
finally:
    with psycopg.connect(admin_url, autocommit=True) as admin:
        for name in names:
            admin.execute(sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(sql.Identifier(name)))
