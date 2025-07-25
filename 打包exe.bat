@echo off
chcp 65001 >nul
title CAD坐标转换器 - 打包exe工具

echo ================================================
echo CAD坐标转换器 - 打包exe工具
echo 版本: 1.1.0
echo 作者: ViVi141
echo ================================================
echo.

echo 正在检查Python环境...
python --version
if errorlevel 1 (
    echo ❌ 错误: 未找到Python环境
    echo 请先安装Python 3.7或更高版本
    pause
    exit /b 1
)

echo.
echo 正在检查依赖包...
python -c "import matplotlib, numpy, pyautogui, PIL" 2>nul
if errorlevel 1 (
    echo ❌ 错误: 缺少必要的依赖包
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖包安装失败
        pause
        exit /b 1
    )
)

echo.
echo 开始打包exe文件...
python 打包exe.py

echo.
echo 打包完成！按任意键退出...
pause >nul 