"""Real process restart against disposable CI PostgreSQL, never the live customer DB."""
import http.cookiejar
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
from urllib.request import Request, build_opener, HTTPCookieProcessor
from urllib.error import HTTPError
import psycopg

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8766"
url = os.environ["TEST_POSTGRES_URL"]
emails = [secrets.token_hex(12) + "@example.invalid" for _ in range(2)]
password = secrets.token_urlsafe(24)
env = dict(os.environ, BAURADAR_DATABASE_URL=url, BAURADAR_ORIGIN=BASE,
           BAURADAR_SECURE_COOKIES="false", BAURADAR_ENABLE_SIGNUP="true")
env.pop("RENDER_EXTERNAL_URL", None)
process = None
def client():
    return build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
one, two = client(), client()
def request(opener, path, method="GET", body=None):
    raw = json.dumps(body).encode() if body is not None else None
    req = Request(BASE + path, data=raw, method=method,
                  headers={"Origin": BASE, "Content-Type": "application/json"})
    with opener.open(req, timeout=15) as response:
        return json.loads(response.read())
def start():
    global process
    process = subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.app:app",
                                "--host", "127.0.0.1", "--port", "8766"],
                               cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        if process.poll() is not None:
            raise RuntimeError("Restart test server exited")
        try:
            request(one, "/api/live")
            return
        except Exception:
            time.sleep(.25)
    raise RuntimeError("Restart test server unavailable")
def stop():
    global process
    if process:
        process.terminate(); process.wait(timeout=15); process = None
try:
    start()
    for opener,email in zip((one,two),emails):
        request(opener,"/api/register","POST",{"email":email,"password":password})
    project = request(one,"/data/bauradar_feed.json")["opportunities"][0]["id"]
    request(one,"/api/profile","PUT",{"name":"Restartbetrieb","city":"Roth","locationMode":"city","trades":["electrical"]})
    request(one,"/api/watches/"+project,"PUT")
    assert request(two,"/api/profile")["name"] == ""
    assert request(two,"/api/watches") == []
    stop()
    env["BAURADAR_ENABLE_SIGNUP"] = "false"
    start()
    assert request(one,"/api/health")["signup_enabled"] is False
    assert request(one,"/api/me")["email"] == emails[0]
    assert request(one,"/api/profile")["name"] == "Restartbetrieb"
    assert request(one,"/api/watches") == [project]
    assert request(two,"/api/watches") == []
    request(one,"/api/logout","POST")
    try:
        request(one,"/api/me")
        raise AssertionError("Logout session remained active")
    except HTTPError as error:
        assert error.code == 401
    request(one,"/api/login","POST",{"email":emails[0],"password":password})
    assert request(one,"/api/profile")["name"] == "Restartbetrieb"
    print(json.dumps({"postgres_process_restart":True,"profiles":True,"watches":True,
                      "session_persistence":True,"account_isolation":True,"signup_after_restart":False}))
finally:
    stop()
    with psycopg.connect(url) as db:
        for email in emails:
            for table in ("sessions","profiles","watches"):
                db.execute("DELETE FROM " + table + " WHERE user_id IN (SELECT id FROM users WHERE email=%s)",(email,))
            db.execute("DELETE FROM users WHERE email=%s",(email,))
