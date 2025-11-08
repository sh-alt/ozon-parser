"""
Ozon Parser Microservice for Amvera Cloud
Простой FastAPI микросервис для парсинга Ozon
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.async_api import async_playwright
import asyncio
import logging
import random

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Ozon Parser Service", version="1.0.0")


class ParseRequest(BaseModel):
    url: str


class ParseResponse(BaseModel):
    title: str
    sku: str
    marketplace: str = "ozon"
    image_url: str | None = None


async def human_delay(min_sec: float = 1, max_sec: float = 3):
    """Случайная задержка для имитации человека"""
    await asyncio.sleep(random.uniform(min_sec, max_sec))


async def parse_ozon_product(url: str) -> ParseResponse:
    """
    Парсинг товара Ozon через Playwright
    
    Преимущество Amvera: при каждом запуске - новый IP!
    """
    # Извлечь SKU из URL
    import re
    match = re.search(r'-(\d+)/?$', url)
    if not match:
        raise ValueError(f"Cannot extract SKU from URL: {url}")
    
    sku = match.group(1)
    logger.info(f"Parsing Ozon product: SKU={sku}")
    
    async with async_playwright() as p:
        # Запуск браузера
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ]
        )
        
        # Создание контекста с реалистичными настройками
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='ru-RU',
            timezone_id='Europe/Moscow',
        )
        
        # Маскировка автоматизации
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        """)
        
        page = await context.new_page()
        
        try:
            # Сначала заходим на главную (как реальный пользователь)
            logger.info("Visiting Ozon homepage...")
            await page.goto("https://www.ozon.ru/", wait_until="domcontentloaded", timeout=30000)
            await human_delay(3, 5)
            
            # Случайный скролл
            await page.evaluate("window.scrollBy(0, Math.random() * 500 + 200)")
            await human_delay(1, 2)
            
            # Переход на страницу товара
            logger.info(f"Navigating to product page: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await human_delay(3, 6)
            
            # Несколько случайных скроллов
            for _ in range(2):
                scroll_amount = int(random.random() * 400 + 200)
                await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
                await human_delay(1, 3)
            
            # Извлечение данных
            title_elem = await page.query_selector("h1")
            if title_elem:
                title = (await title_elem.text_content()).strip()
            else:
                title = f"Товар Ozon {sku}"
            
            # Извлечение изображения
            image_url = None
            img_elem = await page.query_selector('img[alt*="фото"]')
            if not img_elem:
                img_elem = await page.query_selector('img.w9v_27')
            if img_elem:
                image_url = await img_elem.get_attribute('src')
            
            logger.info(f"✅ Parsed successfully: {title[:50]}...")
            
            return ParseResponse(
                title=title,
                sku=sku,
                image_url=image_url
            )
            
        finally:
            await browser.close()


@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "Ozon Parser",
        "status": "running",
        "version": "1.0.0"
    }


@app.post("/parse", response_model=ParseResponse)
async def parse_product(request: ParseRequest):
    """
    Парсинг товара Ozon
    
    Amvera автоматически меняет IP при каждом деплое!
    """
    try:
        result = await parse_ozon_product(request.url)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Parse error: {e}")
        raise HTTPException(status_code=500, detail=f"Parse error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
