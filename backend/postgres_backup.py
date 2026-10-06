"""Private PostgreSQL dump and restore into an empty, separate database."""
import argparse
import os
from pathlib import Path
import subprocess
from urllib.parse import urlparse, unquote, parse_qs
import psycopg

ROOT = Path(__file__).resolve().parents[1]

def connection_env(url):
    parsed = urlparse(url)
    if parsed.scheme not in ("postgres", "postgresql") or not parsed.hostname or not parsed.path.strip("/"):
        raise ValueError("A PostgreSQL database secret is required.")
    # Never pass a credential-bearing URL on the command line or in error output.
    env = {k:v for k,v in os.environ.items() if not k.startswith("PG") and not k.startswith("BAURADAR_")}
    env.update(PGHOST=parsed.hostname, PGPORT=str(parsed.port or 5432),
               PGDATABASE=unquote(parsed.path[1:]), PGUSER=unquote(parsed.username or ""),
               PGPASSWORD=unquote(parsed.password or ""), PGCONNECT_TIMEOUT="15")
    query = parse_qs(parsed.query)
    for key in query:
        if key not in ("sslmode", "channel_binding"):
            raise ValueError("Unsupported connection option; use a plain PostgreSQL connection string.")
    env["PGSSLMODE"] = query.get("sslmode", ["prefer"])[0]
    env["PGCHANNELBINDING"] = query.get("channel_binding", ["prefer"])[0]
    return env

def identity(url):
    parsed = urlparse(url)
    return (parsed.hostname, parsed.port or 5432, unquote(parsed.path[1:]))

def private_path(path):
    path = Path(path).expanduser().resolve()
    if path.is_relative_to(ROOT):
        raise ValueError("Backups must stay outside the public repository.")
    return path

def backup(url, destination):
    env = connection_env(url)
    destination = private_path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            result = subprocess.run(["pg_dump", "--format=custom", "--no-owner", "--no-privileges",
                                     "--no-password"], env=env, stdout=stream,
                                    stderr=subprocess.PIPE, timeout=600)
        if result.returncode:
            raise RuntimeError("PostgreSQL backup failed; check connectivity and client/server versions privately.")
        return destination
    except BaseException:
        destination.unlink(missing_ok=True)
        raise

def restore(url, archive, source_url):
    archive = private_path(archive)
    if not source_url or identity(url) == identity(source_url):
        raise ValueError("Restore requires a separate target database and the source database identity.")
    env = connection_env(url)
    if not archive.is_file() or archive.stat().st_mode & 0o077:
        raise ValueError("Restore requires a private backup file (permissions 0600).")
    with archive.open("rb") as stream:
        if stream.read(5) != b"PGDMP":
            raise ValueError("Expected a pg_dump custom-format archive.")
    with psycopg.connect(url, connect_timeout=15) as db:
        objects = db.execute("""
            SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
            WHERE n.nspname NOT IN ('pg_catalog','information_schema')
            AND n.nspname NOT LIKE 'pg_toast%' AND c.relkind IN ('r','p','v','m','S','f')
        """).fetchone()[0]
        routines = db.execute("""
            SELECT count(*) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
            WHERE n.nspname NOT IN ('pg_catalog','information_schema')
            AND n.nspname NOT LIKE 'pg_toast%'
        """).fetchone()[0]
        if objects or routines:
            raise ValueError("Restore refused: target database is not empty.")
    result = subprocess.run(["pg_restore", "--exit-on-error", "--single-transaction",
                             "--no-owner", "--no-privileges", "--no-password",
                             "--dbname", env["PGDATABASE"], str(archive)],
                            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=600)
    if result.returncode:
        raise RuntimeError("PostgreSQL restore failed; target transaction was rolled back.")
    return archive

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=("backup", "restore"))
    parser.add_argument("archive")
    args = parser.parse_args()
    try:
        source = os.environ.get("BAURADAR_DATABASE_URL", "")
        if args.operation == "backup":
            backup(source, args.archive)
        else:
            restore(os.environ.get("BAURADAR_RESTORE_DATABASE_URL", ""), args.archive, source)
    except Exception:
        parser.exit(1, "Operation failed. Check private settings, file permissions, and PostgreSQL client version. No credentials were printed.\n")
    print("Private PostgreSQL operation completed.")

if __name__ == "__main__":
    main()
