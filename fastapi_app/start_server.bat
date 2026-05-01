@echo off
chcp 65001 >nul
echo ========================================
echo 小红书API服务启动脚本
echo ========================================
echo.

cd /d "%~dp0.."

echo 检查Python环境...
python --version
if errorlevel 1 (
    echo [ERROR] Python未安装或不在PATH中
    pause
    exit /b 1
)

echo.
echo 检查依赖包...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [WARNING] FastAPI未安装，正在安装...
    pip install -r fastapi_app\requirements.txt
)

echo.
echo 启动API服务...
echo ========================================
echo API文档地址:
echo   - Swagger UI: http://localhost:8000/docs
echo   - ReDoc: http://localhost:8000/redoc
echo ========================================
echo.
echo 按 Ctrl+C 停止服务
echo.

python -m fastapi_app.main

pause