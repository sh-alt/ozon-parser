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

app = FastAPI(
    title="Ozon Parser Service", 
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Startup event для проверки
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Application starting up...")
    logger.info("✅ Startup complete!")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 Application shutting down...")


class ParseRequest(BaseModel):
    url: str


class ParseResponse(BaseModel):
    title: str
    sku: str
    marketplace: str = "ozon"
    image_url: str | None = None
    price: float | None = None
    old_price: float | None = None
    rating: float | None = None
    reviews_count: int | None = None


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
        # Запуск браузера (как в статье Habr)
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                # '--disable-web-security',
                # '--disable-features=VizDisplayCompositor'
            ],
            # slow_mo=50  # Замедляет действия для имитации человека
        )
        
        # Создание контекста с реалистичными настройками
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='ru-RU',
            timezone_id='Europe/Moscow',
            java_script_enabled=True,
            ignore_https_errors=True
        )
        
        # Агрессивная маскировка автоматизации
        await context.add_init_script("""
            // Удаляем webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () =&gt; undefined
            });
            
            // Фейковые плагины
            Object.defineProperty(navigator, 'plugins', {
                get: () =&gt; [1, 2, 3, 4, 5]
            });
        """)
        
        page = await context.new_page()
        
        # Таймауты (как в статье Habr)
        page.set_default_timeout(15000)
        page.set_default_navigation_timeout(20000)
        
        # Перехват API запросов (для извлечения JSON напрямую)
        api_responses = []
        all_urls = []
        
        async def handle_response(response):
            """Перехватываем API ответы с данными товара"""
            url = response.url
            all_urls.append(url)
            
            # Пытаемся получить JSON из ЛЮБОГО ответа
            if response.status == 200:
                try:
                    # Пробуем распарсить как JSON
                    json_data = await response.json()
                    api_responses.append({
                        'url': url,
                        'data': json_data
                    })
                    logger.info(f"📦 Got JSON from: {url[:100]}...")
                except:
                    # Не JSON - пропускаем
                    pass
        
        page.on("response", handle_response)
        
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
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            
            # Ждём заголовок (как в статье Habr)
            try:
                await page.wait_for_selector("h1", timeout=10000)
            except:
                logger.warning(f"Заголовок не найден: {url}")
            
            await human_delay(3, 6)
            
            # Несколько случайных скроллов
            for _ in range(2):
                scroll_amount = int(random.random() * 400 + 200)
                await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
                await human_delay(1, 3)
            
            # Логируем все URL для отладки
            logger.info(f"📊 Total URLs intercepted: {len(all_urls)}")
            logger.info(f"📊 JSON API responses: {len(api_responses)}")
            
            # Показываем ВСЕ URL (первые 15)
            for i, u in enumerate(all_urls[:15]):
                logger.info(f"  URL #{i+1}: {u}")
            
            # Попытка извлечь данные из JSON API
            json_data = None
            for idx, api_item in enumerate(api_responses):
                api_resp = api_item.get('data', {})
                api_url = api_item.get('url', '')
                
                if isinstance(api_resp, dict):
                    # Логируем ключи для отладки
                    keys = list(api_resp.keys())[:10]  # Первые 10 ключей
                    logger.info(f"API Response #{idx} from {api_url[:80]}...")
                    logger.info(f"  Keys: {keys}")
                    
                    if ('widgetStates' in api_resp or 'title' in api_resp or 'seo' in api_resp):
                        json_data = api_resp
                        logger.info(f"✅ Found product data! Keys: {list(api_resp.keys())[:20]}")
                        break
            
            # Извлечение данных (приоритет - JSON API)
            title = None
            if json_data:
                # Пытаемся извлечь title из JSON
                if 'seo' in json_data and 'title' in json_data['seo']:
                    title = json_data['seo']['title']
                elif 'title' in json_data:
                    title = json_data['title']
            
            # Fallback - парсинг HTML
            if not title:
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
            
            # Извлечение цены
            price = None
            old_price = None
            
            # Попытка 1: текущая цена (основной селектор)
            price_elem = await page.query_selector('span[class*="Price_price"]')
            if not price_elem:
                # Попытка 2: альтернативный селектор
                price_elem = await page.query_selector('div[data-widget="webPrice"] span')
            
            if price_elem:
                price_text = await price_elem.text_content()
                # Очистка: "1 234 ₽" → 1234.0
                price_clean = price_text.replace('₽', '').replace(' ', '').replace('\xa0', '').strip()
                try:
                    price = float(price_clean)
                except ValueError:
                    logger.warning(f"Cannot parse price: {price_text}")
            
            # Старая цена (если есть скидка)
            old_price_elem = await page.query_selector('span[class*="Price_price"][class*="Price_crossed"]')
            if not old_price_elem:
                old_price_elem = await page.query_selector('span[class*="tsBodyControl400Small"]')
            
            if old_price_elem:
                old_price_text = await old_price_elem.text_content()
                old_price_clean = old_price_text.replace('₽', '').replace(' ', '').replace('\xa0', '').strip()
                try:
                    old_price = float(old_price_clean)
                except ValueError:
                    pass
            
            # Извлечение рейтинга
            rating = None
            rating_elem = await page.query_selector('div[class*="Rating"] span')
            if rating_elem:
                rating_text = await rating_elem.text_content()
                try:
                    rating = float(rating_text.strip())
                except ValueError:
                    pass
            
            # Извлечение количества отзывов
            reviews_count = None
            reviews_elem = await page.query_selector('a[href*="#reviews"] span')
            if reviews_elem:
                reviews_text = await reviews_elem.text_content()
                # "1 234 отзыва" → 1234
                reviews_clean = ''.join(filter(str.isdigit, reviews_text))
                if reviews_clean:
                    try:
                        reviews_count = int(reviews_clean)
                    except ValueError:
                        pass
            
            logger.info(f"✅ Parsed: {title[:50]}... | Price: {price}₽ | Rating: {rating}")
            
            return ParseResponse(
                title=title,
                sku=sku,
                image_url=image_url,
                price=price,
                old_price=old_price,
                rating=rating,
                reviews_count=reviews_count
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


@app.get("/health")
async def health():
    """Health check endpoint for Amvera"""
    return {"status": "ok"}


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
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
