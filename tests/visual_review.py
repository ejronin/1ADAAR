"""Actual Chromium visual review at six CSS widths; no production deploy.

Executed inside GitHub Actions from the PR's working tree. The screenshots
capture the staged PlayerOne page, not a hand-drawn mockup or synthetic image.
"""
from __future__ import annotations
import asyncio
import functools
import http.server
import json
import os
from pathlib import Path
import threading

from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
WIDTHS=(320,375,390,768,1024,1440)
ARTIFACT=ROOT/"visual-review"
ARTIFACT.mkdir(exist_ok=True)


async def capture():
    handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT/"docs"))
    server=http.server.ThreadingHTTPServer(("127.0.0.1",0),handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    origin=f"http://127.0.0.1:{server.server_port}"
    report={"origin":"staging checkout / Python static HTTP","screenshots":[]}
    try:
        async with async_playwright() as p:
            browser=await p.chromium.launch(headless=True,args=["--no-sandbox"])
            for width in WIDTHS:
                page=await browser.new_page(viewport={"width":width,"height":900},device_scale_factor=1)
                errors=[]
                page.on("pageerror",lambda error:errors.append(str(error)))
                await page.goto(origin+"/playerone-demo.html",wait_until="domcontentloaded",timeout=30000)
                await page.locator(".perf-svg").wait_for(timeout=20000)
                await page.locator(".snapshot-insight").first.wait_for(timeout=20000)
                await page.screenshot(path=str(ARTIFACT/f"playerone-{width}px.png"),
                                      full_page=True,animations="disabled")
                measurements=await page.evaluate("""() => ({
                   viewport:innerWidth,
                   root:document.documentElement.scrollWidth,
                   body:document.body.scrollWidth,
                   primaryCards:document.querySelectorAll('#profile-metrics .metric-tile').length,
                   secondaryCards:document.querySelectorAll('#profile-secondary .career-secondary-card').length,
                   donuts:document.querySelectorAll('#player-snapshot .profile-win-donut').length,
                   insights:document.querySelectorAll('#player-snapshot .snapshot-insight').length,
                   tabs:[...document.querySelectorAll('.perf-tab')].map(x=>x.textContent.trim()),
                   table:!!document.querySelector('.perf-details table')
                })""")
                report["screenshots"].append({"width":width,**measurements,"errors":errors})
                assert measurements["root"]<=width+2, f"Horizontal overflow at {width}px: {measurements}"
                assert measurements["primaryCards"]==4
                assert measurements["secondaryCards"]==3
                assert measurements["donuts"]==1
                assert measurements["insights"]==2
                assert len(measurements["tabs"])==4
                assert measurements["table"]
                assert not errors, f"JavaScript exceptions at {width}px: {errors}"
                await page.close()
                # Also inspect the live WARCON-backed player lookup surface,
                # with no fake data injected into the browser or source files.
                real=await browser.new_page(viewport={"width":width,"height":900},device_scale_factor=1)
                real_errors=[]
                real.on("pageerror",lambda error:real_errors.append(str(error)))
                await real.goto(origin+"/players.html",wait_until="domcontentloaded",timeout=30000)
                await real.wait_for_timeout(1600)
                await real.screenshot(path=str(ARTIFACT/f"players-search-{width}px.png"),
                                      full_page=True,animations="disabled")
                real_overflow=await real.evaluate("document.documentElement.scrollWidth-innerWidth")
                assert real_overflow<=2, f"Search page horizontal overflow at {width}px: {real_overflow}"
                # When captured public data is present, exercise the entire
                # lookup → true profile → chart → saved match chain.
                usable=await real.evaluate("""() => {
                  try {return typeof publicState!=='undefined' &&
                    publicState.ready&&publicState.players.length>0} catch(_){return false}
                }""")
                if usable:
                    player_name=await real.evaluate("publicState.players[0].name")
                    await real.locator("#player-query").fill(player_name)
                    await real.locator("#player-search button[type='submit']").click()
                    if await real.locator("#player-candidates .candidate").count():
                        await real.locator("#player-candidates .candidate").first.click()
                    await real.locator("#dossier").wait_for(state="visible",timeout=15000)
                    await real.locator("#player-snapshot .profile-win-donut").wait_for(timeout=15000)
                    await real.screenshot(path=str(ARTIFACT/f"players-profile-{width}px.png"),
                                          full_page=True,animations="disabled")
                    actual=await real.evaluate("""() => ({
                      primary:document.querySelectorAll('#profile-metrics .metric-tile').length,
                      secondary:document.querySelectorAll('#profile-secondary .career-secondary-card').length,
                      donuts:document.querySelectorAll('#player-snapshot .profile-win-donut').length,
                      insights:document.querySelectorAll('#player-snapshot .snapshot-insight').length,
                      overflow:document.documentElement.scrollWidth-innerWidth,
                      share:!!document.querySelector('#share-player')
                    })""")
                    assert actual["primary"]==4 and actual["secondary"]==3
                    assert actual["donuts"]==1 and actual["insights"]==2 and actual["share"]
                    assert actual["overflow"]<=2, f"Live profile overflow {width}px: {actual}"
                    report.setdefault("realProfiles",[]).append({"width":width,**actual})
                assert not real_errors, f"Real player page errors at {width}: {real_errors}"
                await real.close()
            # Track keyboard accessibility with ordinary tab traversal on a narrow viewport.
            page=await browser.new_page(viewport={"width":390,"height":844})
            await page.goto(origin+"/playerone-demo.html",wait_until="domcontentloaded",timeout=30000)
            await page.keyboard.press("Tab")
            focus=await page.evaluate("document.activeElement?.tagName")
            report["firstKeyboardFocus"]=focus
            assert focus in ("A","BUTTON"),"First keyboard focus is not an actionable control"
            await page.close()
            await browser.close()
    finally:
        server.shutdown()
    (ARTIFACT/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    asyncio.run(capture())
