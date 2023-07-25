#!/bin/bash

# Ожидать доступности базы данных до 25 секунд
echo "Проверка доступности базы данных..."
timeout 25s bash -c 'until echo > /dev/tcp/db/5432; do sleep 1; done'

# Применить миграции Alembic
alembic upgrade head

# Запустить приложение с помощью Gunicorn
echo "Запуск приложения..."
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000