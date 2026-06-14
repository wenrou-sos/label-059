@echo off
chcp 65001 >nul
title 流水线生产模拟器

echo ========================================
echo   流水线生产模拟器 - Factory Pipeline Simulator
echo ========================================
echo.

echo [1/3] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python 环境就绪
echo.

echo [2/3] 检查并安装依赖...
pip show pygame >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装 pygame...
    pip install pygame
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败，请检查网络连接
        pause
        exit /b 1
    )
) else (
    echo [OK] 依赖已安装
)
echo.

echo [3/3] 启动游戏...
echo.
python main.py

if %errorlevel% neq 0 (
    echo.
    echo [错误] 游戏运行出错，请查看上方错误信息
    pause
)
