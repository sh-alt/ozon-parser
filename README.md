# Ozon Parser Microservice для Amvera Cloud

Микросервис для парсинга товаров Ozon с автоматической ротацией IP через Amvera Cloud.

## ⚠️ Важно: Требуются прокси!

**Ozon блокирует автоматизацию** через anti-bot систему (abt-challenge). Для работы парсера **ОБЯЗАТЕЛЬНО** нужны прокси!

### Настройка прокси в Amvera:

1. В Amvera Dashboard → Переменные окружения → добавить:
   ```
   OZON_PROXY_URL=mobpool.proxy.market:10000@username:password
   ```

2. Формат: `server:port@username:password`

3. Пример (mobpool):
   ```
   OZON_PROXY_URL=mobpool.proxy.market:10000@cyqNcQLcZYMt:d4DS2q5j
   ```

## 🎯 Преимущества Amvera

- ✅ **Автоматическая ротация IP** - при каждом деплое новый IP
- ✅ **Бесплатный tier** - достаточно для тестирования
- ✅ **Простой деплой** - через GitHub
- ✅ **Обход блокировок Ozon** - разные IP при каждом запуске

## 🚀 Деплой на Amvera

### Шаг 1: Регистрация

1. Зайти на https://amvera.io
2. Зарегистрироваться (можно через GitHub)
3. Создать новый проект

### Шаг 2: Подключение репозитория

1. В Amvera: "Создать проект" → "Из GitHub"
2. Выбрать репозиторий `treesum`
3. Указать путь к сервису: `ozon_parser_service`
4. Выбрать Dockerfile

### Шаг 3: Настройка

**Build settings:**
- Build context: `ozon_parser_service`
- Dockerfile path: `Dockerfile`

**Environment variables:**
- Не требуются (прокси не нужны!)

### Шаг 4: Деплой

1. Нажать "Deploy"
2. Подождать 3-5 минут
3. Получить URL: `https://your-project.amvera.io`

## 📡 API

### Health Check
```bash
GET https://your-project.amvera.io/
```

### Парсинг товара
```bash
POST https://your-project.amvera.io/parse
Content-Type: application/json

{
  "url": "https://www.ozon.ru/product/smartfon-apple-iphone-15-128-gb-rozovyy-1475305782/"
}
```

**Ответ:**
```json
{
  "title": "Смартфон Apple iPhone 15 128 ГБ, розовый",
  "sku": "1475305782",
  "marketplace": "ozon",
  "image_url": "https://cdn1.ozone.ru/s3/multimedia-1/...",
  "price": 79990.0,
  "old_price": 89990.0,
  "rating": 4.8,
  "reviews_count": 1234
}
```

## 🔗 Интеграция с основным backend

### Вариант 1: Прямой вызов

```python
# backend/app/parsers/ozon.py
import httpx

AMVERA_PARSER_URL = "https://your-project.amvera.io"

async def parse_via_amvera(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AMVERA_PARSER_URL}/parse",
            json={"url": url},
            timeout=60.0
        )
        return response.json()
```

### Вариант 2: Через environment variable

```bash
# backend/.env
OZON_PARSER_SERVICE_URL=https://your-project.amvera.io
```

```python
# backend/app/config.py
class Settings(BaseSettings):
    OZON_PARSER_SERVICE_URL: str = None
```

## 🧪 Локальное тестирование

```bash
# Запуск локально
cd ozon_parser_service
pip install -r requirements.txt
playwright install chromium
python main.py

# Тест
curl -X POST http://localhost:8000/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.ozon.ru/product/smartfon-apple-iphone-15-128-gb-rozovyy-1475305782/"}'
```

## 💰 Стоимость

**Amvera Free Tier:**
- 512 MB RAM
- 0.5 CPU
- Достаточно для парсинга!

**Платный план (если нужно больше):**
- От 200₽/месяц
- 1 GB RAM
- 1 CPU

## 📊 Мониторинг

В Amvera dashboard можно смотреть:
- Логи приложения
- Использование ресурсов
- Статистику запросов
- Ошибки

## 🔄 Автодеплой

При пуше в `main` ветку - автоматический деплой!

```bash
git add ozon_parser_service/
git commit -m "feat: add Ozon parser microservice for Amvera"
git push origin main
```

## 🐛 Troubleshooting

### Ошибка "Timeout"
- Увеличить timeout в настройках Amvera
- Проверить логи

### Ошибка "Out of memory"
- Перейти на платный план
- Или уменьшить количество одновременных запросов

### Ozon всё равно блокирует
- Подождать и попробовать снова (новый IP при следующем деплое)
- Добавить больше задержек в код
- Использовать комбо: Amvera + прокси
