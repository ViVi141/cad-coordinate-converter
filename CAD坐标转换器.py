#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CAD坐标转换器
版本: 1.0.0
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

# 版本信息
VERSION = "1.0.0"
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
        self.root.geometry("1400x800")
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
        
        # 编译正则表达式以提高性能 - 支持科学计数法，更严格的匹配
        coord_pattern = re.compile(r'^\s*([+-]?\d+\.?\d*(?:[eE][+-]?\d+)?)\s*,\s*([+-]?\d+\.?\d*(?:[eE][+-]?\d+)?)\s*,?\s*([+-]?\d+\.?\d*(?:[eE][+-]?\d+)?)?\s*$')
        
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
            match = coord_pattern.match(line)
            if match:
                try:
                    x, y, z = match.group(1), match.group(2), match.group(3) if match.group(3) else "0"
                    coord = (float(x), float(y), float(z))
                    
                    # 验证坐标值的合理性
                    if abs(coord[0]) > 1e10 or abs(coord[1]) > 1e10 or abs(coord[2]) > 1e10:
                        print(f"警告：跳过异常坐标值: {coord}")
                        continue
                        
                    coordinates.append(coord)
                    
                    # 同时添加到分组中
                    if current_group not in groups:
                        groups[current_group] = []
                    groups[current_group].append(coord)
                except ValueError:
                    # 跳过无效的坐标数据
                    print(f"警告：跳过无效坐标: {line}")
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

