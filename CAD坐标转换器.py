#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CAD坐标转换器
版本: 1.3.0
作者: ViVi141
邮箱: 747384120@qq.com
描述: 将TXT格式的坐标数据转换为CAD图形绘制命令的桌面GUI程序
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import re
import os
import sys
import platform
import threading
import tempfile
import subprocess
import gc
from typing import List, Tuple, Dict, Optional
import chardet

# 剪贴板使用tkinter内置功能
print("✅ 使用tkinter内置剪贴板功能")

# 版本信息
VERSION = "1.3.0"
AUTHOR = "ViVi141"
EMAIL = "747384120@qq.com"

# 全局线程锁，用于保护剪贴板操作
CLIPBOARD_LOCK = threading.Lock()

# 检查matplotlib可用性
HAS_MATPLOTLIB = False
MATPLOTLIB_VERSION = None
try:
    import matplotlib
    MATPLOTLIB_VERSION = matplotlib.__version__
    # 检查版本兼容性
    version_parts = [int(x) for x in MATPLOTLIB_VERSION.split('.')]
    if version_parts[0] >= 3 and version_parts[1] >= 3:
        # 设置matplotlib后端为TkAgg，避免创建额外进程
        matplotlib.use('TkAgg')
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import numpy as np
        HAS_MATPLOTLIB = True
        
        # 设置matplotlib中文字体
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        # 禁用matplotlib的交互模式，减少进程创建
        plt.ioff()
        
    else:
        print(f"警告：matplotlib版本过低({MATPLOTLIB_VERSION})，建议使用3.3.0以上版本")
        
except ImportError:
    print("警告：matplotlib未安装，图形预览功能不可用")

