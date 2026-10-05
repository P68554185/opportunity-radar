"""Real Chromium checks for Pages preview and account-backed customer workflows."""
import json, os, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/"reports"/"browser";OUTPUT.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory() as temp:
    env=dict(os.environ,BAURADAR_DB=str(Path(temp)/"users.sqlite"),
        BAURADAR_ORIGIN="http://127.0.0.1:8765",BAURADAR_SECURE_COOKIES="false",BAURADAR_ENABLE_SIGNUP="true")
    process=subprocess.Popen([sys.executable,"-m","uvicorn","backend.app:app","--host","127.0.0.1","--port","8765"],cwd=ROOT,env=env)
    try:
        for attempt in range(60):
            try:
                urllib.request.urlopen("http://127.0.0.1:8765/api/health",timeout=1);break
            except Exception: time.sleep(.25)
        else: raise RuntimeError("Test server did not start")
        with sync_playwright() as p:
            browser=p.chromium.launch()
            context=browser.new_context(viewport={"width":1280,"height":900})
            page=context.new_page()
            errors=[]
            page.on("pageerror",lambda error:errors.append(str(error)))
            page.goto("http://127.0.0.1:8765/")
            expect(page.locator(".project-card").first).to_be_visible()
            expect(page.locator("#accountOpen")).to_be_visible()
            assert not any(word in page.locator("body").inner_text() for word in ("Classification Rate","Quality Gate","Smart Validation"))
            page.locator('[name="trade"][value="electrical"]').check(force=True)
            page.get_by_role("button",name="Passende Projekte anzeigen").click()
            assert all("Elektro" in card.inner_text() for card in page.locator(".project-card").all())
            page.locator("[data-watch]").first.click()
            page.locator('[data-view="saved"]').click()
            expect(page.locator(".project-card")).to_have_count(1)
            page.reload()
            expect(page.locator(".project-card").first).to_be_visible()
            expect(page.locator("#savedCount")).to_have_text("1")
            page.screenshot(path=str(OUTPUT/"desktop.png"),full_page=True)
            page.set_viewport_size({"width":390,"height":844})
            overflow=page.evaluate("Array.from(document.querySelectorAll('body *')).filter(e=>e.getBoundingClientRect().right>window.innerWidth+1).map(e=>({tag:e.tagName,id:e.id,class:e.className,width:e.getBoundingClientRect().width})).slice(0,10)")
            assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"),f"Mobile horizontal overflow: {overflow}"
            page.screenshot(path=str(OUTPUT/"mobile.png"),full_page=True)
            page.locator("#accountOpen").click()
            page.locator("#accountEmail").fill("browser@example.com")
            page.locator("#accountPassword").fill("browser-test-password")
            page.locator("#register").click()
            expect(page.locator("#logout")).to_be_visible()
            page.locator("#companyName").fill("Browserbetrieb")
            page.locator('[name="trade"][value="electrical"]').check(force=True)
            page.get_by_role("button",name="Passende Projekte anzeigen").click()
            expect(page.locator("#profileMessage")).to_have_text("Betriebsprofil gespeichert.")
            page.locator('[data-view="all"]').click()
            expect(page.locator(".project-card").first).to_be_visible()
            page.locator("[data-watch]").first.click()
            expect(page.locator("#savedCount")).to_have_text("1")
            page.reload()
            expect(page.locator("#companyName")).to_have_value("Browserbetrieb")
            expect(page.locator("#savedCount")).to_have_text("1")
            page.locator("#logout").click()
            expect(page.locator("#logout")).to_be_hidden()
            expect(page.locator("#companyName")).to_have_value("")
            assert not errors,errors
            context.close()
            # Static Pages mode: no backend login, local persistence remains functional.
            preview=browser.new_context()
            static=preview.new_page()
            static.route("**/api/**",lambda route:route.fulfill(status=404,body="not found"))
            static.goto("http://127.0.0.1:8765/")
            expect(static.locator(".project-card").first).to_be_visible()
            expect(static.locator("#accountOpen")).to_be_hidden()
            static.locator("#search").fill("zzzz-no-project-match")
            expect(static.locator(".project-card")).to_have_count(0)
            expect(static.locator(".empty")).to_be_visible()
            preview.close();browser.close()
        print(json.dumps({"browser":"Chromium","desktop":True,"mobile":True,"local_watch":True,"accounts":True,"server_profile":True,"server_watch":True}))
    finally:
        process.terminate();process.wait(timeout=10)
