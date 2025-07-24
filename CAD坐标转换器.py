#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CAD坐标转换器
版本: 1.1.0
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

# 尝试导入pyautogui用于模拟按键
try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False
    print("警告：pyautogui未安装，无法使用自动按键功能")

# 版本信息
VERSION = "1.1.0"
AUTHOR = "ViVi141"
EMAIL = "747384120@qq.com"

# 检查matplotlib可用性
HAS_MATPLOTLIB = False
try:
    import matplotlib
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
        
        self.setup_ui()
        self.setup_keyboard_shortcuts()
        
    def check_system_compatibility(self):
        """检查系统兼容性"""
        system_info = platform.system() + " " + platform.release()
        python_version = sys.version.split()[0]
        
        print(f"CAD坐标转换器 v{VERSION}")
        print(f"作者: {AUTHOR} ({EMAIL})")
        print(f"系统信息: {system_info}")
        print(f"Python版本: {python_version}")
        print(f"matplotlib可用: {HAS_MATPLOTLIB}")
        
        # 显示兼容性信息
        if not HAS_MATPLOTLIB:
            messagebox.showwarning("兼容性提示", 
                "matplotlib未安装，图形预览功能不可用。\n"
                "建议运行'安装依赖.bat'安装依赖包。")
        
    def setup_ui(self):
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
        
        # 自动复制选项
        self.auto_copy_var = tk.BooleanVar(value=True)
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
        ttk.Button(button_frame, text="自动复制", command=self.auto_copy_to_cad).pack(fill=tk.X, pady=2)
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
                                                 bg='#f8f9fa', fg='#212529', insertbackground='#212529')
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
                text="图形预览功能不可用\n\n请安装matplotlib库\n运行'安装依赖.bat'安装依赖包",
                font=('Microsoft YaHei', 12), fg='#6c757d', bg='white')
            no_graph_label.pack(expand=True)
        
        return right_frame
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="选择坐标文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)
            self.preview_file_content()
    
    def preview_file_content(self):
        try:
            with open(self.file_path_var.get(), 'r', encoding='utf-8') as f:
                content = f.read()
                self.preview_text.delete(1.0, tk.END)
                self.preview_text.insert(1.0, content[:1000] + "..." if len(content) > 1000 else content)
        except Exception as e:
            messagebox.showerror("错误", f"无法读取文件: {str(e)}")
    
    def parse_coordinates(self, content):
        """解析坐标数据"""
        coordinates = []
        groups = {}  # 存储分组坐标数据
        current_group = "默认组"
        
        # 编译正则表达式以提高性能
        coord_pattern = re.compile(r'(\d+\.?\d*)\s*,\s*(\d+\.?\d*)\s*,?\s*(\d+\.?\d*)?')
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # 检查是否是分组标识
            if line.startswith('第') and '组' in line:
                current_group = line
                if current_group not in groups:
                    groups[current_group] = []
                continue
                
            # 匹配坐标格式: x, y, z (可选)
            matches = coord_pattern.findall(line)
            
            for match in matches:
                try:
                    x, y, z = match[0], match[1], match[2] if match[2] else "0"
                    coord = (float(x), float(y), float(z))
                    coordinates.append(coord)
                    
                    # 同时添加到分组中
                    if current_group not in groups:
                        groups[current_group] = []
                    groups[current_group].append(coord)
                except ValueError:
                    # 跳过无效的坐标数据
                    continue
        
        # 存储分组数据
        self.coordinate_groups = groups
        
        return coordinates
    
    def setup_keyboard_shortcuts(self):
        """设置键盘快捷键"""
        # Ctrl+O: 打开文件
        self.root.bind('<Control-o>', lambda e: self.browse_file())
        # Ctrl+Enter: 转换坐标
        self.root.bind('<Control-Return>', lambda e: self.convert_coordinates())
        # Ctrl+C: 复制到CAD
        self.root.bind('<Control-c>', lambda e: self.copy_to_cad())
        # Ctrl+S: 保存文件
        self.root.bind('<Control-s>', lambda e: self.save_to_file())
        # Ctrl+L: 清空结果
        self.root.bind('<Control-l>', lambda e: self.clear_results())
        # F1: 帮助信息
        self.root.bind('<F1>', lambda e: self.show_help())
    
    def show_help(self):
        """显示帮助信息"""
        help_text = f"""
CAD坐标转换器 v{VERSION} - 快捷键说明

文件操作:
  Ctrl+O    打开坐标文件
  Ctrl+S    保存结果到文件

转换操作:
  Ctrl+Enter 执行坐标转换
  Ctrl+C    复制CAD命令到剪贴板
  Ctrl+L    清空结果显示

其他:
  F1        显示此帮助信息

使用说明:
1. 选择包含坐标数据的TXT文件
2. 选择转换类型（pline/line/point）
3. 设置是否添加文字标注
4. 选择是否按分组分别处理（可选）
5. 点击"转换坐标"或按Ctrl+Enter
6. 复制生成的CAD命令到CAD软件中使用

支持格式:
- X,Y 坐标: 447677.9778, 2491585.3947
- X,Y,Z 坐标: 447677.9778, 2491585.3947, 100.5
- 分组标识: 第1组、第2组等

分组处理:
- 默认忽略分组，所有坐标合并处理
- 勾选"按分组分别处理"可分别生成每个组的CAD命令

⚠️ 重要说明 - CAD命令限制:
• 当多个分组的多段线连续执行时，CAD会将它们合并为一个多段线
• 手动复制粘贴可能导致分组边界丢失
• 建议使用"自动复制"功能，通过模拟键盘操作确保每个分组独立执行
• 自动粘贴功能是为了克服CAD命令限制而设计的妥协方案

复制方式:
• 手动复制：直接复制到剪贴板，适合单个分组
• 自动复制：模拟键盘操作，确保多个分组独立执行

作者: {AUTHOR} ({EMAIL})
        """
        messagebox.showinfo("快捷键帮助", help_text)
    
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
            # 生成多段线命令 - 使用CAD标准格式，确保每个图形独立
            commands.append("pline")
            for x, y, z in coordinates:
                if has_z_coords:
                    commands.append(f"{x:.4f},{y:.4f},{z:.4f}")
                else:
                    commands.append(f"{x:.4f},{y:.4f}")
            commands.append("")  # 空行表示命令结束
            # 添加明确的命令结束标记
            commands.append("")
            # 添加回车键模拟，确保CAD命令中断
            commands.append("")
            
        elif convert_type == "line":
            # 生成直线命令 - 每个坐标点单独生成 line 命令
            for x, y, z in coordinates:
                if has_z_coords:
                    commands.append(f"line {x:.4f},{y:.4f},{z:.4f}")
                else:
                    commands.append(f"line {x:.4f},{y:.4f}")
                
        elif convert_type == "point":
            # 生成点命令
            for x, y, z in coordinates:
                if has_z_coords:
                    commands.append(f"point {x:.4f},{y:.4f},{z:.4f}")
                else:
                    commands.append(f"point {x:.4f},{y:.4f}")
        
        # 添加文字标注
        if add_text:
            commands.append("")  # 空行分隔
            for i, (x, y, z) in enumerate(coordinates, 1):
                if has_z_coords:
                    commands.append(f'-text j ml {x:.4f},{y:.4f},{z:.4f} "" {text_height} 0 A 点{i}')
                else:
                    commands.append(f'-text j ml {x:.4f},{y:.4f} "" {text_height} 0 A 点{i}')
        
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
            
            # 生成该组的CAD命令
            group_commands = self.generate_cad_commands(coordinates)
            commands.append(group_commands)
            commands.append("")  # 空行分隔
        
        return "\n".join(commands)
    
    def plot_coordinates(self, coordinates):
        """绘制坐标图形"""
        if not coordinates or not HAS_MATPLOTLIB:
            return
        
        try:
            # 延迟导入 matplotlib 相关模块
            import matplotlib
            matplotlib.use('TkAgg')
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import numpy as np
            
            # 设置matplotlib中文字体
            plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            # 禁用matplotlib的交互模式，减少进程创建
            plt.ioff()
            
            # 清除之前的图形
            for widget in self.graph_frame.winfo_children():
                widget.destroy()
            
            # 检查是否启用分组处理且有多个分组
            if (self.group_processing_var.get() and 
                len(self.coordinate_groups) > 1 and 
                any(len(coords) > 0 for coords in self.coordinate_groups.values())):
                # 分组绘图
                has_z_coords = any(len(coord) > 2 and coord[2] != 0 
                                 for coords in self.coordinate_groups.values() 
                                 for coord in coords)
                if has_z_coords:
                    self.plot_3d_grouped_coordinates()
                else:
                    self.plot_2d_grouped_coordinates()
            else:
                # 普通绘图
                # 限制显示的点数以提高性能
                max_display_points = 1000
                if len(coordinates) > max_display_points:
                    # 均匀采样
                    step = len(coordinates) // max_display_points
                    display_coordinates = coordinates[::step]
                    self.update_status(f"⚠️ 坐标点过多，图形预览仅显示{len(display_coordinates)}个采样点", '#ffc107')
                else:
                    display_coordinates = coordinates
                
                # 检查是否包含Z坐标
                has_z_coords = any(len(coord) > 2 and coord[2] != 0 for coord in display_coordinates)
                
                if has_z_coords:
                    # 3D图形显示
                    self.plot_3d_coordinates(display_coordinates)
                else:
                    # 2D图形显示
                    self.plot_2d_coordinates(display_coordinates)
            
        except Exception as e:
            # 如果图形绘制失败，显示错误信息
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
        """执行坐标转换"""
        if not self.file_path_var.get():
            messagebox.showwarning("警告", "请先选择坐标文件")
            return
        
        try:
            self.update_status("正在读取文件...", '#007bff')
            self.root.update()  # 强制更新界面
            
            # 添加文件大小检查
            file_size = os.path.getsize(self.file_path_var.get())
            if file_size > 10 * 1024 * 1024:  # 10MB
                if not messagebox.askyesno("文件过大", 
                    f"文件大小({file_size/1024/1024:.1f}MB)较大，处理可能需要较长时间。\n是否继续？"):
                    return
            
            with open(self.file_path_var.get(), 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.update_status("正在解析坐标数据...", '#007bff')
            self.root.update()  # 强制更新界面
            self.coordinates = self.parse_coordinates(content)
            
            if not self.coordinates:
                messagebox.showwarning("警告", "文件中未找到有效的坐标数据")
                self.update_status("就绪", '#6c757d')
                return
            
            # 添加坐标数量检查
            if len(self.coordinates) > 10000:
                if not messagebox.askyesno("坐标数量过多", 
                    f"检测到{len(self.coordinates)}个坐标点，处理可能需要较长时间。\n是否继续？"):
                    return
            
            self.update_status("正在生成CAD命令...", '#007bff')
            self.root.update()  # 强制更新界面
            
            # 根据用户选择决定是否按分组处理
            if self.group_processing_var.get() and len(self.coordinate_groups) > 1:
                cad_commands = self.generate_grouped_cad_commands(self.coordinate_groups)
            else:
                cad_commands = self.generate_cad_commands(self.coordinates)
            
            # 检查Z坐标并更新状态
            has_z_coords = any(len(coord) > 2 and coord[2] != 0 for coord in self.coordinates)
            if has_z_coords:
                self.update_status(f"✅ 转换完成！共{len(self.coordinates)}个点 (包含Z坐标)", '#28a745')
            else:
                self.update_status(f"✅ 转换完成！共{len(self.coordinates)}个点", '#28a745')
            
            # 显示结果
            self.cad_text.delete(1.0, tk.END)
            self.cad_text.insert(1.0, cad_commands)
            
            # 绘制图形预览
            if HAS_MATPLOTLIB:
                self.update_status("正在生成图形预览...", '#007bff')
                self.root.update()  # 强制更新界面
                self.plot_coordinates(self.coordinates)
            
            # 自动复制功能
            if self.auto_copy_var.get():
                self.update_status("正在自动复制到CAD...", '#007bff')
                self.root.update()  # 强制更新界面
                self.auto_copy_to_cad()
            else:
                self.update_status(f"✅ 转换完成！共处理 {len(self.coordinates)} 个坐标点", '#28a745')
            
            # 3秒后恢复默认状态
            self.root.after(3000, self.reset_status)
            
        except Exception as e:
            messagebox.showerror("错误", f"转换过程中出现错误: {str(e)}")
            self.update_status("转换失败", '#dc3545')
            # 3秒后恢复默认状态
            self.root.after(3000, self.reset_status)
    
    def copy_to_cad(self):
        """一键复制到CAD - 增强版复制功能"""
        content = self.cad_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("警告", "没有可复制的内容")
            return
        
        # 检查是否是分组模式且有多个分组
        if (self.group_processing_var.get() and 
            len(self.coordinate_groups) > 1 and 
            any(len(coords) > 0 for coords in self.coordinate_groups.values())):
            
            # 显示分组复制选择对话框
            self.show_group_copy_dialog()
        else:
            # 普通复制
            self.copy_content_to_clipboard(content)
    
    def auto_copy_to_cad(self):
        """自动复制到CAD功能"""
        # 调试信息
        print(f"调试信息 - coordinate_groups: {len(self.coordinate_groups) if self.coordinate_groups else 0}")
        print(f"调试信息 - coordinates: {len(self.coordinates) if self.coordinates else 0}")
        
        # 检查是否有可复制的内容
        if not self.coordinate_groups and not self.coordinates:
            messagebox.showwarning("警告", "没有可复制的内容\n请先转换坐标数据")
            return
        
        # 如果没有分组数据但有普通坐标数据，先转换
        if not self.coordinate_groups and self.coordinates:
            print("调试信息 - 将普通坐标数据转换为分组格式")
            # 将普通坐标数据转换为分组格式
            self.coordinate_groups = {"默认组": self.coordinates}
        
        print(f"调试信息 - 最终coordinate_groups: {len(self.coordinate_groups)}")
        
        # 显示复制方式选择对话框
        self.show_copy_method_dialog()
    
    def show_copy_method_dialog(self):
        """显示复制方式选择对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("选择复制方式")
        dialog.transient(self.root)
        dialog.focus_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 250
        y = (dialog.winfo_screenheight() // 2) - 200
        dialog.geometry(f"+{x}+{y}")
        
        # 主容器
        main_frame = tk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(main_frame, text="选择复制方式", 
                              font=('Microsoft YaHei', 14, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # 说明
        desc_label = tk.Label(main_frame, text="请选择您希望的复制方式：", 
                             font=('Microsoft YaHei', 10))
        desc_label.pack(pady=(0, 20))
        
        # 选项按钮
        options_frame = tk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        def copy_all_groups():
            """复制所有分组"""
            self._copy_all_groups_to_cad()
            dialog.destroy()
        
        def copy_selected_groups():
            """复制选中的分组"""
            dialog.destroy()
            self.show_group_copy_dialog()
        
        def copy_with_preview():
            """复制并预览"""
            self._copy_all_groups_to_cad(preview=True)
            dialog.destroy()
        
        # 选项按钮
        btn1 = ttk.Button(options_frame, text="📋 复制所有分组", 
                          command=copy_all_groups, width=25)
        btn1.pack(pady=5)
        
        btn2 = ttk.Button(options_frame, text="✅ 选择特定分组", 
                          command=copy_selected_groups, width=25)
        btn2.pack(pady=5)
        
        btn3 = ttk.Button(options_frame, text="👁️ 复制并预览", 
                          command=copy_with_preview, width=25)
        btn3.pack(pady=5)
        
        # 取消按钮
        cancel_btn = ttk.Button(main_frame, text="取消", command=dialog.destroy)
        cancel_btn.pack(pady=(10, 0))
        
        # 提示信息
        tip_frame = tk.Frame(main_frame)
        tip_frame.pack(fill=tk.X, pady=(15, 0))
        
        tip_label = tk.Label(tip_frame, text="💡 提示：\n• 复制所有分组：直接复制所有数据\n• 选择特定分组：可以选择部分分组\n• 复制并预览：先查看内容再复制\n\n⚠️ 注意：由于CAD命令限制，多个分组的多段线可能会被合并。\n建议使用自动粘贴功能来确保每个分组独立执行。", 
                            font=('Microsoft YaHei', 9), fg='#666666', justify=tk.LEFT)
        tip_label.pack()
    
    def _copy_all_groups_to_cad(self, preview=False):
        """复制所有分组到CAD"""
        # 调试信息
        print(f"调试信息 - 开始复制，分组数量: {len(self.coordinate_groups)}")
        
        # 生成纯CAD命令
        pure_commands = []
        
        for group_name, coordinates in self.coordinate_groups.items():
            print(f"调试信息 - 处理分组: {group_name}, 坐标数量: {len(coordinates)}")
            if len(coordinates) > 0:
                group_commands = self.generate_cad_commands(coordinates)
                command_lines_count = len(group_commands.split('\n')) if group_commands else 0
                print(f"调试信息 - 生成的命令: {command_lines_count} 行")
                if group_commands and group_commands != "未找到有效的坐标数据":
                    command_lines = group_commands.split('\n')
                    for line in command_lines:
                        if line.strip():
                            pure_commands.append(line.strip())
                    pure_commands.append("")
                    pure_commands.append("")
        
        content = "\n".join(pure_commands)
        print(f"调试信息 - 最终命令行数: {len(pure_commands)}")
        
        if content and content.strip():
            if preview:
                # 显示预览对话框
                self._show_preview_dialog(content, "所有分组的CAD命令预览")
            else:
                # 直接复制并询问自动粘贴
                self.copy_content_to_clipboard(content)
                self._ask_auto_paste(content)
        else:
            messagebox.showwarning("警告", "没有可复制的CAD命令")
    
    def _ask_auto_paste(self, content):
        """询问是否自动粘贴"""
        if HAS_PYAUTOGUI:
            # 显示详细的警告和说明对话框
            self._show_auto_paste_warning(content)
        else:
            messagebox.showinfo("复制完成", 
                "CAD命令已复制到剪贴板\n"
                "请手动粘贴到CAD中")
    
    def _show_auto_paste_warning(self, content):
        """显示自动粘贴警告对话框"""
        warning_dialog = tk.Toplevel(self.root)
        warning_dialog.title("⚠️ 自动粘贴警告")
        warning_dialog.transient(self.root)
        warning_dialog.focus_set()
        
        # 居中显示
        warning_dialog.update_idletasks()
        x = (warning_dialog.winfo_screenwidth() // 2) - 350
        y = (warning_dialog.winfo_screenheight() // 2) - 300
        warning_dialog.geometry(f"+{x}+{y}")
        
        # 主容器
        main_frame = tk.Frame(warning_dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 警告标题
        warning_title = tk.Label(main_frame, text="⚠️ 自动粘贴功能警告", 
                                font=('Microsoft YaHei', 14, 'bold'), fg='#dc3545')
        warning_title.pack(pady=(0, 15))
        
        # 详细说明
        desc_frame = tk.Frame(main_frame)
        desc_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 使用滚动文本框显示详细说明
        text_widget = tk.Text(desc_frame, wrap=tk.WORD, width=70, height=12,
                             font=('Microsoft YaHei', 9))
        scrollbar = ttk.Scrollbar(desc_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 插入详细说明
        warning_text = """🚨 重要警告：

⚠️ 为什么需要模拟键盘操作？
• 由于CAD的命令行限制，无法一次性执行多个分组的多段线命令
• 当多个分组的多段线连续执行时，CAD会将它们合并为一个多段线
• 模拟键盘操作是为了确保每个分组的多段线都能独立执行
• 这是为了克服CAD命令限制而设计的妥协方案

⚠️ 潜在风险：
• 此功能将模拟键盘和鼠标操作
• 可能会影响当前正在运行的其他程序
• 如果CAD窗口未激活，命令可能发送到错误位置
• 在自动操作期间，请勿移动鼠标或使用键盘

📋 操作说明：
• 程序将在5秒后开始自动操作
• 请确保CAD窗口已打开并处于活动状态
• 请确保CAD命令行为空，没有正在执行的命令
• 建议先保存当前CAD文件

🔧 安全建议：
• 使用前请备份重要的CAD文件
• 确保没有其他重要程序在前台运行
• 如果出现问题，可以按Ctrl+Alt+Del中断操作
• 建议先在测试环境中验证功能

⚡ 自动操作流程：
1. 程序将切换到CAD窗口
2. 粘贴CAD命令到命令行
3. 按回车键执行每个命令
4. 在命令之间添加适当延迟
5. 确保每个分组的多段线独立执行

💡 技术说明：
• 手动复制粘贴时，CAD会将连续的多段线命令合并
• 模拟键盘操作通过在每个命令后按回车键来强制分离
• 这样可以确保每个分组的多段线都是独立的图形对象

❓ 是否继续？
选择"是"将开始自动操作，选择"否"将只复制到剪贴板。"""
        
        text_widget.insert(tk.END, warning_text)
        text_widget.config(state=tk.DISABLED)
        
        # 按钮区域
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        def confirm_auto_paste():
            """确认自动粘贴"""
            warning_dialog.destroy()
            self.auto_paste_to_cad(content)
        
        def manual_paste():
            """选择手动粘贴"""
            warning_dialog.destroy()
            messagebox.showinfo("复制完成", 
                "CAD命令已复制到剪贴板\n"
                "请切换到CAD窗口并手动粘贴")
        
        def cancel_operation():
            """取消操作"""
            warning_dialog.destroy()
        
        # 按钮布局
        btn_frame = tk.Frame(button_frame)
        btn_frame.pack(expand=True)
        
        confirm_btn = ttk.Button(btn_frame, text="✅ 确认自动粘贴", 
                                 command=confirm_auto_paste, width=18)
        confirm_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        manual_btn = ttk.Button(btn_frame, text="📋 手动粘贴", 
                                command=manual_paste, width=12)
        manual_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = ttk.Button(btn_frame, text="❌ 取消", 
                                command=cancel_operation, width=12)
        cancel_btn.pack(side=tk.LEFT)
    
    def _show_preview_dialog(self, content, title):
        """显示预览对话框"""
        preview_dialog = tk.Toplevel(self.root)
        preview_dialog.title(title)
        preview_dialog.transient(self.root)
        
        # 居中显示
        preview_dialog.update_idletasks()
        x = (preview_dialog.winfo_screenwidth() // 2) - 300
        y = (preview_dialog.winfo_screenheight() // 2) - 200
        preview_dialog.geometry(f"+{x}+{y}")
        
        # 预览内容
        preview_frame = tk.Frame(preview_dialog)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(preview_frame, text=title, 
                              font=('Microsoft YaHei', 12, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # 文本区域
        text_frame = tk.Frame(preview_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, width=60, height=15,
                             font=('Consolas', 9))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 插入内容
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)
        
        # 按钮区域
        button_frame = tk.Frame(preview_frame)
        button_frame.pack(fill=tk.X)
        
        def confirm_copy():
            """确认复制"""
            preview_dialog.destroy()
            self.copy_content_to_clipboard(content)
            self._ask_auto_paste(content)
        
        def cancel_preview():
            """取消预览"""
            preview_dialog.destroy()
        
        confirm_btn = ttk.Button(button_frame, text="✅ 确认复制", command=confirm_copy)
        confirm_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = ttk.Button(button_frame, text="❌ 取消", command=cancel_preview)
        cancel_btn.pack(side=tk.LEFT)
    
    def show_group_copy_dialog(self):
        """显示分组复制选择对话框"""
        # 检查是否有分组数据
        if not self.coordinate_groups:
            messagebox.showwarning("警告", "没有分组数据")
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title("选择要复制的分组")
        
        dialog.transient(self.root)
        # 完全移除阻塞，允许同时操作主界面
        # dialog.grab_set()  # 注释掉这行，不阻塞主界面
        dialog.focus_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 300
        y = (dialog.winfo_screenheight() // 2) - 250
        dialog.geometry(f"+{x}+{y}")
        
        # 主容器
        main_frame = tk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(main_frame, text="选择要复制的分组", 
                              font=('Microsoft YaHei', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # 说明
        desc_label = tk.Label(main_frame, text="✅ 勾选要复制的分组，然后选择复制方式", 
                             font=('Microsoft YaHei', 10))
        desc_label.pack(pady=(0, 15))
        
        # 统计信息
        total_groups = len([coords for coords in self.coordinate_groups.values() if len(coords) > 0])
        stats_label = tk.Label(main_frame, text=f"📊 共找到 {total_groups} 个有效分组", 
                              font=('Microsoft YaHei', 9), fg='#666666')
        stats_label.pack(pady=(0, 20))
        
        # 分组选择区域（固定高度）
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 计算分组数量并动态调整滚动区域高度
        group_count = len([coords for coords in self.coordinate_groups.values() if len(coords) > 0])
        
        # 根据分组数量动态调整高度
        # 每个分组约25px，最小200px，最大400px
        if group_count <= 8:
            list_height = max(200, group_count * 25 + 50)
        else:
            list_height = 400
        
        # 创建滚动区域
        canvas = tk.Canvas(list_frame, height=list_height)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 分组选择变量
        group_vars = {}
        
        # 添加分组选项
        actual_group_count = 0
        for group_name, coordinates in self.coordinate_groups.items():
            if len(coordinates) > 0:
                var = tk.BooleanVar(value=True)  # 默认全选
                group_vars[group_name] = var
                
                frame_item = tk.Frame(scrollable_frame)
                frame_item.pack(fill=tk.X, pady=3)
                
                tk.Checkbutton(frame_item, text=f"{group_name} ({len(coordinates)}个点)", 
                              variable=var, font=('Microsoft YaHei', 10)).pack(side=tk.LEFT)
                actual_group_count += 1
        
        # 如果没有分组，显示提示
        if actual_group_count == 0:
            no_group_label = tk.Label(scrollable_frame, text="没有找到有效的分组数据", 
                                     font=('Microsoft YaHei', 10), fg='red')
            no_group_label.pack(pady=20)
        
        # 全选/取消全选按钮
        select_frame = tk.Frame(main_frame)
        select_frame.pack(fill=tk.X, pady=(0, 15))
        
        def select_all():
            for var in group_vars.values():
                var.set(True)
        
        def deselect_all():
            for var in group_vars.values():
                var.set(False)
        
        # 更美观的按钮布局
        select_btn_frame = tk.Frame(select_frame)
        select_btn_frame.pack(expand=True)
        
        select_all_btn = ttk.Button(select_btn_frame, text="✅ 全选", 
                                    command=select_all, width=12)
        select_all_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        deselect_all_btn = ttk.Button(select_btn_frame, text="❌ 取消全选", 
                                      command=deselect_all, width=12)
        deselect_all_btn.pack(side=tk.LEFT)
        
        # 操作按钮区域
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        def copy_selected_groups():
            selected_content = []
            
            for group_name, var in group_vars.items():
                if var.get():
                    coordinates = self.coordinate_groups[group_name]
                    group_commands = self.generate_cad_commands(coordinates)
                    if group_commands and group_commands != "未找到有效的坐标数据":
                        # 将多行命令分割并添加到列表中
                        command_lines = group_commands.split('\n')
                        for line in command_lines:
                            if line.strip():  # 只添加非空行
                                selected_content.append(line.strip())
            
            if selected_content:
                content = "\n".join(selected_content)
                
                # 显示预览对话框
                preview_dialog = tk.Toplevel(dialog)
                preview_dialog.title("CAD命令预览")
                preview_dialog.transient(dialog)
                
                # 居中显示
                preview_dialog.update_idletasks()
                x = (preview_dialog.winfo_screenwidth() // 2) - 300
                y = (preview_dialog.winfo_screenheight() // 2) - 200
                preview_dialog.geometry(f"+{x}+{y}")
                
                # 预览内容
                preview_label = tk.Label(preview_dialog, text="即将复制到CAD的命令:", 
                                       font=('Microsoft YaHei', 10, 'bold'))
                preview_label.pack(pady=(10, 5))
                
                # 文本框显示命令
                text_widget = scrolledtext.ScrolledText(preview_dialog, height=15, width=70)
                text_widget.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
                text_widget.insert(1.0, content)
                text_widget.config(state=tk.DISABLED)
                
                # 按钮
                button_frame = tk.Frame(preview_dialog)
                button_frame.pack(pady=10)
                
                def confirm_copy():
                    self.copy_content_to_clipboard(content)
                    preview_dialog.destroy()
                    dialog.destroy()
                
                def cancel_preview():
                    preview_dialog.destroy()
                
                ttk.Button(button_frame, text="确认复制", command=confirm_copy, width=12).pack(side=tk.LEFT, padx=5)
                ttk.Button(button_frame, text="取消", command=cancel_preview, width=12).pack(side=tk.LEFT, padx=5)
            else:
                messagebox.showwarning("警告", "请至少选择一个分组")
        
        def copy_all():
            # 生成纯CAD命令，去除注释和空行
            pure_commands = []
            
            for group_name, coordinates in self.coordinate_groups.items():
                if len(coordinates) > 0:
                    # 只生成CAD命令，不包含注释
                    group_commands = self.generate_cad_commands(coordinates)
                    if group_commands and group_commands != "未找到有效的坐标数据":
                        # 将多行命令分割并添加到列表中
                        command_lines = group_commands.split('\n')
                        for line in command_lines:
                            if line.strip():  # 只添加非空行
                                pure_commands.append(line.strip())
                        # 在每个分组后添加明确的空行分隔
                        pure_commands.append("")
                        # 添加回车键模拟，确保CAD命令中断
                        pure_commands.append("")
            
            # 用换行符连接所有命令
            content = "\n".join(pure_commands)
            
            # 调试信息
            print(f"调试: 生成了 {len(pure_commands)} 行命令")
            print(f"调试: 内容长度: {len(content)}")
            if content:
                print(f"调试: 前200个字符: {content[:200]}")
            else:
                print("调试: 内容为空")
            
            # 显示预览对话框
            if content and content.strip():
                preview_dialog = tk.Toplevel(dialog)
                preview_dialog.title("CAD命令预览")
                preview_dialog.transient(dialog)
                
                # 居中显示
                preview_dialog.update_idletasks()
                x = (preview_dialog.winfo_screenwidth() // 2) - 300
                y = (preview_dialog.winfo_screenheight() // 2) - 200
                preview_dialog.geometry(f"+{x}+{y}")
                
                # 预览内容
                preview_label = tk.Label(preview_dialog, text="即将复制到CAD的命令:", 
                                       font=('Microsoft YaHei', 10, 'bold'))
                preview_label.pack(pady=(10, 5))
                
                # 文本框显示命令
                text_widget = scrolledtext.ScrolledText(preview_dialog, height=15, width=70)
                text_widget.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
                text_widget.insert(1.0, content)
                text_widget.config(state=tk.DISABLED)
                
                # 按钮
                button_frame = tk.Frame(preview_dialog)
                button_frame.pack(pady=10)
                
                def confirm_copy():
                    self.copy_content_to_clipboard(content)
                    preview_dialog.destroy()
                    dialog.destroy()
                
                def cancel_preview():
                    preview_dialog.destroy()
                
                ttk.Button(button_frame, text="确认复制", command=confirm_copy, width=12).pack(side=tk.LEFT, padx=5)
                ttk.Button(button_frame, text="取消", command=cancel_preview, width=12).pack(side=tk.LEFT, padx=5)
            else:
                messagebox.showwarning("警告", f"没有可复制的CAD命令\n调试信息: 生成了{len(pure_commands)}行命令")
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        # 按钮布局 - 更清晰的选项
        btn_frame = tk.Frame(button_frame)
        btn_frame.pack(expand=True)
        
        # 主要操作按钮
        copy_btn = ttk.Button(btn_frame, text="📋 复制选中分组", 
                              command=copy_selected_groups, width=18)
        copy_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        copy_all_btn = ttk.Button(btn_frame, text="📋 复制全部", 
                                  command=copy_all, width=12)
        copy_all_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = ttk.Button(btn_frame, text="❌ 取消", 
                                command=cancel, width=12)
        cancel_btn.pack(side=tk.LEFT)
        
        # 添加提示信息
        tip_frame = tk.Frame(main_frame)
        tip_frame.pack(fill=tk.X, pady=(15, 0))
        
        tip_label = tk.Label(tip_frame, text="💡 提示：\n• 复制选中分组：只复制勾选的分组\n• 复制全部：复制所有分组（忽略勾选状态）", 
                            font=('Microsoft YaHei', 9), fg='#666666', justify=tk.LEFT)
        tip_label.pack()
        
        # 配置滚动条
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 设置焦点但不阻塞主界面
        dialog.focus_set()
        # 完全移除阻塞，允许同时操作主界面
    
    def copy_content_to_clipboard(self, content):
        """复制内容到剪贴板"""
        try:
            # 使用tkinter的剪贴板
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            
            # 使用状态栏提示而不是弹窗
            self.update_status("✅ CAD命令已复制到剪贴板", '#28a745')
            # 2秒后恢复默认状态
            self.root.after(2000, self.reset_status)
            
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {str(e)}")
            self.update_status("复制失败", '#dc3545')
            # 2秒后恢复默认状态
            self.root.after(2000, self.reset_status)
    
    def auto_paste_to_cad(self, content):
        """自动粘贴到CAD并模拟按键中断命令"""
        if not HAS_PYAUTOGUI:
            messagebox.showwarning("警告", "pyautogui未安装，无法使用自动粘贴功能")
            return False
        
        try:
            # 显示倒计时对话框
            self._show_countdown_dialog(content)
            return True
        except Exception as e:
            messagebox.showerror("错误", f"自动粘贴失败: {str(e)}")
            return False
    
    def _show_countdown_dialog(self, content):
        """显示倒计时对话框"""
        countdown_dialog = tk.Toplevel(self.root)
        countdown_dialog.title("⏰ 准备自动粘贴")
        countdown_dialog.transient(self.root)
        countdown_dialog.focus_set()
        
        # 居中显示
        countdown_dialog.update_idletasks()
        x = (countdown_dialog.winfo_screenwidth() // 2) - 250
        y = (countdown_dialog.winfo_screenheight() // 2) - 150
        countdown_dialog.geometry(f"+{x}+{y}")
        
        # 主容器
        main_frame = tk.Frame(countdown_dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(main_frame, text="⏰ 准备自动粘贴到CAD", 
                              font=('Microsoft YaHei', 12, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # 倒计时标签
        countdown_label = tk.Label(main_frame, text="5", 
                                  font=('Microsoft YaHei', 24, 'bold'), fg='#dc3545')
        countdown_label.pack(pady=(0, 15))
        
        # 说明
        desc_label = tk.Label(main_frame, text="请确保：\n• CAD窗口已打开并处于活动状态\n• 没有正在执行的CAD命令\n• 已保存重要文件\n\n💡 自动粘贴将确保每个分组的多段线独立执行，\n避免CAD将多个分组合并为一个多段线。", 
                             font=('Microsoft YaHei', 10), justify=tk.LEFT)
        desc_label.pack(pady=(0, 15))
        
        # 取消按钮
        def cancel_operation():
            countdown_dialog.destroy()
            messagebox.showinfo("已取消", "自动粘贴操作已取消")
        
        cancel_btn = ttk.Button(main_frame, text="❌ 取消操作", command=cancel_operation)
        cancel_btn.pack(pady=(10, 0))
        
        # 倒计时功能
        def update_countdown(count):
            if count > 0:
                countdown_label.config(text=str(count))
                countdown_dialog.after(1000, lambda: update_countdown(count - 1))
            else:
                countdown_dialog.destroy()
                self._execute_cad_commands(content)
        
        # 开始倒计时
        update_countdown(5)
    
    def _execute_cad_commands(self, content):
        """执行CAD命令并模拟按键"""
        try:
            # 显示执行进度对话框
            progress_dialog = tk.Toplevel(self.root)
            progress_dialog.title("⚡ 正在执行CAD命令")
            progress_dialog.transient(self.root)
            progress_dialog.focus_set()
            
            # 居中显示
            progress_dialog.update_idletasks()
            x = (progress_dialog.winfo_screenwidth() // 2) - 250
            y = (progress_dialog.winfo_screenheight() // 2) - 150
            progress_dialog.geometry(f"+{x}+{y}")
            
            # 主容器
            main_frame = tk.Frame(progress_dialog)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # 标题
            title_label = tk.Label(main_frame, text="⚡ 正在执行CAD命令", 
                                  font=('Microsoft YaHei', 12, 'bold'))
            title_label.pack(pady=(0, 15))
            
            # 进度说明
            progress_label = tk.Label(main_frame, text="正在粘贴并执行命令...", 
                                     font=('Microsoft YaHei', 10))
            progress_label.pack(pady=(0, 15))
            
            # 警告信息
            warning_label = tk.Label(main_frame, text="⚠️ 请勿移动鼠标或使用键盘", 
                                    font=('Microsoft YaHei', 9), fg='#dc3545')
            warning_label.pack(pady=(0, 15))
            
            def execute_with_progress():
                """带进度反馈的执行"""
                try:
                    # 初始化pyautogui设置
                    pyautogui.FAILSAFE = True
                    pyautogui.PAUSE = 0.1
                    
                    # 分割命令为单独的多段线
                    commands = content.split('\n')
                    current_command = []
                    command_count = 0
                    
                    for line in commands:
                        if line.strip():
                            if line.startswith('pline'):
                                command_count += 1
                                # 更新进度
                                progress_label.config(text=f"正在执行第 {command_count} 个命令...")
                                progress_dialog.update()
                                
                                # 如果有待执行的命令，先执行它
                                if current_command:
                                    self._execute_single_pline(current_command)
                                    current_command = []
                                # 开始新的多段线命令
                                current_command = [line]
                            else:
                                current_command.append(line)
                    
                    # 执行最后一个命令
                    if current_command:
                        command_count += 1
                        progress_label.config(text=f"正在执行第 {command_count} 个命令...")
                        progress_dialog.update()
                        self._execute_single_pline(current_command)
                    
                    # 完成
                    progress_dialog.destroy()
                    self.update_status("✅ 自动执行CAD命令完成", '#28a745')
                    self._show_completion_dialog(command_count)
                    
                except Exception as e:
                    progress_dialog.destroy()
                    self._show_error_dialog(str(e))
                    self.update_status("❌ 自动执行失败", '#dc3545')
                finally:
                    # 确保资源被释放
                    self._cleanup_pyautogui()
            
            # 延迟执行，让对话框先显示
            progress_dialog.after(1000, execute_with_progress)
            
        except Exception as e:
            messagebox.showerror("错误", f"执行CAD命令失败: {str(e)}")
            self.update_status("❌ 自动执行失败", '#dc3545')
    
    def _show_completion_dialog(self, command_count):
        """显示操作完成提示对话框"""
        completion_dialog = tk.Toplevel(self.root)
        completion_dialog.title("✅ 操作完成")
        completion_dialog.transient(self.root)
        completion_dialog.focus_set()
        
        # 设置对话框为顶层窗口
        completion_dialog.attributes('-topmost', True)
        
        # 居中显示
        completion_dialog.update_idletasks()
        x = (completion_dialog.winfo_screenwidth() // 2) - 300
        y = (completion_dialog.winfo_screenheight() // 2) - 200
        completion_dialog.geometry(f"+{x}+{y}")
        
        # 主容器
        main_frame = tk.Frame(completion_dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # 成功图标和标题
        success_frame = tk.Frame(main_frame)
        success_frame.pack(pady=(0, 20))
        
        success_title = tk.Label(success_frame, text="✅ 操作完成", 
                                font=('Microsoft YaHei', 16, 'bold'), fg='#28a745')
        success_title.pack()
        
        # 详细信息
        info_frame = tk.Frame(main_frame)
        info_frame.pack(pady=(0, 25))
        
        # 执行统计
        stats_label = tk.Label(info_frame, text=f"📊 执行统计：", 
                              font=('Microsoft YaHei', 12, 'bold'))
        stats_label.pack(pady=(0, 10))
        
        command_label = tk.Label(info_frame, text=f"• 成功执行了 {command_count} 个CAD命令", 
                                font=('Microsoft YaHei', 11))
        command_label.pack(pady=2)
        
        group_label = tk.Label(info_frame, text="• 每个分组的多段线都已独立执行", 
                              font=('Microsoft YaHei', 11))
        group_label.pack(pady=2)
        
        status_label = tk.Label(info_frame, text="• 所有命令已成功粘贴到CAD", 
                               font=('Microsoft YaHei', 11))
        status_label.pack(pady=2)
        
        # 操作结果
        result_frame = tk.Frame(main_frame)
        result_frame.pack(pady=(0, 25))
        
        result_title = tk.Label(result_frame, text="🎯 操作结果：", 
                               font=('Microsoft YaHei', 12, 'bold'))
        result_title.pack(pady=(0, 10))
        
        result1 = tk.Label(result_frame, text="• 每个分组的多段线都是独立的图形对象", 
                           font=('Microsoft YaHei', 10), fg='#28a745')
        result1.pack(pady=2)
        
        result2 = tk.Label(result_frame, text="• 避免了CAD将多个分组合并的问题", 
                           font=('Microsoft YaHei', 10), fg='#28a745')
        result2.pack(pady=2)
        
        result3 = tk.Label(result_frame, text="• 可以继续在CAD中进行编辑和修改", 
                           font=('Microsoft YaHei', 10), fg='#28a745')
        result3.pack(pady=2)
        
        # 提示信息
        tip_frame = tk.Frame(main_frame)
        tip_frame.pack(pady=(0, 20))
        
        tip_label = tk.Label(tip_frame, text="💡 提示：现在可以继续在CAD中工作，\n所有图形都已成功创建并可以独立编辑。", 
                            font=('Microsoft YaHei', 10), fg='#666666', justify=tk.CENTER)
        tip_label.pack()
        
        # 确认按钮
        def close_dialog():
            completion_dialog.destroy()
        
        confirm_btn = ttk.Button(main_frame, text="✅ 确认", 
                                 command=close_dialog, width=15)
        confirm_btn.pack()
        
        # 自动关闭（10秒后）
        completion_dialog.after(10000, close_dialog)
        
        # 设置焦点到确认按钮
        confirm_btn.focus_set()
    
    def _show_error_dialog(self, error_message):
        """显示错误提示对话框"""
        error_dialog = tk.Toplevel(self.root)
        error_dialog.title("❌ 操作失败")
        error_dialog.transient(self.root)
        error_dialog.focus_set()
        
        # 设置对话框为顶层窗口
        error_dialog.attributes('-topmost', True)
        
        # 居中显示
        error_dialog.update_idletasks()
        x = (error_dialog.winfo_screenwidth() // 2) - 300
        y = (error_dialog.winfo_screenheight() // 2) - 200
        error_dialog.geometry(f"+{x}+{y}")
        
        # 主容器
        main_frame = tk.Frame(error_dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # 错误图标和标题
        error_frame = tk.Frame(main_frame)
        error_frame.pack(pady=(0, 20))
        
        error_title = tk.Label(error_frame, text="❌ 操作失败", 
                              font=('Microsoft YaHei', 16, 'bold'), fg='#dc3545')
        error_title.pack()
        
        # 错误信息
        error_info_frame = tk.Frame(main_frame)
        error_info_frame.pack(pady=(0, 25))
        
        error_desc = tk.Label(error_info_frame, text="自动执行CAD命令时发生错误：", 
                             font=('Microsoft YaHei', 12, 'bold'))
        error_desc.pack(pady=(0, 10))
        
        # 错误详情（可滚动）
        error_text_frame = tk.Frame(error_info_frame)
        error_text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        error_text = tk.Text(error_text_frame, wrap=tk.WORD, width=50, height=6,
                            font=('Consolas', 9))
        error_scrollbar = ttk.Scrollbar(error_text_frame, orient="vertical", command=error_text.yview)
        error_text.configure(yscrollcommand=error_scrollbar.set)
        
        error_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        error_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 插入错误信息
        error_text.insert(tk.END, error_message)
        error_text.config(state=tk.DISABLED)
        
        # 解决建议
        solution_frame = tk.Frame(main_frame)
        solution_frame.pack(pady=(0, 20))
        
        solution_title = tk.Label(solution_frame, text="🔧 解决建议：", 
                                 font=('Microsoft YaHei', 12, 'bold'))
        solution_title.pack(pady=(0, 10))
        
        solution1 = tk.Label(solution_frame, text="• 检查CAD窗口是否处于活动状态", 
                            font=('Microsoft YaHei', 10))
        solution1.pack(pady=2)
        
        solution2 = tk.Label(solution_frame, text="• 确保没有其他程序干扰", 
                            font=('Microsoft YaHei', 10))
        solution2.pack(pady=2)
        
        solution3 = tk.Label(solution_frame, text="• 尝试使用手动复制粘贴方式", 
                            font=('Microsoft YaHei', 10))
        solution3.pack(pady=2)
        
        # 按钮区域
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def close_dialog():
            error_dialog.destroy()
        
        def retry_manual():
            """重试手动复制"""
            error_dialog.destroy()
            messagebox.showinfo("手动复制", "CAD命令已复制到剪贴板\n请手动粘贴到CAD中")
        
        # 按钮布局
        btn_frame = tk.Frame(button_frame)
        btn_frame.pack(expand=True)
        
        retry_btn = ttk.Button(btn_frame, text="📋 手动复制", 
                               command=retry_manual, width=12)
        retry_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        close_btn = ttk.Button(btn_frame, text="❌ 关闭", 
                               command=close_dialog, width=12)
        close_btn.pack(side=tk.LEFT)
        
        # 自动关闭（15秒后）
        error_dialog.after(15000, close_dialog)
        
        # 设置焦点到关闭按钮
        close_btn.focus_set()
    
    def _execute_single_pline(self, command_lines):
        """执行单个多段线命令"""
        try:
            # 设置pyautogui的安全设置，避免意外操作
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.1  # 减少延迟，提高效率
            
            # 粘贴命令
            pyautogui.hotkey('ctrl', 'v')
            pyautogui.sleep(0.3)  # 减少延迟
            
            # 按回车执行命令
            pyautogui.press('enter')
            pyautogui.sleep(0.3)  # 减少延迟
            
            # 再次按回车确保命令结束
            pyautogui.press('enter')
            pyautogui.sleep(0.2)  # 减少延迟
            
        except Exception as e:
            print(f"执行命令失败: {e}")
            # 确保在异常情况下也能释放资源
            self._cleanup_pyautogui()
        finally:
            # 确保资源被释放
            self._cleanup_pyautogui()
    
    def _cleanup_pyautogui(self):
        """清理pyautogui资源"""
        try:
            # 重置pyautogui设置
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.1
            
            # 强制垃圾回收
            import gc
            gc.collect()
            
            print("pyautogui资源已清理")
        except Exception as e:
            print(f"清理pyautogui资源时出现错误: {e}")
    

    
    def copy_cad_commands(self):
        """复制CAD命令到剪贴板"""
        content = self.cad_text.get(1.0, tk.END).strip()
        if content:
            try:
                # 使用tkinter的剪贴板
                self.root.clipboard_clear()
                self.root.clipboard_append(content)
                messagebox.showinfo("成功", "CAD命令已复制到剪贴板")
            except Exception as e:
                messagebox.showerror("错误", f"复制失败: {str(e)}")
        else:
            messagebox.showwarning("警告", "没有可复制的内容")
    
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
        self.cad_text.delete(1.0, tk.END)
        self.preview_text.delete(1.0, tk.END)
        self.coordinates = []
        
        # 清除图形
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
    
    def cleanup_matplotlib(self):
        """清理matplotlib资源"""
        try:
            if HAS_MATPLOTLIB:
                # 关闭所有图形
                plt.close('all')
                # 清除当前图形和轴
                plt.clf()
                plt.cla()
                # 强制垃圾回收
                import gc
                gc.collect()
        except Exception as e:
            print(f"清理matplotlib资源时出现错误: {e}")
    
    def cleanup_resources(self):
        """清理所有资源"""
        try:
            # 清理matplotlib资源
            self.cleanup_matplotlib()
            
            # 清理pyautogui资源
            self._cleanup_pyautogui()
            
            # 清理坐标数据
            self.coordinates = []
            self.coordinate_groups = {}
            
            # 清理图形框架
            for widget in self.graph_frame.winfo_children():
                widget.destroy()
            
            # 强制垃圾回收
            import gc
            gc.collect()
            
            print("所有资源清理完成")
                
        except Exception as e:
            print(f"清理资源时出现错误: {e}")

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
    def on_closing():
        try:
            print("正在关闭程序，清理资源...")
            # 清理应用资源
            app.cleanup_resources()
            print("资源清理完成，正在退出...")
            # 强制退出程序，确保没有残留进程
            import os
            os._exit(0)
        except Exception as e:
            print(f"关闭程序时出现错误: {e}")
            # 即使出错也要强制退出
            import os
            os._exit(0)
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 