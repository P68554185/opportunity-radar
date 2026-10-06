import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from backend.postgres_backup import ROOT, backup, connection_env, restore

class PostgresBackupSafetyTests(unittest.TestCase):
    def test_credentials_are_separate_from_process_arguments(self):
        with patch.dict(os.environ, {"PGSERVICE":"unexpected", "PGOPTIONS":"-c search_path=attacker"}):
            env = connection_env("postgresql://user:p%40ss@db.example/test?sslmode=require&channel_binding=require")
        self.assertEqual(env["PGPASSWORD"],"p@ss")
        self.assertEqual(env["PGSSLMODE"],"require")
        self.assertNotIn("PGSERVICE",env)
        self.assertNotIn("PGOPTIONS",env)

    def test_repository_destination_refused(self):
        with self.assertRaises(ValueError):
            backup("postgresql://user:pass@host/db", ROOT/"reports"/"private.dump")

    def test_failed_dump_removes_partial_file(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp)/"partial.dump"
            with patch("backend.postgres_backup.subprocess.run",side_effect=TimeoutError):
                with self.assertRaises(TimeoutError):
                    backup("postgresql://user:pass@host/db",archive)
            self.assertFalse(archive.exists())

    def test_restore_needs_separate_private_target(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp)/"test.dump"
            archive.write_bytes(b"PGDMP")
            archive.chmod(0o600)
            with self.assertRaises(ValueError):
                restore("postgresql://user:pass@host/db",archive,"postgresql://other:pass@host/db")
            archive.chmod(0o644)
            with self.assertRaises(ValueError):
                restore("postgresql://user:pass@host/other",archive,"postgresql://user:pass@host/db")
