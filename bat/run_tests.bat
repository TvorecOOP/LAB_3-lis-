@echo off
chcp 65001 > nul
cd /d "%~dp0.."
echo ========================================
echo ЗАПУСК ТЕСТОВ (pytest)
echo ========================================
python -m pytest tests/ -v
pause