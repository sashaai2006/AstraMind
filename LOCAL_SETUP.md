# ЗАПУСК ЛОКАЛЬНО НА НОУТБУКЕ

## ШАГ 1: УСТАНОВИТЕ DOCKER

**Mac:**
- Скачайте Docker Desktop: https://www.docker.com/products/docker-desktop
- Установите и запустите

**Windows:**
- Скачайте Docker Desktop: https://www.docker.com/products/docker-desktop
- Установите и запустите

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

## ШАГ 2: ПРОВЕРЬТЕ .env ФАЙЛ

Убедитесь что в `.env` есть:
```
LLM_MODE=groq
GROQ_API_KEY=ваш_ключ_здесь
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## ШАГ 3: ЗАПУСТИТЕ

**Вариант 1 - Автоматически:**
```bash
./START_LOCAL.sh
```

**Вариант 2 - Вручную:**
```bash
# Создайте директории
mkdir -p data projects documents

# Запустите
docker compose up --build -d

# Или если старая версия docker-compose:
docker-compose up --build -d
```

## ШАГ 4: ОТКРОЙТЕ В БРАУЗЕРЕ

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## ПОЛЕЗНЫЕ КОМАНДЫ

Просмотр логов:
```bash
docker compose logs -f
```

Остановка:
```bash
docker compose down
```

Перезапуск:
```bash
docker compose restart
```

Очистка (удалить все контейнеры и образы):
```bash
docker compose down -v
docker system prune -a
```

