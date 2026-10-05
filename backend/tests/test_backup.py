import sqlite3
import tempfile
import unittest
from pathlib import Path
from backend.backup import backup

class BackupTests(unittest.TestCase):
    def test_backup_can_be_restored(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/"source.sqlite";target=Path(d)/"backup.sqlite"
            with sqlite3.connect(source) as db:
                db.execute("CREATE TABLE probe(value TEXT)")
                db.execute("INSERT INTO probe VALUES('restorable')")
            backup(source,target)
            with sqlite3.connect(target) as db:
                self.assertEqual(db.execute("SELECT value FROM probe").fetchone()[0],"restorable")
            self.assertEqual(target.stat().st_mode & 0o777,0o600)
            with self.assertRaises(FileExistsError): backup(source,target)
