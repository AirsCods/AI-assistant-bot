#!/bin/bash

IFS='
'
export $(egrep -v '^#' .env | xargs -0)
IFS=
echo "Working branch " $GIT_BRANCH

# Скачиваем или обновляем репозиторий
if [ -d "$PROJECT_TG_DIR" ]; then
  cd $PROJECT_TG_DIR && git pull
  cp /home/wise-dev/update_tg/.penv $PROJECT_TG_DIR/app/.env
else
  git config --global --add safe.directory $PROJECT_TG_DIR
  git clone $GIT_HTTPS_REPO $PROJECT_TG_DIR
  cp /home/wise-dev/update_tg/.penv $PROJECT_TG_DIR/app/.env
  cd $PROJECT_TG_DIR
fi
echo "Start docker-compose in " $PWD

# Собираем и запускаем контейнеры Docker
docker-compose up -d --build

echo "Finish build container!"