# АЛЬТЕРНАТИВНЫЕ БЕСПЛАТНЫЕ ВАРИАНТЫ РАЗВЕРТЫВАНИЯ

## ВАРИАНТ 1: RENDER (РЕКОМЕНДУЮ - БЕСПЛАТНО 750 ЧАСОВ/МЕСЯЦ)
-----------------------------------------------------------

1. Зарегистрируйтесь: https://render.com
2. New → Web Service
3. Подключите GitHub репозиторий
4. Настройки:
   - Name: astramind-backend
   - Environment: Docker
   - Dockerfile Path: `Dockerfile.backend`
   - Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. Variables (Environment Variables):
   - `LLM_MODE=groq`
   - `GROQ_API_KEY=ваш_ключ`
   - `PORT=10000` (Render использует свой порт)
6. Deploy!

**Плюсы:** Бесплатно, автоматический HTTPS, просто


## ВАРИАНТ 2: FLY.IO (БЕСПЛАТНО 3 VM)
------------------------------------

1. Установите flyctl: `curl -L https://fly.io/install.sh | sh`
2. Зарегистрируйтесь: `fly auth signup`
3. Создайте приложение: `fly launch`
4. Следуйте инструкциям
5. Добавьте переменные: `fly secrets set GROQ_API_KEY=ваш_ключ LLM_MODE=groq`

**Плюсы:** Быстро, глобальная сеть


## ВАРИАНТ 3: ORACLE CLOUD (БЕСПЛАТНО НАВСЕГДА!)
------------------------------------------------

1. Зарегистрируйтесь: https://www.oracle.com/cloud/free/
2. Создайте VM (Always Free):
   - Shape: VM.Standard.A1.Flex (4GB RAM, 1 CPU)
   - OS: Ubuntu 22.04
3. Подключитесь: `ssh ubuntu@ваш-ip`
4. Установите Docker:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
```
5. Установите Docker Compose:
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
6. Клонируйте проект:
```bash
git clone ваш-репозиторий astramind
cd astramind
```
7. Создайте .env:
```bash
nano .env
# Добавьте:
LLM_MODE=groq
GROQ_API_KEY=ваш_ключ
NEXT_PUBLIC_API_BASE_URL=http://ваш-ip:8000
ADMIN_API_KEY=случайный_ключ
```
8. Запустите:
```bash
docker-compose up -d
```

**Плюсы:** БЕСПЛАТНО НАВСЕГДА, полный контроль, 4GB RAM


## ВАРИАНТ 4: GOOGLE CLOUD RUN (БЕСПЛАТНЫЙ TIER)
------------------------------------------------

1. Зарегистрируйтесь: https://cloud.google.com (есть $300 кредитов)
2. Установите gcloud CLI
3. Создайте проект
4. Разверните:
```bash
gcloud run deploy astramind \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Плюсы:** Масштабируется автоматически, платите только за использование


## ВАРИАНТ 5: ЛОКАЛЬНЫЙ СЕРВЕР/ДОМАШНИЙ ПК
------------------------------------------

Если у вас есть старый компьютер или Raspberry Pi:

1. Установите Ubuntu Server
2. Установите Docker (инструкции выше)
3. Запустите через docker-compose
4. Настройте port forwarding на роутере
5. Используйте бесплатный DDNS (noip.com, duckdns.org)

**Плюсы:** Полностью бесплатно, полный контроль


## ВАРИАНТ 6: CODEPIPELINE + AWS LAMBDA (СЛОЖНО, НО БЕСПЛАТНО)
-------------------------------------------------------------

Для продвинутых пользователей. Сложная настройка, но бесплатно для небольших проектов.


## МОЯ РЕКОМЕНДАЦИЯ
-------------------

**Для быстрого старта:** Render.com
- Проще всего
- Бесплатно 750 часов/месяц
- Автоматический HTTPS

**Для долгосрочного использования:** Oracle Cloud
- Бесплатно навсегда
- 4GB RAM достаточно
- Полный контроль

**Для обучения:** Локальный сервер
- Полностью бесплатно
- Учитесь на практике

