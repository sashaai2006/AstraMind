#!/bin/bash
# Скрипт для полного перезапуска AstraMind с DeepSeek

echo "🛑 Останавливаем все процессы..."
pkill -9 -f uvicorn
pkill -9 -f "next dev"
pkill -9 -f "make dev"
sleep 2

echo "🔑 Настройка DeepSeek..."
export LLM_MODE=deepseek
export DEEPSEEK_API_KEY=sk-63dc97e4fa46466583fdd8018a96fe4c

echo "🚀 Запускаем серверы с DeepSeek..."
cd /Users/sasii/Code/projects/AstraMind
make dev

