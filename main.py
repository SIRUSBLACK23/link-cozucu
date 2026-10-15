import asyncio
from fastapi import FastAPI, Query
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

app = FastAPI()

@app.get("/coz")
async def coz(url: str = Query(...)):
    try:
        async with async_playwright() as p:
            # Gerçek Chrome gibi davranması için özel argümanlar
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled"
                ]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                viewport={"width": 1366, "height": 768},
                locale="tr-TR"
            )
            page = await context.new_page()
            
            # Cloudflare bot algılamasını kapat
            await stealth_async(page)

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=25000)
            except Exception:
                pass

            # Sayfanın yüklenmesi ve Cloudflare kontrolü için bekle
            await asyncio.sleep(4)

            # 1. Yöntem: Sayfa içindeki tüm <a> etiketlerindeki Trendyol / HB linklerini tara
            for _ in range(8):
                if "trendyol.com" in page.url or "hepsiburada.com" in page.url:
                    sonuc = page.url
                    await browser.close()
                    return {"hedef": sonuc}

                try:
                    hrefs = await page.eval_on_selector_all("a", "elements => elements.map(el => el.href)")
                    for h in hrefs:
                        if "trendyol.com" in h or "hepsiburada.com" in h:
                            await browser.close()
                            return {"hedef": h}
                except Exception:
                    pass

                # 2. Yöntem: Butona tıkla
                try:
                    buton = await page.query_selector("a:has-text('Kampanyaya Git'), a:has-text('Fırsata Git'), a.btn-primary")
                    if buton:
                        await buton.click()
                except Exception:
                    pass

                await asyncio.sleep(1.5)

            sonuc = page.url
            await browser.close()
            return {"hedef": sonuc}

    except Exception as e:
        return {"hata": str(e), "hedef": url}
