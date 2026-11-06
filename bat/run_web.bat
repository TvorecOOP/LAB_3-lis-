@echo off
chcp 65001 > nul
cd /d "%~dp0.."
echo ========================================
echo ЗАПУСК ВЕБ-ВЕРСИИ (FastAPI + SQLite)
echo ========================================
echo Перейдите в браузере по адресу: http://localhost:8000
python -m uvicorn web.app:app --reload
pause