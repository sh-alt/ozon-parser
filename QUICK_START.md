# ⚡ Быстрый старт - Ozon Parser на Amvera

## 🎯 За 15 минут получишь:
- ✅ Парсинг Ozon БЕЗ прокси
- ✅ Автоматическая ротация IP
- ✅ Обход блокировок Ozon

---

## 📝 Пошаговая инструкция

### 1️⃣ Регистрация (2 мин)
```
1. Открыть https://amvera.io
2. "Войти" → "Через GitHub"
3. Авторизовать
```

### 2️⃣ Закоммитить код (1 мин)
```bash
cd /home/sh-alt/projects/treesum
git add ozon_parser_service/
git commit -m "feat: add Ozon parser for Amvera"
git push origin main
```

### 3️⃣ Создать проект в Amvera (5 мин)
```
1. "Создать проект" → "Из GitHub"
2. Выбрать репозиторий "treesum"
3. Build context: ozon_parser_service
4. Dockerfile path: Dockerfile
5. Port: 8000
6. "Deploy" → подождать 3-5 мин
```

### 4️⃣ Скопировать URL (1 мин)
```
После деплоя получите:
https://ozon-parser-XXXXX.amvera.io

Скопируйте его!
```

### 5️⃣ Настроить backend (2 мин)
```bash
# Добавить в backend/.env
echo "OZON_PARSER_SERVICE_URL=https://ozon-parser-XXXXX.amvera.io" >> backend/.env

# Перезапустить
docker-compose restart backend
```

### 6️⃣ Протестировать (2 мин)
```bash
curl -X POST https://ozon-parser-XXXXX.amvera.io/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.ozon.ru/product/smartfon-apple-iphone-15-128-gb-rozovyy-1475305782/"}'
```

**Ожидаемый ответ:**
```json
{
  "title": "Смартфон Apple iPhone 15 128 ГБ, розовый",
  "sku": "1475305782",
  "marketplace": "ozon",
  "image_url": "https://cdn1.ozone.ru/..."
}
```

---

## ✅ Готово!

Теперь парсинг Ozon работает через Amvera:
- Без прокси
- С ротацией IP
- Бесплатно (Free tier)

---

## 🔄 Если Ozon блокирует

**Просто сделай редеплой:**
```bash
# Любое изменение → новый IP
git commit --allow-empty -m "redeploy for new IP"
git push origin main

# Amvera автоматически задеплоит
# Получишь новый IP!
```

---

## 💡 Подробная инструкция

См. `AMVERA_DEPLOY.md` для детальных инструкций и troubleshooting.
