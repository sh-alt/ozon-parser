# 🚀 Деплой Ozon Parser на Amvera Cloud

**Время:** 15-20 минут  
**Стоимость:** Бесплатно (Free tier)

## 📋 Что получим

✅ Парсинг Ozon **без прокси**  
✅ Автоматическая **ротация IP** при каждом деплое  
✅ **Обход блокировок** Ozon  
✅ Простая интеграция с основным backend  

---

## Шаг 1: Регистрация на Amvera (2 мин)

1. Зайти на https://amvera.io
2. Нажать "Войти" → "Через GitHub"
3. Авторизовать Amvera

---

## Шаг 2: Подготовка репозитория (3 мин)

### Вариант A: Использовать существующий репозиторий

```bash
cd /home/sh-alt/projects/treesum

# Проверить что файлы созданы
ls -la ozon_parser_service/
# Должны быть: main.py, requirements.txt, Dockerfile, README.md

# Закоммитить
git add ozon_parser_service/
git commit -m "feat: add Ozon parser microservice for Amvera"
git push origin main
```

### Вариант B: Создать отдельный репозиторий (рекомендуется)

```bash
cd /home/sh-alt/projects/treesum/ozon_parser_service

# Инициализировать git
git init
git add .
git commit -m "Initial commit: Ozon parser microservice"

# Создать репозиторий на GitHub
# https://github.com/new
# Название: ozon-parser-service

# Подключить remote
git remote add origin https://github.com/YOUR_USERNAME/ozon-parser-service.git
git branch -M main
git push -u origin main
```

---

## Шаг 3: Создание проекта на Amvera (5 мин)

### 3.1 Создать проект

1. В Amvera dashboard: **"Создать проект"**
2. Выбрать **"Из GitHub"**
3. Выбрать репозиторий:
   - Если Вариант A: `treesum`
   - Если Вариант B: `ozon-parser-service`

### 3.2 Настроить build

**Build Configuration:**
```
Build context: ozon_parser_service  (если Вариант A)
Build context: .                     (если Вариант B)

Dockerfile path: Dockerfile

Port: 8000
```

**Environment Variables:**
- Не требуются! (прокси не нужны)

### 3.3 Запустить деплой

1. Нажать **"Deploy"**
2. Подождать 3-5 минут
3. Статус должен стать **"Running"**

### 3.4 Получить URL

После деплоя получите URL вида:
```
https://ozon-parser-XXXXX.amvera.io
```

Скопируйте его!

---

## Шаг 4: Тестирование (3 мин)

### 4.1 Health check

```bash
curl https://ozon-parser-XXXXX.amvera.io/
```

**Ожидаемый ответ:**
```json
{
  "service": "Ozon Parser",
  "status": "running",
  "version": "1.0.0"
}
```

### 4.2 Тест парсинга

```bash
curl -X POST https://ozon-parser-XXXXX.amvera.io/parse \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.ozon.ru/product/smartfon-apple-iphone-15-128-gb-rozovyy-1475305782/"
  }'
```

**Ожидаемый ответ:**
```json
{
  "title": "Смартфон Apple iPhone 15 128 ГБ, розовый",
  "sku": "1475305782",
  "marketplace": "ozon",
  "image_url": "https://cdn1.ozone.ru/s3/multimedia-1/..."
}
```

---

## Шаг 5: Интеграция с backend (5 мин)

### 5.1 Добавить URL в .env

```bash
# backend/.env
OZON_PARSER_SERVICE_URL=https://ozon-parser-XXXXX.amvera.io
```

### 5.2 Перезапустить backend

```bash
docker-compose restart backend
```

### 5.3 Проверить логи

```bash
docker-compose logs backend | grep -i ozon
```

Должно быть:
```
INFO:app.parsers:Using OzonAmveraParser for https://www.ozon.ru/...
```

---

## Шаг 6: Тестирование интеграции (2 мин)

```bash
docker-compose exec -T backend python3 << 'PYEOF'
import asyncio
import sys
sys.path.insert(0, '/app')

async def test():
    from app.parsers import get_parser
    
    url = "https://www.ozon.ru/product/smartfon-apple-iphone-15-128-gb-rozovyy-1475305782/"
    parser = get_parser(url)
    
    print(f"Parser: {parser.__class__.__name__}")
    
    result = await parser.parse_preview(url)
    print(f"Title: {result.title}")
    print(f"SKU: {result.sku}")
    print("✅ SUCCESS!")

asyncio.run(test())
PYEOF
```

**Ожидаемый вывод:**
```
Parser: OzonAmveraParser
Title: Смартфон Apple iPhone 15 128 ГБ, розовый
SKU: 1475305782
✅ SUCCESS!
```

---

## 🎉 Готово!

Теперь парсинг Ozon работает через Amvera Cloud:
- ✅ Без прокси
- ✅ С ротацией IP
- ✅ Обход блокировок

---

## 🔄 Автодеплой

При пуше в `main` ветку - автоматический деплой!

```bash
# Внести изменения в ozon_parser_service/main.py
git add ozon_parser_service/
git commit -m "feat: improve parsing logic"
git push origin main

# Amvera автоматически задеплоит новую версию
# Новый IP будет назначен!
```

---

## 💰 Стоимость

**Free Tier (достаточно для тестирования):**
- 512 MB RAM
- 0.5 CPU
- Бесплатно навсегда

**Если нужно больше:**
- От 200₽/месяц
- 1 GB RAM
- 1 CPU

---

## 🐛 Troubleshooting

### Ошибка при деплое

**Проблема:** Build failed  
**Решение:**
1. Проверить логи в Amvera dashboard
2. Убедиться что Dockerfile корректный
3. Проверить requirements.txt

### Timeout при парсинге

**Проблема:** Request timeout  
**Решение:**
1. Увеличить timeout в Amvera настройках
2. Или в коде: `httpx.AsyncClient(timeout=120.0)`

### Ozon всё равно блокирует

**Проблема:** "Доступ ограничен"  
**Решение:**
1. Подождать и попробовать снова (новый IP)
2. Сделать редеплой (новый IP)
3. Увеличить задержки в `main.py`
4. Комбо: Amvera + прокси (добавить в микросервис)

---

## 📊 Мониторинг

В Amvera dashboard:
- **Логи** - смотреть ошибки парсинга
- **Метрики** - CPU, RAM usage
- **Статистика** - количество запросов

---

## 🔗 Полезные ссылки

- Amvera Dashboard: https://amvera.io/dashboard
- Документация Amvera: https://docs.amvera.io
- Статья на Habr: https://habr.com/ru/companies/amvera/articles/960280/
