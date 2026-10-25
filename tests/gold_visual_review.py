"""Browser acceptance and real source-data screenshots for the staged 1ADAAR GOLD page."""
from __future__ import annotations
import asyncio
import datetime as dt
import functools
import http.server
import json
import threading
import urllib.request
from pathlib import Path

from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"review"/"gold"
API="https://wardogserverlist.com/api/gold-bars"
DAY=86400000

def source_snapshot():
    request=urllib.request.Request(
        API,headers={"Accept":"application/json",
                     "User-Agent":"1ADAAR-GoldReview/1.0 (+https://github.com/ejronin/1ADAAR)"})
    with urllib.request.urlopen(request,timeout=35) as response:
        assert response.status==200
        raw=response.read(500000)
    payload=json.loads(raw.decode("utf-8"))
    assert isinstance(payload.get("points"),list) and len(payload["points"])>=49, "Source has too few history points"
    assert isinstance(payload.get("latest"),dict), "Source has no latest price"
    assert all(isinstance(pair,list) and len(pair)==2 for pair in payload["points"])
    assert payload["latest"]["price"]>0
    assert payload["latest"]["ts"]==payload["points"][-1][0]
    assert all(pair[0]%DAY==0 for pair in payload["points"])
    return raw,payload

async def capture():
    raw,payload=source_snapshot()
    OUT.mkdir(parents=True,exist_ok=True)
    handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT/"docs"))
    server=http.server.ThreadingHTTPServer(("127.0.0.1",0),handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    results=[]
    try:
        async with async_playwright() as p:
            browser=await p.chromium.launch(headless=True,args=["--no-sandbox"])
            for width,name in ((1440,"desktop-1440"),(390,"mobile-390")):
                page=await browser.new_page(viewport={"width":width,"height":900},device_scale_factor=1)
                errors=[]
                page.on("pageerror",lambda e: errors.append(str(e)))
                async def fulfill(route):
                    await route.fulfill(status=200,body=raw,
                        headers={"Content-Type":"application/json",
                                 "Access-Control-Allow-Origin":"*",
                                 "Cache-Control":"no-store"})
                await page.route(API,fulfill)
                response=await page.goto(
                    f"http://127.0.0.1:{server.server_port}/gold.html",
                    wait_until="domcontentloaded",timeout=40000)
                assert response and response.status==200
                await page.wait_for_function(
                    "() => document.querySelector('#gold-price').textContent !== '—'",
                    timeout=25000)
                price=await page.locator("#gold-price").inner_text()
                assert price==f"{payload['latest']['price']:,}", (price,payload["latest"])
                assert await page.locator(".gold-line").count()>=1, "Daily price line absent"
                forecast=await page.locator("#gold-forecast-message").inner_text()
                assert forecast.startswith("Daily-price outlook"),forecast
                assert await page.locator(".gold-forecast-line").count()==1, "Forecast line absent"
                assert await page.locator("#gold-forecast-model").inner_text()!="Model: —"
                await page.locator(".gold-range [data-range='7']").click()
                assert await page.locator(".gold-range [data-range='7']").get_attribute("aria-pressed")=="true"
                await page.locator(".gold-range [data-range='30']").click()
                await page.locator('[data-chart-mode="candles"]').click()
                assert await page.locator('.gold-candle-body').count()>=8
                # Hit three actual candle centers, including near the right edge.
                # Hover must not drift as the SVG scales.
                candles=await page.evaluate("""() => {
                    const svg=document.getElementById('gold-chart');
                    const items=[...svg.querySelectorAll('.gold-candle-body')];
                    const indexes=[0,Math.floor(items.length/2),items.length-1];
                    return indexes.map(i=>{
                        const r=items[i],p=svg.createSVGPoint();
                        p.x=Number(r.getAttribute('x'))+Number(r.getAttribute('width'))/2;
                        p.y=Number(r.getAttribute('y'))+Number(r.getAttribute('height'))/2;
                        const pt=p.matrixTransform(svg.getScreenCTM());
                        return {x:pt.x,y:pt.y,cx:p.x};
                    });
                }""")
                for pt in candles:
                    await page.mouse.move(pt['x'],pt['y'])
                    assert await page.locator('#gold-tooltip').is_visible()
                    label=await page.locator('#gold-tooltip').inner_text()
                    assert all(t in label for t in ('OPEN','HIGH','LOW','CLOSE')),label
                    circle_x=float(await page.locator('.gold-focus-dot').get_attribute('cx'))
                    assert abs(circle_x-pt['cx'])<0.05,(circle_x,pt)

                assert await page.locator('[data-chart-mode="candles"]').get_attribute('aria-pressed') == "true"
                assert await page.locator('#gold-candle-explainer').is_visible()
                # Forecast belongs beneath BOTH dashboard columns, with no long empty left gutter.
                dashboard=await page.locator('.gold-dashboard').bounding_box()
                market=await page.locator('.gold-market').bounding_box()
                sidebar=await page.locator('.gold-sidebar').bounding_box()
                forecast_rect=await page.locator('.gold-forecast-panel').bounding_box()
                history=await page.locator('.gold-history').bounding_box()
                assert await page.locator('.gold-sidebar .gold-forecast-panel').count()==0
                assert abs(forecast_rect['x']-dashboard['x'])<=2, (forecast_rect,dashboard)
                assert forecast_rect['width']>=dashboard['width']-2, (forecast_rect,dashboard)
                columns_bottom=max(market['y']+market['height'],sidebar['y']+sidebar['height'])
                assert 0 <= forecast_rect['y']-columns_bottom<=24, (forecast_rect,market,sidebar)
                assert 0 <= history['y']-(forecast_rect['y']+forecast_rect['height'])<=24, (history,forecast_rect)

                rect=await page.locator('#gold-chart').bounding_box()
                toolbar=await page.locator('.gold-chart-toolbar').bounding_box()
                assert rect['y']-toolbar['y']<160, (rect,toolbar)
                assert rect['height']>=350, rect
                await page.screenshot(path=str(OUT/f"{name}-candles.png"),
                                      full_page=True,animations="disabled")
                await page.locator('[data-chart-mode="line"]').click()
                assert await page.locator('.gold-line').count()>=1
                # Line points at different x-coordinates must match marker and hover.
                points=await page.evaluate("""() => {
                    const svg=document.getElementById('gold-chart');
                    const d=svg.querySelector('.gold-line').getAttribute('d');
                    const parsed=[...d.matchAll(/([ML])([0-9.]+),([0-9.]+)/g)]
                        .map(m=>({x:Number(m[2]),y:Number(m[3])}));
                    const ix=[2,Math.floor(parsed.length/2),parsed.length-2];
                    return ix.map(i=>{
                        const p=svg.createSVGPoint();p.x=parsed[i].x;p.y=parsed[i].y;
                        const screen=p.matrixTransform(svg.getScreenCTM());
                        return {x:screen.x,y:screen.y,cx:p.x};
                    });
                }""")
                for pt in points:
                    await page.mouse.move(pt['x'],pt['y'])
                    assert await page.locator('#gold-tooltip').is_visible()
                    text=await page.locator('#gold-tooltip').inner_text()
                    assert 'cash per bar' in text,text
                    cx=float(await page.locator('.gold-focus-dot').get_attribute('cx'))
                    assert abs(cx-pt['cx'])<0.1,(cx,pt)
                await page.mouse.move(2,2)
                assert await page.locator('#gold-tooltip').is_hidden()

                assert await page.locator('#gold-candle-explainer').is_hidden()

                await page.locator(".gold-quick [data-bars='10']").click()
                cash=await page.locator("#gold-cash").inner_text()
                assert cash==f"{payload['latest']['price']*10:,} cash",cash
                await page.locator(".gold-quick [data-bars='1']").click()
                await page.locator(".gold-day").first.click()
                overflow=await page.evaluate("document.documentElement.scrollWidth-innerWidth")
                assert overflow<=2,f"Horizontal overflow {width}: {overflow}"
                assert not errors,f"Uncaught JavaScript errors {width}: {errors}"
                await page.screenshot(path=str(OUT/f"{name}.png"),
                    full_page=True,animations="disabled")
                results.append({"width":width,"price":price,"cashForTen":cash,
                                "forecast":forecast,"overflow":overflow,
                                "pageErrors":errors,
                                "selectedModel":await page.locator("#gold-forecast-model").inner_text()})
                await page.close()
            await browser.close()
    finally:
        server.shutdown()
    report={"source":API,"sourceLatest":payload["latest"],
            "capturedAt":dt.datetime.now(dt.timezone.utc).isoformat(),"results":results}
    (OUT/"browser-report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    asyncio.run(capture())
