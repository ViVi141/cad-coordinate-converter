@echo off
chcp 65001 >nul
echo ========================================
echo CAD坐标转换器 - 依赖安装脚本
echo ========================================
echo.

echo 正在检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo 错误：未找到Python环境，请先安装Python 3.7+
    pause
    exit /b 1
)

echo.
echo 正在安装依赖包...
echo.

echo 安装matplotlib...
pip install matplotlib>=3.3.0
if %errorlevel% neq 0 (
    echo 警告：matplotlib安装失败，图形预览功能将不可用
)

echo.
echo 安装numpy...
pip install numpy>=1.19.0
if %errorlevel% neq 0 (
    echo 警告：numpy安装失败
)

echo.
echo 安装chardet...
pip install chardet>=4.0.0
if %errorlevel% neq 0 (
    echo 警告：chardet安装失败，文件编码检测功能可能受影响
)

echo.
echo ========================================
echo 依赖安装完成！
echo ========================================
echo.
echo 现在可以运行 CAD坐标转换器.py 启动程序
echo.
pause 