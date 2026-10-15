import asyncio
from fastapi import FastAPI, Query
from playwright.async_api import async_playwright

app = FastAPI()

@app.get("/coz")
async def coz(url: str = Query(...)):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=25000)
            except Exception:
                pass

            for _ in range(12):
                suanki = page.url
                if "trendyol.com" in suanki or "hepsiburada.com" in suanki:
                    await browser.close()
                    return {"hedef": suanki}

                try:
                    linkler = await page.eval_on_selector_all("a[href]", "elements => elements.map(e => e.href)")
                    for l in linkler:
                        if "trendyol.com" in l or "hepsiburada.com" in l:
                            await browser.close()
                            return {"hedef": l}
                except Exception:
                    pass

                await asyncio.sleep(1)

            sonuc = page.url
            await browser.close()
            return {"hedef": sonuc}

    except Exception as e:
        return {"hata": str(e), "hedef": url}
