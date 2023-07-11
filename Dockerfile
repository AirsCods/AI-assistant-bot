# Используйте официальный образ Python для сборки
FROM python:3.10-slim-bullseye as builder-bot

# Установите рабочую директорию
WORKDIR /app

# Установите Poetry
RUN pip install --no-cache-dir poetry

# Копируйте только файлы, необходимые для установки зависимостей
COPY pyproject.toml /app/

# Установите зависимости проекта
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main

# Используйте официальный образ Python для запуска
FROM python:3.10-slim-bullseye

# Установите рабочую директорию
WORKDIR /app

# Установите ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Копируйте установленные зависимости из стадии сборки
COPY --from=builder-bot /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Копируйте файлы проекта
COPY /app .

# Запустите вашего бота
CMD ["python", "main.py"]
