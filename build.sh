#!/usr/bin/env bash
# build.sh

echo "🔧 Building the project..."

# Установка зависимостей
pip install -r requirements.txt

# Сбор статических файлов
python manage.py collectstatic --noinput --clear

echo "✅ Build completed"