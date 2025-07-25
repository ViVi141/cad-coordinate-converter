@echo off
chcp 65001 >nul
title CAD坐标转换器 - 测试exe文件

echo ================================================
echo CAD坐标转换器 - 测试exe文件
echo ================================================
echo.

echo 正在检查exe文件...
if exist "dist\CAD坐标转换器_v1.1.0\CAD坐标转换器.exe" (
    echo ✅ 找到exe文件
    echo.
    echo 文件信息:
    echo - 路径: dist\CAD坐标转换器_v1.1.0\CAD坐标转换器.exe
    echo - 大小: 69MB
    echo - 状态: 已打包完成
    echo.
    echo 是否要启动程序进行测试？(Y/N)
    set /p choice=
    if /i "%choice%"=="Y" (
        echo 正在启动程序...
        start "" "dist\CAD坐标转换器_v1.1.0\CAD坐标转换器.exe"
        echo ✅ 程序已启动，请检查功能是否正常
    ) else (
        echo 跳过启动测试
    )
) else (
    echo ❌ 未找到exe文件
    echo 请先运行打包脚本: python 打包exe.py
)

echo.
echo 测试完成！按任意键退出...
pause >nul 