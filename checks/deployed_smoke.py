"""Check the actual published GitHub Pages app and complete customer feed."""
import json
import time
from pathlib import Path
from urllib.request import Request,urlopen
from playwright.sync_api import sync_playwright,expect
BASE="https://p68554185.github.io/opportunity-radar/"
OUTPUT=Path("reports/deployed-browser");OUTPUT.mkdir(parents=True,exist_ok=True)
def fetch(path):
    request=Request(BASE+path,headers={"Cache-Control":"no-cache"})
    with urlopen(request,timeout=30) as response:return response.read().decode("utf-8")
for attempt in range(20):
    try:
        html=fetch("")
        feed=json.loads(fetch("data/bauradar_feed.json"))
        status=json.loads(fetch("data/status.json"))
        assert "Die nächste Chance" in html
        assert feed["count"]==len(feed["opportunities"])==status["opportunities"]
        assert all(r["quality_status"] in ("CONFIDENT","VERIFIED_EARLY") for r in feed["opportunities"])
        break
    except Exception:
        if attempt==19:raise
        time.sleep(3)
with sync_playwright() as p:
    browser=p.chromium.launch()
    context=browser.new_context(viewport={"width":1280,"height":900})
    page=context.new_page();errors=[]
    page.on("pageerror",lambda error:errors.append(str(error)))
    page.goto(BASE)
    expect(page.locator(".project-card").first).to_be_visible()
    expect(page.locator("#accountOpen")).to_be_hidden()
    assert not any(word in page.locator("body").inner_text() for word in ("Classification Rate","Quality Gate","Smart Validation"))
    page.locator('[name="trade"][value="electrical"]').check(force=True)
    page.get_by_role("button",name="Passende Projekte anzeigen").click()
    assert all("Elektro" in card.inner_text() for card in page.locator(".project-card").all())
    page.locator("[data-watch]").first.click()
    expect(page.locator("#savedCount")).to_have_text("1")
    page.reload()
    expect(page.locator("#savedCount")).to_have_text("1")
    page.screenshot(path=str(OUTPUT/"desktop.png"),full_page=True)
    page.set_viewport_size({"width":390,"height":844})
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    page.screenshot(path=str(OUTPUT/"mobile.png"),full_page=True)
    page.locator('[data-view="early"]').click()
    expect(page.locator(".project-card").first).to_be_visible()
    assert all("In Ausschreibung" not in c.inner_text() and "Bereits vergeben" not in c.inner_text() for c in page.locator(".project-card").all())
    page.locator('[data-view="all"]').click()
    page.locator('[name="trade"][value="electrical"]').uncheck(force=True)
    page.get_by_role("button",name="Passende Projekte anzeigen").click()
    page.locator("#search").fill("Alsfeld")
    hospital=page.locator(".project-card").filter(has=page.locator('[data-watch="PRJ-A36FC997D2"]'))
    expect(hospital).to_have_count(1)
    expect(hospital.locator(".project-history")).to_be_visible()
    hospital.locator(".project-history summary").click()
    assert "2023" in hospital.locator(".project-history[open]").inner_text()
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    page.screenshot(path=str(OUTPUT/"mobile-project-history.png"),full_page=True)
    page.locator("#search").fill("")
    page.locator("#locationMode").select_option("radius")
    expect(page.locator("#locationHint")).to_contain_text("Straße und Hausnummer")
    page.locator("#companyAddress").fill("Südhöhe 9a · 01217 Dresden")
    page.locator("#companyRadius").fill("50")
    page.get_by_role("button",name="Passende Projekte anzeigen").click()
    expect(page.locator(".project-card")).to_have_count(4)
    assert all("Plangebiet" in c.inner_text() for c in page.locator(".project-card").all())
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    page.screenshot(path=str(OUTPUT/"mobile-dresden-radius.png"),full_page=True)
    assert not errors,errors
    browser.close()
print(json.dumps({"url":BASE,"published_customer_records":feed["count"],"source_records":status["live_records"],"browser":"Chromium","verified":True}))
