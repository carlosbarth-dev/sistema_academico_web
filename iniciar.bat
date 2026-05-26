@echo off
cd /d "%~dp0"

echo ========================================
echo      Sistema Academico Web
echo ========================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo Criando ambiente virtual .venv...
    py -m venv .venv
)

echo Instalando/verificando dependencias...
".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo.
echo Iniciando o sistema...
echo Abra no navegador: http://127.0.0.1:5000
echo Para parar o sistema, feche esta janela ou pressione CTRL+C.
echo.

".venv\Scripts\python.exe" app.py

pause
