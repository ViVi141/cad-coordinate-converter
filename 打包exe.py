#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CAD坐标转换器 - 打包exe脚本
版本: 1.1.0
作者: ViVi141
邮箱: 747384120@qq.com
描述: 将CAD坐标转换器打包成exe可执行文件
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        print(f"✅ PyInstaller已安装，版本: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("❌ PyInstaller未安装")
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller安装失败: {e}")
        return False

def create_spec_file():
    """创建PyInstaller的spec配置文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['CAD坐标转换器.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('favicon.ico', '.'),
        ('CAD坐标转换器使用手册(非技术人员版).md', '.'),
        ('CAD坐标转换器使用手册(非技术人员版).pdf', '.'),
        ('README.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.backends.backend_tkagg',
        'numpy',
        'pyautogui',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CAD坐标转换器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='favicon.ico',
    version_file=None,
)
'''
    
    with open('CAD坐标转换器.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✅ 已创建spec配置文件")

def build_exe():
    """构建exe文件"""
    print("开始构建exe文件...")
    
    # 检查必要文件
    required_files = [
        'CAD坐标转换器.py',
        'favicon.ico',
        'requirements.txt'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ 缺少必要文件: {file}")
            return False
    
    # 创建spec文件
    create_spec_file()
    
    # 执行PyInstaller打包
    try:
        print("正在执行PyInstaller打包...")
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",  # 清理临时文件
            "--noconfirm",  # 不询问覆盖
            "CAD坐标转换器.spec"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if result.returncode == 0:
            print("✅ exe文件构建成功！")
            return True
        else:
            print(f"❌ 构建失败，错误信息:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 构建过程中出现错误: {e}")
        return False

def check_dependencies():
    """检查依赖包是否已安装"""
    print("检查依赖包...")
    
    dependencies = [
        'matplotlib',
        'numpy', 
        'pyautogui',
        'PIL'
    ]
    
    missing_deps = []
    
    for dep in dependencies:
        try:
            if dep == 'PIL':
                import PIL
                print(f"✅ {dep} 已安装")
            else:
                __import__(dep)
                print(f"✅ {dep} 已安装")
        except ImportError:
            print(f"❌ {dep} 未安装")
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"\n需要安装以下依赖包: {', '.join(missing_deps)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True

def create_distribution():
    """创建发布包"""
    print("创建发布包...")
    
    # 检查exe文件是否存在
    exe_path = Path("dist/CAD坐标转换器.exe")
    if not exe_path.exists():
        print("❌ 未找到exe文件，尝试查找其他位置...")
        # 尝试在其他位置查找exe文件
        possible_paths = [
            Path("dist/CAD坐标转换器.exe"),
            Path("build/CAD坐标转换器/CAD坐标转换器.exe"),
            Path("CAD坐标转换器.exe")
        ]
        
        for path in possible_paths:
            if path.exists():
                print(f"✅ 找到exe文件: {path}")
                exe_path = path
                break
        else:
            print("❌ 在所有可能位置都未找到exe文件")
            return False
    
    # 创建发布目录
    dist_dir = Path("dist")
    if not dist_dir.exists():
        dist_dir.mkdir()
    
    release_dir = dist_dir / "CAD坐标转换器_v1.1.0"
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # 复制exe文件
    try:
        shutil.copy2(exe_path, release_dir / "CAD坐标转换器.exe")
        print("✅ 已复制exe文件")
    except Exception as e:
        print(f"❌ 复制exe文件失败: {e}")
        return False
    
    # 复制其他文件
    files_to_copy = [
        ("CAD坐标转换器使用手册(非技术人员版).md", "CAD坐标转换器使用手册(非技术人员版).md"),
        ("CAD坐标转换器使用手册(非技术人员版).pdf", "CAD坐标转换器使用手册(非技术人员版).pdf"),
        ("README.md", "README.md"),
        ("LICENSE", "LICENSE")
    ]
    
    for src_file, dst_file in files_to_copy:
        try:
            if Path(src_file).exists():
                shutil.copy2(src_file, release_dir / dst_file)
                print(f"✅ 已复制: {src_file}")
            else:
                print(f"⚠️ 文件不存在: {src_file}")
        except Exception as e:
            print(f"❌ 复制文件失败 {src_file}: {e}")
    
    # 创建使用说明
    readme_content = """# CAD坐标转换器 v1.1.0

## 使用说明

1. 双击运行 `CAD坐标转换器.exe`
2. 选择包含坐标数据的TXT文件
3. 选择转换类型（多段线/直线/点）
4. 设置是否添加文字标注
5. 点击"开始转换"
6. 复制生成的CAD命令到CAD软件中使用

## 支持格式

- X,Y 坐标: 447677.9778, 2491585.3947
- X,Y,Z 坐标: 447677.9778, 2491585.3947, 100.5
- 分组标识: 第1组、第2组等

## 系统要求

- Windows 7/8/10/11
- 无需安装Python环境
- 支持32位和64位系统

## 作者信息

作者: ViVi141
邮箱: 747384120@qq.com
版本: 1.1.0

## 许可证

详见 LICENSE 文件
"""
    
    try:
        with open(release_dir / "使用说明.txt", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("✅ 已创建使用说明文件")
    except Exception as e:
        print(f"❌ 创建使用说明文件失败: {e}")
    
    print(f"✅ 发布包已创建: {release_dir}")
    return True

def main():
    """主函数"""
    print("=" * 50)
    print("CAD坐标转换器 - 打包exe工具")
    print("版本: 1.1.0")
    print("作者: ViVi141")
    print("=" * 50)
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 7):
        print("❌ Python版本过低，需要Python 3.7或更高版本")
        return
    
    # 检查操作系统
    system = platform.system()
    print(f"操作系统: {system}")
    
    if system != "Windows":
        print("⚠️ 警告: 此脚本主要针对Windows系统优化")
    
    # 检查PyInstaller
    if not check_pyinstaller():
        print("\n正在安装PyInstaller...")
        if not install_pyinstaller():
            print("❌ 无法安装PyInstaller，请手动安装")
            return
    
    # 检查依赖
    if not check_dependencies():
        print("\n请先安装依赖包:")
        print("pip install -r requirements.txt")
        return
    
    print("\n开始打包流程...")
    
    # 构建exe
    if build_exe():
        # 创建发布包
        if create_distribution():
            print("\n🎉 打包完成！")
            print("发布包位置: dist/CAD坐标转换器_v1.1.0/")
            print("包含文件:")
            print("- CAD坐标转换器.exe (主程序)")
            print("- 使用说明.txt (使用说明)")
            print("- CAD坐标转换器使用手册(非技术人员版).md")
            print("- CAD坐标转换器使用手册(非技术人员版).pdf")
            print("- README.md")
            print("- LICENSE")
        else:
            print("❌ 创建发布包失败")
    else:
        print("❌ 构建exe失败")

if __name__ == "__main__":
    main() 