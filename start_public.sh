#!/bin/bash
# Скрипт для быстрого публичного доступа через ngrok

echo "🚀 Запуск публичного доступа..."
echo ""

# Проверка установки ngrok
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok не установлен!"
    echo ""
    echo "Установите ngrok:"
    echo "  macOS: brew install ngrok"
    echo "  Или скачайте: https://ngrok.com/download"
    echo ""
    echo "После установки зарегистрируйтесь и получите токен:"
    echo "  ngrok config add-authtoken YOUR_TOKEN"
    exit 1
fi

# Проверка запущенных контейнеров
if ! docker ps | grep -q astramind-frontend; then
    echo "⚠️  Frontend контейнер не запущен. Запускаю..."
    cd "$(dirname "$0")"
    docker compose up -d frontend
    sleep 3
fi

if ! docker ps | grep -q astramind-backend; then
    echo "⚠️  Backend контейнер не запущен. Запускаю..."
    cd "$(dirname "$0")"
    docker compose up -d backend
    sleep 3
fi

echo "✅ Контейнеры запущены"
echo ""
echo "🌐 Запускаю ngrok туннель на порт 3000..."
echo "   Публичный URL будет показан ниже"
echo ""
echo "⚠️  ВАЖНО:"
echo "   - Бесплатный ngrok имеет ограничения (время сессии)"
echo "   - URL будет меняться при каждом перезапуске"
echo "   - Для постоянного доступа используйте Render (см. DEPLOY.md)"
echo ""

# Запуск ngrok
ngrok http 3000

