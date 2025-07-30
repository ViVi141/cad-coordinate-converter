@echo off
chcp 65001
echo ========================================
echo CAD坐标转换器 - EXE打包脚本
echo ========================================
echo.

echo 正在激活虚拟环境...
call venv_py37\Scripts\activate

echo.
echo 正在清理之前的构建文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "CAD坐标转换器.spec" del "CAD坐标转换器.spec"

echo.
echo 开始打包CAD坐标转换器...
echo.

pyinstaller --onefile ^
    --windowed ^
    --name "CAD坐标转换器" ^
    --icon "favicon.ico" ^
    --add-data "favicon.ico;." ^
    --hidden-import matplotlib ^
    --hidden-import numpy ^
    --hidden-import tkinter ^
    --hidden-import chardet ^
    --hidden-import _tkinter ^
    --collect-all matplotlib ^
    --collect-all numpy ^
    --exclude-module tkinter.test ^
    --exclude-module tkinter.tix ^
    "CAD坐标转换器.py"

echo.
echo ========================================
echo 打包完成！
echo ========================================
echo.
echo EXE文件位置: dist\CAD坐标转换器.exe
echo.
echo 正在测试EXE文件...
if exist "dist\CAD坐标转换器.exe" (
    echo EXE文件创建成功！
    echo 文件大小:
    dir "dist\CAD坐标转换器.exe" | findstr "CAD坐标转换器.exe"
) else (
    echo 错误：EXE文件创建失败！
)

echo.
echo 按任意键退出...
pause > nul 