class CAD坐标转换器:
    def __init__(self, root):
        self.root = root
        self.root.title(f"CAD坐标转换器 v{VERSION} - {AUTHOR}")
        self.root.configure(bg='#f8f9fa')
        
        # 检查系统兼容性
        self.check_system_compatibility()
        
        # 设置字体
        self.font_normal = ('Microsoft YaHei', 9)
        self.font_title = ('Microsoft YaHei', 14, 'bold')
        self.font_subtitle = ('Microsoft YaHei', 11, 'bold')
        
        # 存储坐标数据
        self.coordinates = []
        self.coordinate_groups = {}  # 存储分组坐标数据
        
        # 添加配置选项
        self.config = {
            'max_file_size_mb': 50,  # 最大文件大小(MB)
            'max_coordinates': 50000,  # 最大坐标数量
            'max_display_points': 2000,  # 图形预览最大点数
            'auto_save_preview': True,  # 自动保存预览
            'enable_logging': True,  # 启用日志
        }
        
        # 初始化日志
        if self.config['enable_logging']:
            self.setup_logging()
        
        self.setup_ui()
        
    def setup_logging(self):
        """设置日志系统"""
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('cad_converter.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"CAD坐标转换器 v{VERSION} 启动")
        
    def check_system_compatibility(self):
        """检查系统兼容性"""
        system_info = platform.system() + " " + platform.release()
        python_version = sys.version.split()[0]
        
        print(f"CAD坐标转换器 v{VERSION}")
        print(f"作者: {AUTHOR} ({EMAIL})")
        print(f"系统信息: {system_info}")
        print(f"Python版本: {python_version}")
        print(f"matplotlib可用: {HAS_MATPLOTLIB}")
        if HAS_MATPLOTLIB and MATPLOTLIB_VERSION:
            print(f"matplotlib版本: {MATPLOTLIB_VERSION}")
        print("✅ 使用tkinter内置剪贴板功能")
        
        # 显示兼容性信息
        if not HAS_MATPLOTLIB:
            messagebox.showwarning("兼容性提示", 
                "matplotlib未安装或版本过低，图形预览功能不可用。\n"
                "建议运行'pip install matplotlib>=3.3.0'安装依赖包。")
        
        # 记录系统信息
        if hasattr(self, 'logger'):
            self.logger.info(f"系统信息: {system_info}")
            self.logger.info(f"Python版本: {python_version}")
            self.logger.info(f"matplotlib可用: {HAS_MATPLOTLIB}")

    def detect_file_encoding(self, file_path: str) -> str:
        """检测文件编码"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                confidence = result['confidence']
                
                if hasattr(self, 'logger'):
                    self.logger.info(f"检测到文件编码: {encoding}, 置信度: {confidence:.2f}")
                
                # 如果置信度较低，尝试常见编码
                if confidence < 0.7:
                    for test_encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
                        try:
                            with open(file_path, 'r', encoding=test_encoding) as f:
                                f.read()
                            encoding = test_encoding
                            if hasattr(self, 'logger'):
                                self.logger.info(f"使用备用编码: {encoding}")
                            break
                        except UnicodeDecodeError:
                            continue
                
                return encoding
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"编码检测失败: {e}")
            return 'utf-8'  # 默认使用UTF-8

    def safe_read_file(self, file_path: str) -> str:
        """安全读取文件，支持多种编码"""
        try:
            # 检测文件编码
            encoding = self.detect_file_encoding(file_path)
            
            # 尝试读取文件
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            if hasattr(self, 'logger'):
                self.logger.info(f"成功读取文件: {file_path}, 编码: {encoding}")
            
            return content
            
        except UnicodeDecodeError as e:
            # 如果检测的编码失败，尝试其他编码
            for fallback_encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig', 'latin-1']:
                try:
                    with open(file_path, 'r', encoding=fallback_encoding) as f:
                        content = f.read()
                    
                    if hasattr(self, 'logger'):
                        self.logger.info(f"使用备用编码读取成功: {fallback_encoding}")
                    
                    return content
                except UnicodeDecodeError:
                    continue
            
            # 所有编码都失败
            raise Exception(f"无法读取文件，所有编码尝试都失败: {e}")
            
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"文件读取失败: {e}")
            raise

    def validate_file_path(self, file_path: str) -> bool:
        """验证文件路径安全性"""
        try:
            # 检查路径是否包含危险字符
            dangerous_chars = ['..', '\\', '/', ':', '*', '?', '"', '<', '>', '|']
            for char in dangerous_chars:
                if char in file_path:
                    return False
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return False
            
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            max_size = self.config['max_file_size_mb'] * 1024 * 1024
            if file_size > max_size:
                return False
            
            return True
            
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"文件路径验证失败: {e}")
            return False

    def improved_parse_coordinates(self, content: str) -> Tuple[List[Tuple[float, float, float]], Dict[str, List[Tuple[float, float, float]]]]:
        """改进的坐标解析函数"""
        coordinates = []
        groups = {}
        current_group = "默认组"
        
        # 更灵活的坐标正则表达式
        coord_patterns = [
            # 标准格式: x,y 或 x,y,z
            re.compile(r'(\d+\.?\d*)\s*[,，]\s*(\d+\.?\d*)\s*[,，]?\s*(\d+\.?\d*)?'),
            # 空格分隔: x y z
            re.compile(r'(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)?'),
            # 制表符分隔: x\ty\tz
            re.compile(r'(\d+\.?\d*)\t(\d+\.?\d*)\t?(\d+\.?\d*)?'),
            # 分号分隔: x;y;z
            re.compile(r'(\d+\.?\d*)\s*[;；]\s*(\d+\.?\d*)\s*[;；]?\s*(\d+\.?\d*)?'),
        ]
        
        lines = content.split('\n')
        line_number = 0
        
        for line in lines:
            line_number += 1
            line = line.strip()
            
            # 跳过空行和注释
            if not line or line.startswith('#') or line.startswith('//'):
                continue
            
            # 检查分组标识
            if any(keyword in line for keyword in ['第', '组', 'group', 'Group']):
                current_group = line
                if current_group not in groups:
                    groups[current_group] = []
                continue
            
            # 尝试多种格式匹配坐标
            coord_found = False
            for pattern in coord_patterns:
                matches = pattern.findall(line)
                for match in matches:
                    try:
                        x = float(match[0])
                        y = float(match[1])
                        z = float(match[2]) if match[2] else 0.0
                        
                        # 验证坐标值的合理性
                        if abs(x) > 1e9 or abs(y) > 1e9 or abs(z) > 1e9:
                            if hasattr(self, 'logger'):
                                self.logger.warning(f"第{line_number}行: 坐标值过大，跳过: {x},{y},{z}")
                            continue
                        
                        coord = (x, y, z)
                        coordinates.append(coord)
                        
                        # 添加到分组
                        if current_group not in groups:
                            groups[current_group] = []
                        groups[current_group].append(coord)
                        
                        coord_found = True
                        break
                        
                    except ValueError as e:
                        if hasattr(self, 'logger'):
                            self.logger.warning(f"第{line_number}行: 坐标解析失败: {line}, 错误: {e}")
                        continue
            
            if not coord_found and line.strip():
                if hasattr(self, 'logger'):
                    self.logger.warning(f"第{line_number}行: 无法解析的坐标格式: {line}")
        
        if hasattr(self, 'logger'):
            self.logger.info(f"解析完成: 共{len(coordinates)}个坐标点，{len(groups)}个分组")
        
        return coordinates, groups

    def show_help(self):
        """显示帮助信息"""
        help_text = f"""
CAD坐标转换器 v{VERSION} - 使用说明

使用说明:
1. 选择包含坐标数据的TXT文件
2. 选择转换类型（pline/line/point）
3. 设置是否添加文字标注
4. 选择是否按分组分别处理（可选）
5. 点击"转换坐标"按钮
6. 复制生成的CAD命令到CAD软件中使用

支持格式:
- X,Y 坐标: 447677.9778, 2491585.3947
- X,Y,Z 坐标: 447677.9778, 2491585.3947, 100.5
- 分组标识: 第1组、第2组等

分组处理:
- 默认忽略分组，所有坐标合并处理
- 勾选"按分组分别处理"可分别生成每个组的CAD命令
- 每个分组都有独立的PLINE命令

CAD命令格式:
- 使用标准CAD格式，包含注解说明
- 支持自动闭合检测
- 使用大写命令（PLINE/LINE/POINT）
- 保持坐标原始精度
- 自动结束多段线命令

标准CAD格式示例:
```
PLINE
0,0
100,0
100,100
0,100
C  ; 闭合图形
^C  ; 结束多段线命令

LINE
0,0
100,0
100,100
0,100

POINT
0,0
POINT
100,0
```

分组多段线格式:
- 每个分组都有独立的PLINE命令
- 闭合图形自动添加C命令
- 每个分组都有^C结束命令
- 分组之间有空行分隔
- 包含注解说明
- 保持坐标原始精度
- 自动结束多段线命令

命令结束逻辑:
- 闭合图形：C  ; 闭合图形 → ^C  ; 结束多段线命令
- 非闭合图形：直接 → ^C  ; 结束多段线命令
- 避免CAD继续处于编辑多段线状态

复制功能:
• 手动复制：直接复制到剪贴板
• 自动复制：转换后自动复制到剪贴板
• 安全可靠：只使用剪贴板，不涉及键盘操作

作者: {AUTHOR} ({EMAIL})
        """
        messagebox.showinfo("使用说明", help_text)
    
    def generate_cad_commands(self, coordinates):
        """生成CAD命令"""
        commands = []
        
        if not coordinates:
            return "未找到有效的坐标数据"
        
        convert_type = self.convert_type.get()
        add_text = self.add_text_var.get()
        text_height = self.text_height_var.get()
        
        # 检查是否包含Z坐标
        has_z_coords = any(len(coord) > 2 and coord[2] != 0 for coord in coordinates)
        
        if convert_type == "pline":
            # 使用标准CAD格式（带注解）
            commands.append("PLINE")
            for x, y, z in coordinates:
                if has_z_coords:
                    commands.append(f"{x},{y},{z}")
                else:
                    commands.append(f"{x},{y}")
            
            # 添加闭合选项（如果首尾坐标相同或接近）
            if len(coordinates) > 2:
                first_coord = coordinates[0]
                last_coord = coordinates[-1]
                # 检查首尾坐标是否相同（允许小误差）
                if (abs(first_coord[0] - last_coord[0]) < 0.001 and 
                    abs(first_coord[1] - last_coord[1]) < 0.001):
                    commands.append("C  ; 闭合图形")
            
            # 无论是否闭合，都要结束多段线命令
            commands.append("^C  ; 结束多段线命令")
            
        elif convert_type == "line":
            # 生成直线命令 - 使用标准格式
            commands.append("LINE")
            for x, y, z in coordinates:
                if has_z_coords:
                    commands.append(f"{x},{y},{z}")
                else:
                    commands.append(f"{x},{y}")
            commands.append("")
                
        elif convert_type == "point":
            # 生成点命令 - 使用标准格式
            for x, y, z in coordinates:
                commands.append("POINT")
                if has_z_coords:
                    commands.append(f"{x},{y},{z}")
                else:
                    commands.append(f"{x},{y}")
        
        # 添加文字标注
        if add_text:
            commands.append("")  # 空行分隔
            for i, (x, y, z) in enumerate(coordinates, 1):
                commands.append("TEXT")
                commands.append("J")
                commands.append("ML")
                if has_z_coords:
                    commands.append(f"{x},{y},{z}")
                else:
                    commands.append(f"{x},{y}")
                commands.append(str(text_height))
                commands.append("0")
                commands.append(f"点{i}")
        
        return "\n".join(commands)
    
    def generate_grouped_cad_commands(self, groups):
        """按分组生成CAD命令"""
        commands = []
        
        for group_name, coordinates in groups.items():
            if not coordinates:
                continue
                
            commands.append(f"# {group_name}")
            commands.append(f"# 共{len(coordinates)}个坐标点")
            commands.append("")
            
            # 为每个分组生成独立的PLINE命令
            commands.append("PLINE")
            for x, y, z in coordinates:
                # 检查是否包含Z坐标
                has_z_coords = len(coordinates[0]) > 2 and coordinates[0][2] != 0
                if has_z_coords:
                    commands.append(f"{x},{y},{z}")
                else:
                    commands.append(f"{x},{y}")
            
            # 检查是否闭合（首尾坐标相同）
            if len(coordinates) > 2:
                first_coord = coordinates[0]
                last_coord = coordinates[-1]
                if (abs(first_coord[0] - last_coord[0]) < 0.001 and 
                    abs(first_coord[1] - last_coord[1]) < 0.001):
                    commands.append("C  ; 闭合图形")
            
            # 无论是否闭合，都要结束多段线命令
            commands.append("^C  ; 结束多段线命令")
            commands.append("")  # 空行分隔下一个分组
        
        return "\n".join(commands)
    
    def plot_coordinates(self, coordinates: List[Tuple[float, float, float]]):
        """优化的坐标图形绘制"""
        if not coordinates or not HAS_MATPLOTLIB:
            return
        
        try:
            # 限制显示的点数以提高性能
            max_display_points = self.config['max_display_points']
            if len(coordinates) > max_display_points:
                # 使用更智能的采样算法
                step = len(coordinates) // max_display_points
                display_coordinates = coordinates[::step]
                self.update_status(f"⚠️ 坐标点过多，图形预览仅显示{len(display_coordinates)}个采样点", '#ffc107')
            else:
                display_coordinates = coordinates
            
            # 检查是否包含Z坐标
            has_z_coords = any(len(coord) > 2 and coord[2] != 0 for coord in display_coordinates)
            
            if has_z_coords:
                self.plot_3d_coordinates(display_coordinates)
            else:
                self.plot_2d_coordinates(display_coordinates)
                
        except Exception as e:
            error_msg = f"图形预览失败: {str(e)}"
            if hasattr(self, 'logger'):
                self.logger.error(error_msg)
            
            # 显示错误信息
            error_label = tk.Label(self.graph_frame, 
                text=f"图形预览失败:\n{str(e)}\n\n请检查matplotlib安装",
                font=('Microsoft YaHei', 10), fg='#dc3545', bg='white')
            error_label.pack(expand=True)
    
    def plot_2d_coordinates(self, coordinates):
        """绘制2D坐标图形"""
        # 清理旧的图形
        self.cleanup_matplotlib()
        
        # 创建图形并设置中文字体
        fig, ax = plt.subplots(figsize=(10, 7))
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 提取X和Y坐标
        x_coords = [coord[0] for coord in coordinates]
        y_coords = [coord[1] for coord in coordinates]
        
        # 绘制图形
        convert_type = self.convert_type.get()
        
        if convert_type == "pline":
            # 绘制多段线
            ax.plot(x_coords, y_coords, 'b-', linewidth=2, label='多段线')
            ax.plot(x_coords, y_coords, 'ro', markersize=4, label='坐标点')
            
        elif convert_type == "line":
            # 绘制直线段
            for i in range(len(coordinates) - 1):
                x1, y1 = coordinates[i][0], coordinates[i][1]
                x2, y2 = coordinates[i+1][0], coordinates[i+1][1]
                ax.plot([x1, x2], [y1, y2], 'b-', linewidth=1)
            ax.plot(x_coords, y_coords, 'ro', markersize=4, label='坐标点')
            
        elif convert_type == "point":
            # 绘制点
            ax.plot(x_coords, y_coords, 'ro', markersize=6, label='坐标点')
        
        # 设置等比例尺
        ax.set_aspect('equal')
        
        # 计算坐标范围并设置合适的显示范围
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        # 添加边距，确保图形不会太贴近边缘
        x_margin = (x_max - x_min) * 0.1
        y_margin = (y_max - y_min) * 0.1
        
        # 如果边距太小，设置最小边距
        if x_margin < 1:
            x_margin = 1
        if y_margin < 1:
            y_margin = 1
        
        ax.set_xlim(x_min - x_margin, x_max + x_margin)
        ax.set_ylim(y_min - y_margin, y_max + y_margin)
        
        # 设置图形属性
        ax.set_xlabel('X坐标', fontsize=12)
        ax.set_ylabel('Y坐标', fontsize=12)
        ax.set_title(f'坐标图形预览 ({len(coordinates)}个点) - 2D视图', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # 添加坐标点标注（限制数量避免过于拥挤）
        max_annotations = min(20, len(coordinates))
        step = max(1, len(coordinates) // max_annotations)
        for i in range(0, len(coordinates), step):
            x, y = coordinates[i][0], coordinates[i][1]
            ax.annotate(f'点{i+1}', (x, y), xytext=(5, 5), 
                       textcoords='offset points', fontsize=8)
        
        # 嵌入到tkinter窗口
        canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    

    
    def plot_3d_coordinates(self, coordinates):
        """绘制3D坐标图形"""
        # 清理旧的图形
        self.cleanup_matplotlib()
        
        # 创建3D图形
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 提取X、Y、Z坐标
        x_coords = [coord[0] for coord in coordinates]
        y_coords = [coord[1] for coord in coordinates]
        z_coords = [coord[2] for coord in coordinates]
        
        # 绘制图形
        convert_type = self.convert_type.get()
        
        if convert_type == "pline":
            # 绘制3D多段线
            ax.plot(x_coords, y_coords, z_coords, 'b-', linewidth=2, label='3D多段线')
            ax.scatter(x_coords, y_coords, z_coords, c='red', s=50, label='坐标点')
            
        elif convert_type == "line":
            # 绘制3D直线段
            for i in range(len(coordinates) - 1):
                x1, y1, z1 = coordinates[i]
                x2, y2, z2 = coordinates[i+1]
                ax.plot([x1, x2], [y1, y2], [z1, z2], 'b-', linewidth=1)
            ax.scatter(x_coords, y_coords, z_coords, c='red', s=50, label='坐标点')
            
        elif convert_type == "point":
            # 绘制3D点
            ax.scatter(x_coords, y_coords, z_coords, c='red', s=100, label='坐标点')
        
        # 设置坐标轴标签
        ax.set_xlabel('X坐标', fontsize=12)
        ax.set_ylabel('Y坐标', fontsize=12)
        ax.set_zlabel('Z坐标', fontsize=12)
        
        # 设置标题
        ax.set_title(f'3D坐标图形预览 ({len(coordinates)}个点)', fontsize=14, fontweight='bold')
        
        # 添加图例
        ax.legend()
        
        # 添加坐标点标注（限制数量避免过于拥挤）
        max_annotations = min(15, len(coordinates))
        step = max(1, len(coordinates) // max_annotations)
        for i in range(0, len(coordinates), step):
            x, y, z = coordinates[i]
            ax.text(x, y, z, f'点{i+1}', fontsize=8)
        
        # 设置视角
        ax.view_init(elev=20, azim=45)
        
        # 嵌入到tkinter窗口
        canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def plot_2d_grouped_coordinates(self):
        """绘制2D分组坐标图形"""
        # 清理旧的图形
        self.cleanup_matplotlib()
        
        # 创建图形并设置中文字体
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 定义颜色列表
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        
        # 收集所有坐标用于计算范围
        all_x = []
        all_y = []
        
        # 绘制每个分组
        for i, (group_name, coordinates) in enumerate(self.coordinate_groups.items()):
            if len(coordinates) == 0:
                continue
                
            color = colors[i % len(colors)]
            
            # 限制显示的点数以提高性能
            max_display_points = 500
            if len(coordinates) > max_display_points:
                step = len(coordinates) // max_display_points
                display_coordinates = coordinates[::step]
            else:
                display_coordinates = coordinates
            
            # 提取X和Y坐标
            x_coords = [coord[0] for coord in display_coordinates]
            y_coords = [coord[1] for coord in display_coordinates]
            
            all_x.extend(x_coords)
            all_y.extend(y_coords)
            
            # 绘制图形
            convert_type = self.convert_type.get()
            
            if convert_type == "pline":
                # 绘制多段线
                ax.plot(x_coords, y_coords, color=color, linewidth=2, 
                       label=f'{group_name} ({len(coordinates)}个点)')
                ax.plot(x_coords, y_coords, color=color, marker='o', 
                       markersize=4, linestyle='')
                
            elif convert_type == "line":
                # 绘制直线段
                for j in range(len(display_coordinates) - 1):
                    x1, y1 = display_coordinates[j][0], display_coordinates[j][1]
                    x2, y2 = display_coordinates[j+1][0], display_coordinates[j+1][1]
                    ax.plot([x1, x2], [y1, y2], color=color, linewidth=1)
                ax.plot(x_coords, y_coords, color=color, marker='o', 
                       markersize=4, linestyle='', label=f'{group_name} ({len(coordinates)}个点)')
                
            elif convert_type == "point":
                # 绘制点
                ax.plot(x_coords, y_coords, color=color, marker='o', 
                       markersize=6, linestyle='', label=f'{group_name} ({len(coordinates)}个点)')
        
        # 设置等比例尺
        ax.set_aspect('equal')
        
        # 计算坐标范围并设置合适的显示范围
        if all_x and all_y:
            x_min, x_max = min(all_x), max(all_x)
            y_min, y_max = min(all_y), max(all_y)
            
            # 添加边距
            x_margin = (x_max - x_min) * 0.1
            y_margin = (y_max - y_min) * 0.1
            
            if x_margin < 1:
                x_margin = 1
            if y_margin < 1:
                y_margin = 1
            
            ax.set_xlim(x_min - x_margin, x_max + x_margin)
            ax.set_ylim(y_min - y_margin, y_max + y_margin)
        
        # 设置图形属性
        ax.set_xlabel('X坐标', fontsize=12)
        ax.set_ylabel('Y坐标', fontsize=12)
        ax.set_title(f'分组坐标图形预览 - 2D视图', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 嵌入到tkinter窗口
        canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def plot_3d_grouped_coordinates(self):
        """绘制3D分组坐标图形"""
        # 清理旧的图形
        self.cleanup_matplotlib()
        
        # 创建3D图形
        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 定义颜色列表
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        
        # 收集所有坐标用于计算范围
        all_x = []
        all_y = []
        all_z = []
        
        # 绘制每个分组
        for i, (group_name, coordinates) in enumerate(self.coordinate_groups.items()):
            if len(coordinates) == 0:
                continue
                
            color = colors[i % len(colors)]
            
            # 限制显示的点数以提高性能
            max_display_points = 500
            if len(coordinates) > max_display_points:
                step = len(coordinates) // max_display_points
                display_coordinates = coordinates[::step]
            else:
                display_coordinates = coordinates
            
            # 提取X、Y、Z坐标
            x_coords = [coord[0] for coord in display_coordinates]
            y_coords = [coord[1] for coord in display_coordinates]
            z_coords = [coord[2] for coord in display_coordinates]
            
            all_x.extend(x_coords)
            all_y.extend(y_coords)
            all_z.extend(z_coords)
            
            # 绘制图形
            convert_type = self.convert_type.get()
            
            if convert_type == "pline":
                # 绘制3D多段线
                ax.plot(x_coords, y_coords, z_coords, color=color, linewidth=2, 
                       label=f'{group_name} ({len(coordinates)}个点)')
                ax.scatter(x_coords, y_coords, z_coords, c=color, s=50)
                
            elif convert_type == "line":
                # 绘制3D直线段
                for j in range(len(display_coordinates) - 1):
                    x1, y1, z1 = display_coordinates[j]
                    x2, y2, z2 = display_coordinates[j+1]
                    ax.plot([x1, x2], [y1, y2], [z1, z2], color=color, linewidth=1)
                ax.scatter(x_coords, y_coords, z_coords, c=color, s=50, 
                          label=f'{group_name} ({len(coordinates)}个点)')
                
            elif convert_type == "point":
                # 绘制3D点
                ax.scatter(x_coords, y_coords, z_coords, c=color, s=100, 
                          label=f'{group_name} ({len(coordinates)}个点)')
        
        # 设置坐标轴标签
        ax.set_xlabel('X坐标', fontsize=12)
        ax.set_ylabel('Y坐标', fontsize=12)
        ax.set_zlabel('Z坐标', fontsize=12)
        
        # 设置标题
        ax.set_title(f'分组3D坐标图形预览', fontsize=14, fontweight='bold')
        
        # 添加图例
        ax.legend(bbox_to_anchor=(1.15, 1), loc='upper left')
        
        # 设置视角
        ax.view_init(elev=20, azim=45)
        
        # 嵌入到tkinter窗口
        canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def update_status(self, message, color='#6c757d'):
        """更新状态栏信息"""
        self.status_label.config(text=message, fg=color)
        self.root.update_idletasks()
    
    def reset_status(self):
        """重置状态栏为默认状态"""
        self.update_status("就绪", '#6c757d')
    
    def convert_coordinates(self):
        """转换坐标数据"""
        if not self.coordinates:
            messagebox.showwarning("警告", "请先加载坐标文件")
            return
        
        try:
            self.update_status("正在转换坐标...", '#007bff')
            
            # 生成CAD命令
            if self.group_processing_var.get() and self.coordinate_groups:
                cad_commands = self.generate_grouped_cad_commands(self.coordinate_groups)
            else:
                cad_commands = self.generate_cad_commands(self.coordinates)
            
            # 显示结果 - 临时启用编辑状态
            self.cad_text.config(state='normal')
            self.cad_text.delete(1.0, tk.END)
            self.cad_text.insert(1.0, cad_commands)
            self.cad_text.config(state='disabled')  # 恢复只读状态
            
            # 绘制图形预览
            if HAS_MATPLOTLIB:
                self.update_status("正在生成图形预览...", '#007bff')
                self.plot_coordinates(self.coordinates)
            
            # 自动复制功能 - 修复版本
            if self.auto_copy_var.get():
                self.update_status("正在复制到剪贴板...", '#007bff')
                try:
                    # 使用非阻塞方式复制到剪贴板，确保与手动复制行为一致
                    self.root.after(100, lambda: self.safe_copy_to_clipboard(cad_commands, is_auto=True))
                except Exception as e:
                    self.update_status(f"复制失败: {str(e)}", '#dc3545')
            else:
                self.update_status(f"✅ 转换完成！共处理 {len(self.coordinates)} 个坐标点", '#28a745')
            
            # 3秒后恢复默认状态
            self.root.after(3000, self.reset_status)
            
        except Exception as e:
            messagebox.showerror("错误", f"转换过程中出现错误: {str(e)}")
            self.update_status("转换失败", '#dc3545')
            # 3秒后恢复默认状态
            self.root.after(3000, self.reset_status)
    
    def safe_copy_to_clipboard(self, content: str, is_auto: bool = False) -> bool:
        """线程安全的剪贴板复制"""
        def perform_copy():
            try:
                with CLIPBOARD_LOCK:
                    # 使用系统命令复制
                    try:
                        subprocess.run(['clip'], input=content.encode('utf-8'), 
                                     check=True, timeout=5)
                        if hasattr(self, 'logger'):
                            self.logger.info("使用clip命令复制成功")
                        return True
                    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                        # 回退到tkinter剪贴板
                        self.root.after(100, lambda: self._safe_tkinter_copy(content))
                        return True
                        
            except Exception as e:
                if hasattr(self, 'logger'):
                    self.logger.error(f"复制操作失败: {e}")
                return False
        
        # 在新线程中执行复制操作
        copy_thread = threading.Thread(target=perform_copy, daemon=True)
        copy_thread.start()
        
        # 显示状态信息
        status_msg = "正在复制到剪贴板..." if not is_auto else "正在自动复制..."
        self.update_status(status_msg, '#007bff')
        
        return True

    def _safe_tkinter_copy(self, content: str):
        """安全的tkinter剪贴板复制"""
        try:
            with CLIPBOARD_LOCK:
                self.root.clipboard_clear()
                self.root.clipboard_append(content)
                
                if hasattr(self, 'logger'):
                    self.logger.info("使用tkinter剪贴板复制成功")
                
                # 显示成功消息
                self.update_status("✅ 已复制到剪贴板", '#28a745')
                self.root.after(200, lambda: self.show_non_blocking_message("复制成功", "CAD命令已复制到剪贴板"))
                
        except Exception as e:
            self.update_status(f"复制失败: {str(e)}", '#dc3545')
            if hasattr(self, 'logger'):
                self.logger.error(f"tkinter复制操作失败: {e}")

    def show_non_blocking_message(self, title, message):
        """非阻塞方式显示消息"""
        try:
            # 创建临时窗口显示消息
            msg_window = tk.Toplevel(self.root)
            msg_window.title(title)
            msg_window.geometry("300x100")
            msg_window.resizable(False, False)
            msg_window.transient(self.root)
            msg_window.grab_set()
            
            # 居中显示
            msg_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
            
            # 消息内容
            tk.Label(msg_window, text=message, font=('Microsoft YaHei', 10)).pack(pady=20)
            
            # 确定按钮
            tk.Button(msg_window, text="确定", command=msg_window.destroy, 
                     font=('Microsoft YaHei', 9)).pack(pady=10)
            
            # 3秒后自动关闭
            msg_window.after(3000, msg_window.destroy)
            
        except Exception as e:
            print(f"显示消息时出错: {e}")
    
    def copy_to_cad(self):
        """复制CAD命令到剪贴板 - 统一复制函数"""
        content = self.cad_text.get(1.0, tk.END).strip()
        if content:
            try:
                self.safe_copy_to_clipboard(content)
            except Exception as e:
                self.update_status(f"复制失败: {str(e)}", '#dc3545')
        else:
            self.update_status("没有可复制的内容", '#ffc107')
    
    def auto_copy_to_cad(self):
        """自动复制到剪贴板 - 已废弃，保留兼容性"""
        self.copy_to_cad()
    
    def copy_cad_commands(self):
        """复制CAD命令到剪贴板 - 已废弃，保留兼容性"""
        self.copy_to_cad()
    
    def save_to_file(self):
        """保存结果到文件"""
        content = self.cad_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("警告", "没有可保存的内容")
            return
        
        filename = filedialog.asksaveasfilename(
            title="保存CAD命令文件",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"文件已保存到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存文件时出现错误: {str(e)}")
    
    def clear_results(self):
        """清空结果显示"""
        # 临时启用编辑状态清空内容
        self.cad_text.config(state='normal')
        self.cad_text.delete(1.0, tk.END)
        self.cad_text.config(state='disabled')
        
        self.preview_text.delete(1.0, tk.END)
        self.coordinates = []
        
        # 清除图形
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        # 使用安全方式清理剪贴板
        try:
            def clear_clipboard():
                try:
                    # 使用clip命令清空剪贴板
                    subprocess.run(['echo', ''], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except:
                    # 回退到tkinter清理
                    self.root.after(500, lambda: self.root.clipboard_clear())
            
            clear_thread = threading.Thread(target=clear_clipboard, daemon=True)
            clear_thread.start()
            print("✅ 使用安全方式清理剪贴板")
        except Exception as e:
            print(f"清理剪贴板时出错: {e}")
    

    
    def cleanup_matplotlib(self):
        """改进的matplotlib资源清理"""
        try:
            if HAS_MATPLOTLIB:
                # 关闭所有图形
                plt.close('all')
                # 清除当前图形和轴
                plt.clf()
                plt.cla()
                
                # 强制垃圾回收
                gc.collect()
                
                if hasattr(self, 'logger'):
                    self.logger.info("matplotlib资源已清理")
            else:
                if hasattr(self, 'logger'):
                    self.logger.info("matplotlib未安装，无需清理")
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"清理matplotlib资源时出现错误: {e}")
    
    def cleanup_resources(self):
        """清理所有资源"""
        try:
            print("正在清理资源...")
            
            # 清理matplotlib资源
            self.cleanup_matplotlib()
            
            # 清理坐标数据
            self.coordinates = []
            self.coordinate_groups = {}
            
            # 强制垃圾回收
            gc.collect()
            
            print("资源清理完成")
        except Exception as e:
            print(f"清理资源时出现错误: {e}")
    
    def on_closing(self):
        """程序关闭时的清理工作 - 优化版本"""
        try:
            if hasattr(self, 'logger'):
                self.logger.info("正在关闭程序，清理资源...")
            
            # 清理应用资源
            self.cleanup_resources()
            
            # 销毁主窗口
            self.root.destroy()
            
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"关闭程序时出现错误: {e}")
            # 强制退出程序，确保没有残留进程
            import os
            os._exit(0)

    def setup_ui(self):
        """设置用户界面 - 优化版本"""
        # 创建主容器
        main_container = tk.Frame(self.root, bg='#f8f9fa')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 顶部标题区域
        self.create_header(main_container)
        
        # 创建左右分栏布局
        content_frame = tk.Frame(main_container, bg='#f8f9fa')
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # 左侧控制面板
        left_panel = self.create_left_panel(content_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # 右侧结果显示区域
        right_panel = self.create_right_panel(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
    def create_header(self, parent):
        """创建顶部标题区域"""
        header_frame = tk.Frame(parent, bg='#f8f9fa', height=100)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # 主标题
        title_label = tk.Label(header_frame, text=f"CAD坐标转换器 v{VERSION}", 
                              font=self.font_title, bg='#f8f9fa', fg='#2c3e50')
        title_label.pack(pady=(10, 5))
        
        # 副标题
        subtitle_label = tk.Label(header_frame, text="专业坐标转换工具 - 支持Windows 7/8/10/11", 
                                 font=('Microsoft YaHei', 9), bg='#f8f9fa', fg='#7f8c8d')
        subtitle_label.pack()
        
        # 作者信息
        author_label = tk.Label(header_frame, text=f"作者: {AUTHOR} ({EMAIL})", 
                               font=('Microsoft YaHei', 8), bg='#f8f9fa', fg='#95a5a6')
        author_label.pack(pady=(2, 0))
        
    def create_left_panel(self, parent):
        """创建左侧控制面板"""
        left_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(left_frame, text="文件选择", padding=15)
        file_frame.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=35, font=self.font_normal)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(file_frame, text="浏览", command=self.browse_file)
        browse_btn.pack(side=tk.RIGHT)
        
        # 转换选项区域
        options_frame = ttk.LabelFrame(left_frame, text="转换选项", padding=15)
        options_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # 转换类型选择
        type_label = tk.Label(options_frame, text="转换类型:", font=('Microsoft YaHei', 9, 'bold'), bg='white')
        type_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.convert_type = tk.StringVar(value="line")
        ttk.Radiobutton(options_frame, text="多段线 (PLINE)", 
                       variable=self.convert_type, value="pline").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(options_frame, text="直线 (LINE)", 
                       variable=self.convert_type, value="line").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(options_frame, text="点 (POINT)", 
                       variable=self.convert_type, value="point").pack(anchor=tk.W, pady=2)
        
        # 高级选项
        advanced_label = tk.Label(options_frame, text="高级设置:", font=('Microsoft YaHei', 9, 'bold'), bg='white')
        advanced_label.pack(anchor=tk.W, pady=(15, 5))
        
        self.add_text_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="添加文字标注", 
                       variable=self.add_text_var).pack(anchor=tk.W, pady=2)
        
        text_height_frame = tk.Frame(options_frame, bg='white')
        text_height_frame.pack(fill=tk.X, pady=(5, 0))
        
        tk.Label(text_height_frame, text="文字高度:", bg='white').pack(side=tk.LEFT)
        self.text_height_var = tk.StringVar(value="5")
        ttk.Entry(text_height_frame, textvariable=self.text_height_var, width=8).pack(side=tk.LEFT, padx=(5, 0))
        
        # 分组处理选项
        self.group_processing_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="按分组分别处理", 
                       variable=self.group_processing_var).pack(anchor=tk.W, pady=(5, 0))
        
        # 自动复制选项 - 默认关闭，避免干扰用户
        self.auto_copy_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="转换后自动复制", 
                       variable=self.auto_copy_var).pack(anchor=tk.W, pady=(10, 0))
        
        # 转换按钮
        convert_frame = tk.Frame(left_frame, bg='white')
        convert_frame.pack(fill=tk.X, padx=15, pady=15)
        
        convert_btn = ttk.Button(convert_frame, text="开始转换", 
                                command=self.convert_coordinates)
        convert_btn.pack(fill=tk.X, pady=(0, 10))
        
        # 操作按钮组
        button_frame = tk.Frame(left_frame, bg='white')
        button_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        ttk.Button(button_frame, text="一键复制", command=self.copy_to_cad).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="保存文件", command=self.save_to_file).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="清空结果", command=self.clear_results).pack(fill=tk.X, pady=2)
        
        return left_frame
        
    def create_right_panel(self, parent):
        """创建右侧结果显示区域"""
        right_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        
        # 结果显示标题
        result_header = tk.Frame(right_frame, bg='#e9ecef', height=40)
        result_header.pack(fill=tk.X)
        result_header.pack_propagate(False)
        
        result_title = tk.Label(result_header, text="转换结果", 
                               font=self.font_subtitle, bg='#e9ecef', fg='#495057')
        result_title.pack(side=tk.LEFT, padx=15, pady=10)
        
        # 状态栏
        self.status_label = tk.Label(result_header, text="就绪", 
                                    font=('Microsoft YaHei', 9), bg='#e9ecef', fg='#6c757d')
        self.status_label.pack(side=tk.RIGHT, padx=15, pady=10)
        
        # 创建选项卡
        notebook = ttk.Notebook(right_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # CAD命令选项卡
        cad_frame = tk.Frame(notebook, bg='white')
        notebook.add(cad_frame, text="🎯 CAD命令")
        
        self.cad_text = scrolledtext.ScrolledText(cad_frame, height=20, font=('Consolas', 10),
                                                 bg='#f8f9fa', fg='#212529', insertbackground='#212529',
                                                 state='disabled')  # 设置为只读状态
        self.cad_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 预览选项卡
        preview_frame = tk.Frame(notebook, bg='white')
        notebook.add(preview_frame, text="📄 数据预览")
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=20, font=('Consolas', 10),
                                                     bg='#f8f9fa', fg='#212529', insertbackground='#212529')
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 图形预览选项卡
        self.graph_frame = tk.Frame(notebook, bg='white')
        notebook.add(self.graph_frame, text="📈 图形预览")
        
        # 如果matplotlib不可用，显示提示
        if not HAS_MATPLOTLIB:
            no_graph_label = tk.Label(self.graph_frame, 
                text="图形预览功能不可用\n\n请安装matplotlib库\n运行'pip install matplotlib>=3.3.0'安装依赖包",
                font=('Microsoft YaHei', 12), fg='#6c757d', bg='white')
            no_graph_label.pack(expand=True)
        
        return right_frame

    def browse_file(self):
        """浏览文件 - 优化版本"""
        filename = filedialog.askopenfilename(
            title="选择坐标文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if filename:
            # 验证文件路径安全性
            if not self.validate_file_path(filename):
                messagebox.showerror("错误", "选择的文件路径无效或文件过大")
                return
            
            self.file_path_var.set(filename)
            self.load_coordinate_file(filename)

    def preview_file_content(self):
        """预览文件内容 - 优化版本"""
        try:
            content = self.safe_read_file(self.file_path_var.get())
            self.preview_text.delete(1.0, tk.END)
            
            # 限制预览内容长度
            max_preview_length = 2000
            if len(content) > max_preview_length:
                preview_content = content[:max_preview_length] + "\n\n... (内容过长，已截断)"
            else:
                preview_content = content
                
            self.preview_text.insert(1.0, preview_content)
            
        except Exception as e:
            error_msg = f"无法读取文件: {str(e)}"
            messagebox.showerror("错误", error_msg)
            if hasattr(self, 'logger'):
                self.logger.error(error_msg)

    def convert_coordinates(self):
        """转换坐标数据 - 优化版本"""
        if not self.coordinates:
            messagebox.showwarning("警告", "请先加载坐标文件")
            return
        
        try:
            self.update_status("正在转换坐标...", '#007bff')
            
            # 生成CAD命令
            if self.group_processing_var.get() and self.coordinate_groups:
                cad_commands = self.generate_grouped_cad_commands(self.coordinate_groups)
            else:
                cad_commands = self.generate_cad_commands(self.coordinates)
            
            # 显示结果 - 临时启用编辑状态
            self.cad_text.config(state='normal')
            self.cad_text.delete(1.0, tk.END)
            self.cad_text.insert(1.0, cad_commands)
            self.cad_text.config(state='disabled')  # 恢复只读状态
            
            # 绘制图形预览
            if HAS_MATPLOTLIB:
                self.update_status("正在生成图形预览...", '#007bff')
                self.plot_coordinates(self.coordinates)
            
            # 自动复制功能 - 修复版本
            if self.auto_copy_var.get():
                self.update_status("正在复制到剪贴板...", '#007bff')
                try:
                    # 使用非阻塞方式复制到剪贴板，确保与手动复制行为一致
                    self.root.after(100, lambda: self.safe_copy_to_clipboard(cad_commands, is_auto=True))
                except Exception as e:
                    self.update_status(f"复制失败: {str(e)}", '#dc3545')
            else:
                self.update_status(f"✅ 转换完成！共处理 {len(self.coordinates)} 个坐标点", '#28a745')
            
            # 3秒后恢复默认状态
            self.root.after(3000, self.reset_status)
            
        except Exception as e:
            error_msg = f"转换过程中出现错误: {str(e)}"
            messagebox.showerror("错误", error_msg)
            self.update_status("转换失败", '#dc3545')
            if hasattr(self, 'logger'):
                self.logger.error(error_msg)
            # 3秒后恢复默认状态
            self.root.after(3000, self.reset_status)

    def update_status(self, message, color='#6c757d'):
        """更新状态栏信息"""
        self.status_label.config(text=message, fg=color)
        self.root.update_idletasks()
    
    def reset_status(self):
        """重置状态栏为默认状态"""
        self.update_status("就绪", '#6c757d')

    def copy_to_cad(self):
        """复制CAD命令到剪贴板 - 统一复制函数"""
        content = self.cad_text.get(1.0, tk.END).strip()
        if content:
            try:
                self.safe_copy_to_clipboard(content)
            except Exception as e:
                self.update_status(f"复制失败: {str(e)}", '#dc3545')
        else:
            self.update_status("没有可复制的内容", '#ffc107')
    
    def auto_copy_to_cad(self):
        """自动复制到剪贴板 - 已废弃，保留兼容性"""
        self.copy_to_cad()
    
    def copy_cad_commands(self):
        """复制CAD命令到剪贴板 - 已废弃，保留兼容性"""
        self.copy_to_cad()
    
    def save_to_file(self):
        """保存结果到文件"""
        content = self.cad_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("警告", "没有可保存的内容")
            return
        
        filename = filedialog.asksaveasfilename(
            title="保存CAD命令文件",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"文件已保存到: {filename}")
                if hasattr(self, 'logger'):
                    self.logger.info(f"文件已保存: {filename}")
            except Exception as e:
                error_msg = f"保存文件时出现错误: {str(e)}"
                messagebox.showerror("错误", error_msg)
                if hasattr(self, 'logger'):
                    self.logger.error(error_msg)
    
    def clear_results(self):
        """清空结果显示"""
        # 临时启用编辑状态清空内容
        self.cad_text.config(state='normal')
        self.cad_text.delete(1.0, tk.END)
        self.cad_text.config(state='disabled')
        
        self.preview_text.delete(1.0, tk.END)
        self.coordinates = []
        
        # 清除图形
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        # 使用安全方式清理剪贴板
        try:
            def clear_clipboard():
                try:
                    # 使用clip命令清空剪贴板
                    subprocess.run(['echo', ''], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except:
                    # 回退到tkinter清理
                    self.root.after(500, lambda: self.root.clipboard_clear())
            
            clear_thread = threading.Thread(target=clear_clipboard, daemon=True)
            clear_thread.start()
            if hasattr(self, 'logger'):
                self.logger.info("使用安全方式清理剪贴板")
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"清理剪贴板时出错: {e}")

    def cleanup_resources(self):
        """清理所有资源 - 优化版本"""
        try:
            if hasattr(self, 'logger'):
                self.logger.info("正在清理资源...")
            
            # 清理matplotlib资源
            self.cleanup_matplotlib()
            
            # 清理坐标数据
            self.coordinates = []
            self.coordinate_groups = {}
            
            # 强制垃圾回收
            gc.collect()
            
            if hasattr(self, 'logger'):
                self.logger.info("资源清理完成")
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"清理资源时出现错误: {e}")

def main():
    root = tk.Tk()
    
    # 设置窗口图标
    try:
        # 尝试设置窗口图标
        root.iconbitmap('favicon.ico')
    except:
        # 如果图标文件不存在，使用默认图标
        pass
    
    app = CAD坐标转换器(root)
    
    # 设置窗口关闭事件处理
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 