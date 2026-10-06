"""Opt-in synthetic account fixtures for a closed deployment test."""
import secrets
import time

FIXTURES = (
    ("closed_test_one_v1", "closed-test-one@example.invalid"),
    ("closed_test_two_v1", "closed-test-two@example.invalid"),
)
IDS = {uid for uid, _ in FIXTURES}

def configure(db, password, hash_password, matches):
    if password and (len(password) < 32 or len(password) > 200):
        raise RuntimeError("Closed-test password must contain 32 to 200 characters.")
    existing = {}
    for uid, email in FIXTURES:
        rows = list(db.execute("SELECT id,email,password FROM users WHERE id=? OR email=?", (uid,email)))
        if rows and (len(rows) != 1 or rows[0]["id"] != uid or rows[0]["email"] != email):
            raise RuntimeError("Reserved test-account identity conflict; no existing account was changed.")
        existing[uid] = rows[0] if rows else None
    for uid, email in FIXTURES:
        row = existing[uid]
        if not password:
            if row:
                for table in ("sessions", "profiles", "watches"):
                    db.execute("DELETE FROM " + table + " WHERE user_id=?", (uid,))
                db.execute("DELETE FROM users WHERE id=? AND email=?", (uid,email))
        elif row is None:
            db.execute("INSERT INTO users VALUES(?,?,?,?)", (uid,email,hash_password(password),int(time.time())))
        elif not matches(password,row["password"]):
            db.execute("UPDATE users SET password=? WHERE id=?", (hash_password(password),uid))
            db.execute("DELETE FROM sessions WHERE user_id=?", (uid,))
