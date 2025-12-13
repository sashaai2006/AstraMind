#!/bin/bash
# Скрипт для запуска AstraMind локально

echo "🚀 Запуск AstraMind локально..."

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен!"
    echo "Установите Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose не установлен!"
    exit 1
fi

# Проверка .env файла
if [ ! -f .env ]; then
    echo "📝 Создание .env файла..."
    cat > .env << 'EOF'
LLM_MODE=groq
GROQ_API_KEY=ваш_groq_ключ_здесь
DEEPSEEK_API_KEY=
GITHUB_TOKEN=
CEREBRAS_API_KEY=
ADMIN_API_KEY=
LLM_SEMAPHORE=10
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
EOF
    echo "⚠️  Отредактируйте .env файл и добавьте ваш Groq API ключ!"
    echo "   nano .env"
    read -p "Нажмите Enter после редактирования .env файла..."
fi

# Создание директорий
echo "📁 Создание директорий..."
mkdir -p data projects documents

# Запуск
echo "🔨 Сборка и запуск..."
if docker compose version &> /dev/null; then
    docker compose up --build -d
else
    docker-compose up --build -d
fi

echo ""
echo "✅ Готово!"
echo ""
echo "🌐 Приложение доступно:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Просмотр логов:"
if command -v docker-compose &> /dev/null; then
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 Остановка:"
    echo "   docker-compose down"
else
    echo "   docker compose logs -f"
    echo ""
    echo "🛑 Остановка:"
    echo "   docker compose down"
fi

