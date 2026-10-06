import tempfile
from pathlib import Path
import sqlite3
import unittest
from backend.closed_test import configure, FIXTURES
from backend.app import SCHEMA, password_hash, password_matches

class ClosedTestFixtures(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = sqlite3.connect(Path(self.temp.name)/"test.sqlite")
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)
        self.db.execute("INSERT INTO users VALUES(?,?,?,?)",("real","owner@example.com","untouched",1))
        self.password = "closed-test-only-password-32-characters"
    def tearDown(self):
        self.db.close(); self.temp.cleanup()
    def configure(self, password):
        configure(self.db,password,password_hash,password_matches)
    def test_disabled_and_cleanup_preserve_customer(self):
        self.configure("")
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM users").fetchone()[0],1)
        self.configure(self.password)
        uid = FIXTURES[0][0]
        self.db.execute("INSERT INTO profiles VALUES(?,?)",(uid,'{"name":"fixture"}'))
        self.db.execute("INSERT INTO sessions VALUES(?,?,?)",("synthetic-token",uid,2000000000))
        self.configure("")
        self.assertEqual(self.db.execute("SELECT id,password FROM users").fetchone()["id"],"real")
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0],0)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM profiles").fetchone()[0],0)
    def test_repeat_preserves_profile_password_and_session(self):
        self.configure(self.password)
        uid = FIXTURES[0][0]
        original = self.db.execute("SELECT password FROM users WHERE id=?",(uid,)).fetchone()[0]
        self.db.execute("INSERT INTO profiles VALUES(?,?)",(uid,'{"name":"persist"}'))
        self.db.execute("INSERT INTO sessions VALUES(?,?,?)",("synthetic-token",uid,2000000000))
        self.configure(self.password)
        self.assertEqual(self.db.execute("SELECT password FROM users WHERE id=?",(uid,)).fetchone()[0],original)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0],1)
        self.configure(self.password+"-rotated")
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0],0)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM profiles").fetchone()[0],1)
    def test_short_secret_and_identity_conflict_are_refused(self):
        with self.assertRaises(RuntimeError): self.configure("short")
        self.db.execute("INSERT INTO users VALUES(?,?,?,?)",("other",FIXTURES[1][1],"untouched",1))
        with self.assertRaises(RuntimeError): self.configure(self.password)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM users").fetchone()[0],2)
