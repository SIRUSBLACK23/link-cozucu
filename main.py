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

            # Tüm ağ isteklerini dinleyip Trendyol/HB linki geçerse yakalayalım
            yakalanan_link = None
            def on_request(request):
                nonlocal yakalanan_link
                req_url = request.url
                if "trendyol.com" in req_url or "hepsiburada.com" in req_url:
                    if not yakalanan_link:
                        yakalanan_link = req_url

            page.on("request", on_request)

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=25000)
            except Exception:
                pass

            await asyncio.sleep(2)

            # Sayfa içinde doğrudan trendyol/hepsiburada linki var mı tara
            try:
                linkler = await page.eval_on_selector_all("a[href]", "elements => elements.map(e => e.href)")
                for l in linkler:
                    if "trendyol.com" in l or "hepsiburada.com" in l:
                        await browser.close()
                        return {"hedef": l}
            except Exception:
                pass

            # Butonlara tıkla (yeni sekme açarsa onu da yakalamak için context dinle)
            try:
                popup_kapat = await page.query_selector("button.close, .modal-close, [aria-label='Close'], .btn-close")
                if popup_kapat:
                    await popup_kapat.click()
            except Exception:
                pass

            try:
                butonlar = await page.query_selector_all("a, button")
                for b in butonlar:
                    metin = (await b.inner_text()).lower()
                    if "git" in metin or "kampanya" in metin or "fırsat" in metin:
                        await b.click(timeout=3000)
                        break
            except Exception:
                pass

            # Tıklama sonrası yönlenmeyi veya yeni sekmeyi bekle
            for _ in range(10):
                if yakalanan_link:
                    await browser.close()
                    return {"hedef": yakalanan_link}

                for p_item in context.pages:
                    if "trendyol.com" in p_item.url or "hepsiburada.com" in p_item.url:
                        res = p_item.url
                        await browser.close()
                        return {"hedef": res}

                await asyncio.sleep(1)

            sonuc = yakalanan_link or page.url
            await browser.close()
            return {"hedef": sonuc}

    except Exception as e:
        return {"hata": str(e), "hedef": url}
