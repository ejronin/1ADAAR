#!/usr/bin/env python3
"""Render real Chromium screenshots from editable design files. No live WARCON requests."""
from __future__ import annotations
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json
import os
import threading
import datetime
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "design" / "v1.1.0"
SCREENS = ["home", "player", "map-team", "weekly", "recap", "activity"]
WIDTHS = (320, 375, 390, 768, 1024, 1440)
OUT = BASE / "screenshots"
OUT.mkdir(exist_ok=True)

class SilentHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

def capture():
    os.chdir(ROOT)
    server = ThreadingHTTPServer(("127.0.0.1", 0), SilentHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    root_url = f"http://127.0.0.1:{server.server_port}/design/v1.1.0/prototypes"
    errors = []
    report = ["# Browser QA of editable design candidates", "",
              "Source: design/v1.1.0/prototypes/*.html (not current implementation pages).",
              "These are browser screenshots, not native Discord-app screenshots. All data in mockups is explicit fictional fixture or no-data.",
              "",
              "| Screen | CSS width | Page JS errors | Body overflow px | Result |",
              "|---|---:|---:|---:|---|"]
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            for name in SCREENS:
                for width in WIDTHS:
                    page = browser.new_page(viewport={"width": width, "height": 870},
                                            device_scale_factor=1,
                                            reduced_motion="reduce" if width == 320 else "no-preference")
                    js_errors = []
                    page.on("pageerror", lambda e, sink=js_errors: sink.append(str(e)))
                    response = page.goto(f"{root_url}/{name}.html", wait_until="domcontentloaded", timeout=30000)
                    if response is None or response.status != 200:
                        errors.append(f"{name}-{width} unexpected status")
                    page.wait_for_timeout(1750)  # let once-only art motion finish in normal-motion modes
                    # Genuinely load repository branding, not only layout boxes.
                    for img in page.locator("img").all():
                        if img.evaluate("(el) => el.complete && el.naturalWidth === 0"):
                            errors.append(f"{name}-{width}: original image unavailable: {img.get_attribute('src')}")
                    # Verify interactive designs against the canonical PlayerOne data.
                    if name == "player":
                        panel=page.locator("#progression")
                        if panel.count()!=1:
                            errors.append(f"player-{width}: missing optional progression connection proposal")
                        else:
                            if panel.locator(".progression-rows span").count()!=6:
                                errors.append(f"player-{width}: not all six exact role axes have empty-state rows")
                            if panel.locator(".progression-metrics .metric").count()!=4:
                                errors.append(f"player-{width}: missing WARDOG level / career XP / cash / gold")
                            link=panel.locator('a[href="https://wardogstracker.gg/stats"]')
                            if link.count()!=1 or link.get_attribute("target")!="_blank":
                                errors.append(f"player-{width}: missing real tracker sync external link")
                            if not all(k in panel.inner_text() for k in
                                       ("WARDOG level","Career XP","Account cash","Gold",
                                        "Assault","Medic","Support","Recon","Driver","Pilot")):
                                errors.append(f"player-{width}: missing approved exact role/economy language")
                    if name == "player":
                        if page.locator("#performance-chart svg.chart").count() != 1:
                            errors.append(f"player-{width}: canonical data chart absent")
                        if page.locator("#chart-data tr").count() != 33:
                            errors.append(f"player-{width}: expected 32 sourced rows")
                        if "2026-10-15" not in (page.locator("#chart-data").text_content() or ""):
                            errors.append(f"player-{width}: canonical last observation missing")
                    if name == "map-team":
                        if page.locator(".titlebar [data-map]").count() != 0 or page.locator(".result-composition [data-map]").count() != 3:
                            errors.append(f"map-team-{width}: local-only selectors must live inside Result composition, not page-level header")
                    if name == "recap":
                        links = page.locator(".discord a.action")
                        if links.count() != 2 or any(not (link.get_attribute("href") or "").startswith("https://ejronin.github.io/1ADAAR/") for link in links.all()):
                            errors.append(f"recap-{width}: missing functional first-party Discord-link design CTA")
                        if page.locator(".discord-faction-leaders").count() != 2:
                            errors.append(f"recap-{width}: missing faction top-player availability design block")
                    if name == "map-team":
                        outcome_text = page.locator("#map-insight").inner_text()
                        if not all(term in outcome_text for term in ("Wins", "5 of 10", "Losses", "4 of 10", "Draws", "1 of 10")):
                            errors.append(f"map-team-{width}: outcome view not grounded in fixture")
                    if name == "activity":
                        if page.locator("#heat-cells button[data-b='1']").count() != 0:
                            errors.append(f"activity-{width}: real empty state has fabricated colored cells")
                    if name == "home" and width in (390, 1440):
                        # CSS animations must conclude fully (no lingering bright laser segment).
                        page.wait_for_timeout(1200)
                        motion = page.evaluate("""() => {
                          const hero = document.querySelector('.hero');
                          const laser = hero.querySelector('.laser');
                          const mark = hero.querySelector('.hero-logo-mark');
                          const sheen = hero.querySelector('.hero-logo-sheen');
                          const logo = mark.querySelector('img');
                          const r = el => {
                            const b=el.getBoundingClientRect();
                            return {x:b.x,y:b.y,width:b.width,height:b.height};
                          };
                          return {
                            beamOpacity:parseFloat(getComputedStyle(laser).opacity),
                            sheenOpacity:parseFloat(getComputedStyle(sheen).opacity),
                            laserAnimation:getComputedStyle(laser).animationName,
                            mask:getComputedStyle(sheen).maskImage||getComputedStyle(sheen).webkitMaskImage,
                            mark:r(mark),logo:r(logo),sheen:r(sheen)
                          };
                        }""")
                        if motion["beamOpacity"] > .01 or motion["sheenOpacity"] > .01:
                            errors.append(f"home-{width}: laser/sheens remain bright after motion: {motion}")
                        if "1ad-logo.svg" not in motion["mask"]:
                            errors.append(f"home-{width}: sheen is not alpha-masked to original 1AD source")
                        for key in ("width","height","x","y"):
                            if abs(motion["logo"][key]-motion["sheen"][key])>1:
                                errors.append(f"home-{width}: sheen not exact displayed emblem geometry: {motion}")
                                break
                        if motion["laserAnimation"] == "none":
                            errors.append(f"home-{width}: perimeter motion absent")
                    if name == "weekly":
                        cards = page.locator(".weekly-spotlight .weekly-podium .weekly-place")
                        if cards.count() != 3:
                            errors.append(f"weekly-{width}: expected three distinct placement cards")
                        else:
                            visual = cards.evaluate_all("""els => els.map(el => ({
                              x:el.getBoundingClientRect().x,
                              height:el.getBoundingClientRect().height,
                              border:getComputedStyle(el).borderTopColor,
                              text:el.innerText
                            }))""")
                            if not visual[0]["x"] < visual[1]["x"] < visual[2]["x"]:
                                errors.append(f"weekly-{width}: wrong silver/gold/bronze order")
                            if visual[1]["height"] <= visual[0]["height"]:
                                errors.append(f"weekly-{width}: first-place gold card must be taller")
                            if len({v["border"] for v in visual}) != 3:
                                errors.append(f"weekly-{width}: podium metallic border colors are not distinct")
                            if any("Awaiting results" not in v["text"] or
                                   "No player selected" not in v["text"] for v in visual):
                                errors.append(f"weekly-{width}: unassigned state lost reference copy")
                        if page.locator(".weekly-spotlight .weekly-crown--static").count()!=1:
                            errors.append(f"weekly-{width}: missing original empty first-place crown")
                        elif not page.locator(".weekly-spotlight .weekly-crown--static").is_visible():
                            errors.append(f"weekly-{width}: static crown not visible")
                    delta = page.evaluate("Math.max(0, document.documentElement.scrollWidth - window.innerWidth)")
                    if delta > 2 or js_errors:
                        overflow_detail=""
                        if delta > 2 and name == "recap":
                            overflow_detail=page.evaluate("""() => [...document.querySelectorAll('*')]
                              .map(el=>({el,box:el.getBoundingClientRect()}))
                              .filter(x=>x.box.right>innerWidth+2)
                              .sort((a,b)=>b.box.right-a.box.right)
                              .slice(0,8)
                              .map(x=>({
                                el:x.el.tagName.toLowerCase(),
                                cls:typeof x.el.className==='string'?x.el.className:'',
                                right:Math.round(x.box.right),
                                width:Math.round(x.box.width),
                                text:(x.el.textContent||'').trim().slice(0,44)
                              }))""")
                        errors.append(f"{name}-{width}: {delta}px overflow, JS={js_errors}, offenders={overflow_detail}")
                    report.append(f"| {name} | {width} | {len(js_errors)} | {delta} | {'PASS' if not js_errors and delta<=2 else 'FAIL'} |")
                    if width in (390,1440):
                        target = OUT / f"{name}-{width}.png"
                        page.screenshot(path=str(target), full_page=True, animations="disabled")
                        if name == "player":
                            page.locator("#kills-encoding").select_option("paired")
                            if page.locator("#performance-chart svg").count() != 1:
                                errors.append(f"player-{width}: paired chart did not render. JS={js_errors}. Panel={page.locator('#performance-chart').text_content()[:260]}")
                            elif "paired comparison" not in (page.locator("#performance-chart svg").get_attribute("aria-label") or "").lower():
                                errors.append(f"player-{width}: paired dumbbell encoding not active")
                            page.screenshot(path=str(OUT / f"player-paired-{width}.png"),
                                            full_page=True, animations="disabled")
                            page.locator("#point-window").select_option("10")
                            if page.locator("#chart-data tr").count() != 11:
                                errors.append(f"player-{width}: Last 10 fails to change plotted points")
                            page.locator("[data-trend='career']").click()
                            if "careerhistory" not in page.locator("#trend-context").inner_text().lower():
                                errors.append(f"player-{width}: career snapshots not correctly labeled")
                            page.locator("[data-trend='rolling']").click()
                            if page.locator("#kills-chart-picker").is_visible():
                                errors.append(f"player-{width}: paired count encoding offered on trailing K/D")
                            if "overlapping" not in page.locator("#trend-context").inner_text().lower():
                                errors.append(f"player-{width}: rolling average denominator unclear")
                        if name == "map-team":
                            page.locator("[data-map='factions']").click()
                            if "Lonestar" not in page.locator("#map-insight").inner_text():
                                errors.append(f"map-team-{width}: faction-share control nonfunctional")
                            page.screenshot(path=str(OUT / f"map-team-faction-share-{width}.png"),
                                            full_page=True, animations="disabled")
                            page.locator("[data-map='maps']").click()
                            if "Bakurani" not in page.locator("#map-insight").inner_text():
                                errors.append(f"map-team-{width}: map-share control nonfunctional")
                        if not target.is_file() or target.stat().st_size < 3000:
                            errors.append(f"{target} screenshot missing or too small")
                    if width == 1440 and name in ("weekly", "activity"):
                        selector = "#weekly-demo" if name == "weekly" else "#demo-heat"
                        page.locator(selector).check()
                        page.wait_for_timeout(200)
                        page.screenshot(path=str(OUT / f"{name}-fictional-interaction-1440.png"),
                                        full_page=True, animations="disabled")
                    page.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    manifest_path = BASE / "screen-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for row in manifest["screens"]:
        name = row["id"]
        screenshots = {
            "mobile390": f"design/v1.1.0/screenshots/{name}-390.png",
            "desktop1440": f"design/v1.1.0/screenshots/{name}-1440.png",
        }
        if all((ROOT / path).is_file() for path in screenshots.values()):
            row["screenshots"] = screenshots
            row["deliveryStatus"] = "editable_prototype_and_chromium_screenshots_committed"
        else:
            row["deliveryStatus"] = "browser_capture_failed"
    manifest["status"] = "owner_visual_review_pending" if not errors else "qa_issues_awaiting_fix"
    manifest["browserQA"] = {"viewportWidths": list(WIDTHS),
                              "screenshotsAreFromEditableSource": True,
                              "nativeDiscordClientVerified": False,
                              "errors": errors}
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    report += ["", "## Data acceptance caveats",
               "The activity heatmap has zero actual saved match starts and is neutral by default.",
               "The fictional interaction captures deliberately show sample-only states, not live data.",
               "The six-role radar has no filled role-level data polygon.",
               "Sourced PlayerOne plot / 32 rows, Last 10 selector, paired-dot encoding, historical snapshots and faction/map switch tested.",
               "A first real WARCON source and actual Discord desktop/mobile visual acceptance are separate release gates.",
               "", "## Errors", *(["- " + e for e in errors] if errors else ["- None in source/prototype browser checks"])]
    (OUT / "BROWSER_QA.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    if errors:
        raise SystemExit("Prototype screenshots contain QA failures: " + "; ".join(errors))

if __name__ == "__main__":
    capture()
