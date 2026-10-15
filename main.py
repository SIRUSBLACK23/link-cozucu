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
                await page.goto(url, wait_until="networkidle", timeout=30000)
            except Exception:
                pass

            # Varsa bildirim veya popup kapatma butonunu tıkla
            try:
                popup_kapat = await page.query_selector("button.close, .modal-close, [aria-label='Close'], .btn-close")
                if popup_kapat:
                    await popup_kapat.click()
                    await asyncio.sleep(1)
            except Exception:
                pass

            # Kampanyaya Git / Fırsata Git butonuna tıkla
            try:
                buton = await page.query_selector("a:has-text('Kampanyaya Git'), a:has-text('Fırsata Git'), button:has-text('Kampanyaya Git'), a.btn-primary")
                if buton:
                    await buton.click()
            except Exception:
                pass

            # Trendyol veya Hepsiburada URL'si gelene kadar bekle
            for _ in range(15):
                suanki = page.url
                if "trendyol.com" in suanki or "hepsiburada.com" in suanki:
                    await browser.close()
                    return {"hedef": suanki}

                # Sayfadaki tüm dış linkleri kontrol et
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