作者: {AUTHOR} ({EMAIL})
        """
        messagebox.showinfo("快捷键帮助", help_text)
    
    def generate_cad_commands(self, coordinates, is_grouped=False):
        """生成CAD命令"""
        commands = []
        
        if not coordinates:
            return "未找到有效的坐标数据"
        
        convert_type = self.convert_type.get()
        add_text = self.add_text_var.get()
        text_height = self.text_height_var.get()
        
        # 检查是否包含Z坐标
        has_z_coords = any(len(coord) > 2 and coord[2] != 0 for coord in coordinates)
        
        # 添加CAD命令说明
        commands.append(f"# CAD命令 - {convert_type.upper()} 格式")
        commands.append(f"# 共{len(coordinates)}个坐标点")
        if has_z_coords:
            commands.append("# 包含Z坐标 (3D)")
        else:
            commands.append("# 仅X,Y坐标 (2D)")
        commands.append("")
        
        if convert_type == "pline":
            # 生成多段线命令 - 改进格式
            if has_z_coords:
                # 3D多段线
                commands.append("pline")
                for x, y, z in coordinates:
                    commands.append(f"{x},{y},{z}")
                # 添加闭合选项（可选）
                if len(coordinates) > 2:
                    commands.append("C")  # 使用C终止多段线
                else:
                    commands.append("C^")  # 使用C^终止多段线
            else:
                # 2D多段线
                commands.append("pline")
                for x, y, z in coordinates:
                    commands.append(f"{x},{y}")
                # 添加闭合选项（可选）
                if len(coordinates) > 2:
                    commands.append("C")  # 使用C终止多段线
                else:
                    commands.append("C^")  # 使用C^终止多段线
            
        elif convert_type == "line":
            # 生成直线命令 - 连接相邻点形成线段
            # 如果是分组模式，确保每个组内的线段是独立的
            for i in range(len(coordinates) - 1):
                x1, y1, z1 = coordinates[i]
                x2, y2, z2 = coordinates[i+1]
                if has_z_coords:
                    commands.append(f"line {x1},{y1},{z1} {x2},{y2},{z2}")
                else:
                    commands.append(f"line {x1},{y1} {x2},{y2}")
            # 添加空行结束line命令组
            if len(coordinates) > 1:
                commands.append("")
                
        elif convert_type == "point":
            # 生成点命令
            for x, y, z in coordinates:
                if has_z_coords:
                    commands.append(f"point {x},{y},{z}")
                else:
                    commands.append(f"point {x},{y}")
            # 添加空行结束point命令组
            if coordinates:
                commands.append("")
        
        # 添加文字标注
        if add_text:
            commands.append("")  # 空行分隔
            commands.append("# 文字标注")
            for i, (x, y, z) in enumerate(coordinates, 1):
                if has_z_coords:
                    commands.append(f'text j ml {x},{y},{z} {text_height} 0 "点{i}"')
                else:
                    commands.append(f'text j ml {x},{y} {text_height} 0 "点{i}"')
            # 添加空行结束text命令组
            if coordinates:
                commands.append("")
        
        return "\n".join(commands)
    
    def generate_grouped_cad_commands(self, groups):
        """按分组生成CAD命令 - 确保每个组都是独立的闭合图形"""
        commands = []
        
        for group_name, coordinates in groups.items():
            if not coordinates:
                continue
                
            commands.append(f"# {group_name}")
            commands.append(f"# 共{len(coordinates)}个坐标点")
            commands.append("")
            
            # 生成该组的CAD命令 - 传入is_grouped=True表示这是分组模式
            group_commands = self.generate_cad_commands(coordinates, is_grouped=True)
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
            
            # 改进的文件读取方式 - 流式处理
            coordinates = []
            groups = {}
            current_group = "默认组"
            line_count = 0
            valid_coords = 0
            
            # 编译正则表达式
            coord_pattern = re.compile(r'^\s*([+-]?\d+\.?\d*(?:[eE][+-]?\d+)?)\s*,\s*([+-]?\d+\.?\d*(?:[eE][+-]?\d+)?)\s*,?\s*([+-]?\d+\.?\d*(?:[eE][+-]?\d+)?)?\s*$')
            
            with open(self.file_path_var.get(), 'r', encoding='utf-8') as f:
                for line in f:
                    line_count += 1
                    line = line.strip()
                    
                    # 每处理1000行更新一次状态
                    if line_count % 1000 == 0:
                        self.update_status(f"正在解析坐标数据... (已处理{line_count}行，找到{valid_coords}个有效坐标)", '#007bff')
                        self.root.update()
                    
                    if not line or line.startswith('#'):
                        continue
                    
                    # 检查是否是分组标识
                    if line.startswith('第') and '组' in line:
                        current_group = line
                        if current_group not in groups:
                            groups[current_group] = []
                        continue
                    
                    # 匹配坐标格式
                    match = coord_pattern.match(line)
                    if match:
                        try:
                            x, y, z = match.group(1), match.group(2), match.group(3) if match.group(3) else "0"
                            coord = (float(x), float(y), float(z))
                            
                            # 验证坐标值的合理性
                            if abs(coord[0]) > 1e10 or abs(coord[1]) > 1e10 or abs(coord[2]) > 1e10:
                                continue
                            
                            # 检查是否启用分组处理
                            if self.group_processing_var.get() and len(groups) > 1:
                                # 分组模式：只添加到分组中，不添加到合并列表
                                if current_group not in groups:
                                    groups[current_group] = []
                                groups[current_group].append(coord)
                                valid_coords += 1
                            else:
                                # 非分组模式：添加到合并列表和分组中
                                coordinates.append(coord)
                                if current_group not in groups:
                                    groups[current_group] = []
                                groups[current_group].append(coord)
                                valid_coords += 1
                        except ValueError:
                            continue
            
            self.coordinates = coordinates
            self.coordinate_groups = groups
            
            # 提供详细的解析结果反馈
            if valid_coords == 0:
                messagebox.showwarning("警告", "文件中未找到有效的坐标数据\n请检查文件格式是否正确")
                self.update_status("就绪", '#6c757d')
                return
            elif valid_coords < len(coordinates):
                messagebox.showinfo("信息", f"解析完成：共处理{line_count}行，找到{valid_coords}个有效坐标点")
            
            self.update_status(f"解析完成：共{valid_coords}个有效坐标点", '#28a745')
            
            # 检查是否启用分组处理
            if self.group_processing_var.get() and len(self.coordinate_groups) > 1:
                # 分组模式：检查分组数据
                total_group_coords = sum(len(coords) for coords in self.coordinate_groups.values())
                if total_group_coords == 0:
                    messagebox.showwarning("警告", "文件中未找到有效的坐标数据")
                    self.update_status("就绪", '#6c757d')
                    return
                
                # 添加坐标数量检查
                if total_group_coords > 10000:
                    if not messagebox.askyesno("坐标数量过多", 
                        f"检测到{total_group_coords}个坐标点，处理可能需要较长时间。\n是否继续？"):
                        return
            else:
                # 非分组模式：检查合并的coordinates
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
                # 分组处理 - 使用分组数据，不使用合并的coordinates
                cad_commands = self.generate_grouped_cad_commands(self.coordinate_groups)
            else:
                # 非分组处理 - 使用合并的coordinates
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
                self.update_status("正在复制到剪贴板...", '#007bff')
                self.root.update()  # 强制更新界面
                self.copy_to_cad()
                self.update_status(f"✅ 转换完成！共处理 {len(self.coordinates)} 个坐标点，已自动复制", '#28a745')
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
    
    def show_group_copy_dialog(self):
        """显示分组复制选择对话框"""
        # 检查是否有分组数据
        if not self.coordinate_groups:
            messagebox.showwarning("警告", "没有分组数据")
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title("选择要复制的分组")
        
        # 计算最合适的窗口大小
        # 内容分析：
        # - 标题：约30px
        # - 说明：约25px  
        # - 分组列表：根据分组数量动态调整，最小300px
        # - 选择按钮：约40px
        # - 操作按钮：约50px
        # - 边距：上下左右各20px = 40px
        # - 总高度：30+25+300+40+50+40 = 485px
        
        # 宽度分析：
        # - 分组名称最长约50字符
        # - 按钮宽度：15+12+12 = 39字符
        # - 边距：左右各20px = 40px
        # - 总宽度：约600px
        
        dialog_width = 600
        dialog_height = 500
        
        dialog.geometry(f"{dialog_width}x{dialog_height}")
        dialog.transient(self.root)
        # 完全移除阻塞，允许同时操作主界面
        # dialog.grab_set()  # 注释掉这行，不阻塞主界面
        dialog.focus_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog_width // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog_height // 2)
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # 主容器
        main_frame = tk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(main_frame, text="选择要复制的分组", 
                              font=('Microsoft YaHei', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # 说明
        desc_label = tk.Label(main_frame, text="勾选要复制的分组，然后点击复制按钮", 
                             font=('Microsoft YaHei', 10))
        desc_label.pack(pady=(0, 20))
        
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
        
        ttk.Button(select_frame, text="全选", command=select_all, width=12).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(select_frame, text="取消全选", command=deselect_all, width=12).pack(side=tk.LEFT)
        
        # 操作按钮区域
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        def copy_selected_groups():
            selected_content = []
            
            for group_name, var in group_vars.items():
                if var.get():
                    coordinates = self.coordinate_groups[group_name]
                    group_commands = self.generate_cad_commands(coordinates)
                    selected_content.append(f"# {group_name}")
                    selected_content.append(f"# 共{len(coordinates)}个坐标点")
                    selected_content.append("")
                    selected_content.append(group_commands)
                    selected_content.append("")
            
            if selected_content:
                content = "\n".join(selected_content)
                self.copy_content_to_clipboard(content)
                dialog.destroy()
            else:
                messagebox.showwarning("警告", "请至少选择一个分组")
        
        def copy_all():
            content = self.cad_text.get(1.0, tk.END).strip()
            self.copy_content_to_clipboard(content)
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        # 按钮布局 - 确保按钮可见且间距合理
        ttk.Button(button_frame, text="复制选中分组", command=copy_selected_groups, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="复制全部", command=copy_all, width=12).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=cancel, width=12).pack(side=tk.RIGHT)
        
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
                
                # 记录清理成功
                print("matplotlib资源已清理")
        except Exception as e:
            # 改进异常处理
            error_msg = f"清理matplotlib资源时出现错误: {e}"
            print(error_msg)
            # 尝试强制清理
            try:
                import gc
                gc.collect()
                print("已尝试强制垃圾回收")
            except:
                pass
    
    def cleanup_resources(self):
        """清理所有资源"""
        try:
            # 清理matplotlib资源
            self.cleanup_matplotlib()
            
            # 清理坐标数据
            self.coordinates = []
            self.coordinate_groups = {}
            
            # 清理图形框架
            for widget in self.graph_frame.winfo_children():
                widget.destroy()
            
            # 强制垃圾回收
            import gc
            gc.collect()
                
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
            # 清理应用资源
            app.cleanup_resources()
            # 强制退出程序，确保没有残留进程
            import os
            os._exit(0)
        except Exception as e:
            print(f"关闭程序时出现错误: {e}")
            import os
            os._exit(0)
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 