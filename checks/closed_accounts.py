"""Closed account acceptance in Chromium; live mode requires host-held fixture credentials."""
import argparse
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
from urllib.parse import urlparse
from urllib.request import urlopen
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
EMAILS = ("closed-test-one@example.invalid","closed-test-two@example.invalid")
LIVE = "https://bauradar-pilot.onrender.com"
stage = "setup"
process = None

def start(env, base):
    global process
    process = subprocess.Popen([sys.executable,"-m","uvicorn","backend.app:app",
                                "--host","127.0.0.1","--port","8767"],cwd=ROOT,env=env,
                                stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    for _ in range(80):
        if process.poll() is not None: raise RuntimeError("Closed test server exited")
        try:
            with urlopen(base+"/api/live",timeout=1): return
        except Exception: time.sleep(.25)
    raise RuntimeError("Closed test server unavailable")

def stop():
    global process
    if process:
        process.terminate();process.wait(timeout=15);process=None

def run(base,password,restart=None,persistence=False):
    global stage
    with sync_playwright() as p:
        browser=p.chromium.launch()
        contexts=[browser.new_context() for _ in EMAILS]
        pages=[context.new_page() for context in contexts]
        errors=[]
        for page in pages:
            page.on("pageerror",lambda error:errors.append("browser script error"))
        def api(context,path,method="GET",body=None):
            response=context.request.fetch(base+"/api/"+path,method=method,
                                           headers={"Origin":base},data=body,timeout=90000)
            return response
        def login(index):
            global stage
            stage="login-account-"+str(index+1)
            page=pages[index]
            statuses=[]
            def record_response(response):
                path=urlparse(response.url).path
                if path in ("/api/login","/api/me","/api/profile","/api/watches"):
                    statuses.append({"endpoint":path,"status":response.status})
            page.on("response",record_response)
            page.goto(base+"/",timeout=90000)
            expect(page.locator("#accountOpen")).to_be_visible(timeout=30000)
            expect(page.locator("#register")).to_be_hidden()
            page.locator("#accountOpen").click()
            page.locator("#accountEmail").fill(EMAILS[index])
            page.locator("#accountPassword").fill(password)
            page.locator("#accountForm button[type=submit]").click()
            try:
                expect(page.locator("#logout")).to_be_visible(timeout=30000)
            except Exception:
                print(json.dumps({"stage":stage,"api_statuses":statuses[-12:],"diagnostic":"Login did not complete; response bodies and credentials omitted."}))
                raise
            finally:
                page.remove_listener("response",record_response)
            expect(page.locator("#register")).to_be_hidden()
            if base.startswith("https:"):
                cookie=next(c for c in contexts[index].cookies(base) if c["name"]=="bauradar_session")
                assert cookie["secure"] and cookie["httpOnly"] and cookie["sameSite"]=="Strict"
        try:
            stage="closed-registration-and-anonymous-access"
            health=api(contexts[0],"health")
            assert health.ok and health.json()["signup_enabled"] is False
            assert api(contexts[0],"me").status==401
            response=api(contexts[0],"register","POST",{"email":"blocked@example.invalid","password":password})
            assert response.status==503
            stage="login-two-existing-accounts"
            for index in range(2): login(index)
            assert all(context.request.get(base+"/admin/").status==403 for context in contexts)
            if persistence:
                stage="live-redeploy-persistence"
                expect(pages[0].locator("#companyName")).to_have_value("Geschlossener Test A")
                expect(pages[1].locator("#companyName")).to_have_value("Geschlossener Test B")
                assert len(api(contexts[0],"watches").json())==1
                assert api(contexts[1],"watches").json()==[]
            else:
                stage="prepare-only-synthetic-fixtures"
                for context in contexts:
                    for identity in api(context,"watches").json():
                        assert api(context,"watches/"+identity,"DELETE").ok
                assert api(contexts[1],"profile","PUT",{"name":"Geschlossener Test B","trades":[]}).ok
                stage="profile-and-watch-isolation"
                page=pages[0]
                page.reload()
                expect(page.locator("#logout")).to_be_visible()
                page.locator("#companyName").fill("Geschlossener Test A")
                page.locator("#companyCity").fill("")
                page.locator("#locationMode").select_option("all")
                for checkbox in page.locator('[name=trade]').all(): checkbox.uncheck(force=True)
                page.locator('[name=trade][value=electrical]').check(force=True)
                page.get_by_role("button",name="Passende Projekte anzeigen").click()
                expect(page.locator("#profileMessage")).to_have_text("Betriebsprofil gespeichert.")
                expect(page.locator(".project-card").first).to_be_visible()
                page.locator("[data-watch]").first.click()
                expect(page.locator("#savedCount")).to_have_text("1")
                pages[1].reload()
                expect(pages[1].locator("#companyName")).to_have_value("Geschlossener Test B")
                expect(pages[1].locator("#savedCount")).to_have_text("0")
                assert api(contexts[0],"profile").json()["name"]=="Geschlossener Test A"
                assert api(contexts[1],"watches").json()==[]
            stage="reload-and-returning-login"
            pages[0].reload()
            expect(pages[0].locator("#companyName")).to_have_value("Geschlossener Test A")
            expect(pages[0].locator("#savedCount")).to_have_text("1")
            pages[0].locator("#logout").click()
            expect(pages[0].locator("#logout")).to_be_hidden()
            assert api(contexts[0],"me").status==401
            login(0)
            expect(pages[0].locator("#companyName")).to_have_value("Geschlossener Test A")
            expect(pages[0].locator("#savedCount")).to_have_text("1")
            if restart:
                stage="closed-process-restart-and-existing-sessions"
                restart()
                for page in pages: page.reload()
                expect(pages[0].locator("#companyName")).to_have_value("Geschlossener Test A")
                expect(pages[0].locator("#savedCount")).to_have_text("1")
                expect(pages[1].locator("#companyName")).to_have_value("Geschlossener Test B")
                expect(pages[1].locator("#savedCount")).to_have_text("0")
                assert all(api(context,"me").status==200 for context in contexts)
            assert not errors
            print(json.dumps({"closed_signup":True,"two_accounts":True,"profile_and_watch_isolation":True,
                              "returning_login":True,"admin_denied":True,"browser":"Chromium",
                              "environment":"live Render/Neon" if base==LIVE else "disposable CI PostgreSQL",
                              "process_restart":bool(restart),"live_redeploy_persistence":persistence,
                              "secure_cookies":base.startswith("https:")}))
        finally:
            for context in contexts: context.close()
            browser.close()

def main():
    global stage
    parser=argparse.ArgumentParser()
    parser.add_argument("--live",action="store_true")
    parser.add_argument("--verify-persistence",action="store_true")
    args=parser.parse_args()
    if args.live:
        password=os.environ.get("BAURADAR_CLOSED_TEST_PASSWORD","")
        if len(password)<32: raise RuntimeError("Live fixture secret not configured")
        run(LIVE,password,persistence=args.verify_persistence)
    else:
        if args.verify_persistence: raise ValueError("Persistence mode requires --live")
        database_url=os.environ["TEST_POSTGRES_URL"]
        if urlparse(database_url).hostname not in ("localhost","127.0.0.1"):
            raise ValueError("CI fixture test requires a local disposable PostgreSQL service")
        password=secrets.token_urlsafe(36)
        base="http://127.0.0.1:8767"
        env=dict(os.environ,BAURADAR_DATABASE_URL=database_url,BAURADAR_ORIGIN=base,
                 BAURADAR_SECURE_COOKIES="false",BAURADAR_ENABLE_SIGNUP="false",
                 BAURADAR_CLOSED_TEST_PASSWORD=password,
                 BAURADAR_ADMIN_EMAILS=",".join(EMAILS))
        env.pop("RENDER_EXTERNAL_URL",None)
        try:
            start(env,base)
            def restart():
                stop();start(env,base)
            run(base,password,restart=restart)
        finally:
            stop()
            stage="disable-fixtures-and-revoke-access"
            env.pop("BAURADAR_CLOSED_TEST_PASSWORD",None)
            try:
                start(env,base)
                from backend.database import connect
                from backend.closed_test import FIXTURES
                with connect(Path("/tmp/unused.sqlite"),database_url) as db:
                    for uid,email in FIXTURES:
                        assert db.execute("SELECT id FROM users WHERE id=?",(uid,)).fetchone() is None
                        assert db.execute("SELECT token_hash FROM sessions WHERE user_id=?",(uid,)).fetchone() is None
                print("Closed fixtures removed and access revoked after disabling test secret.")
            finally: stop()

if __name__=="__main__":
    try: main()
    except Exception:
        print("Closed account test failed at stage: "+stage+". No credentials were logged.",file=sys.stderr)
        sys.exit(1)
