"""Consistent private SQLite backup. Destination must be outside the public repository."""
import argparse
import os
import sqlite3
from pathlib import Path

def backup(source,destination):
    destination=Path(destination).resolve()
    root=Path(__file__).resolve().parents[1]
    if destination.is_relative_to(root): raise ValueError("Backup must be outside the public repository.")
    if destination.exists(): raise FileExistsError("Refusing to overwrite an existing backup.")
    source=Path(source).resolve()
    if not source.is_file(): raise FileNotFoundError(source)
    destination.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(destination,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
    with sqlite3.connect(f"file:{source}?mode=ro",uri=True) as src,sqlite3.connect(destination) as dst:
        src.backup(dst)
    return destination

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("destination")
    parser.add_argument("--source",default=os.environ.get("BAURADAR_DB","/var/lib/bauradar/users.sqlite"))
    args=parser.parse_args()
    print(backup(args.source,args.destination))
