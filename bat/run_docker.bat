@echo off
chcp 65001 > nul
cd /d "%~dp0.."
echo ========================================
echo ЗАПУСК ВЕБ-ВЕРСИИ И БД В DOCKER
echo ========================================
echo Перейдите в браузере по адресу: http://localhost:8000
docker-compose up --build
pause