import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib
import platform
from datetime import datetime
import json
import csv

# 设置中文字体
def set_chinese_font():
    """设置跨平台中文字体"""
    system = platform.system()
    if system == 'Windows':
        matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
    elif system == 'Darwin':
        matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Heiti TC', 'STHeiti']
    else:
        matplotlib.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Droid Sans Fallback', 'DejaVu Sans']
    matplotlib.rcParams['axes.unicode_minus'] = False

set_chinese_font()


class DatabaseManager:
    """SQLite数据库管理类"""

    def __init__(self, db_path="gdp_data.db"):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)

    def init_database(self):
        """初始化数据库表结构"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 创建省份信息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS provinces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                region TEXT NOT NULL
            )
        ''')

        # 创建GDP数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gdp_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                province_code TEXT NOT NULL,
                year INTEGER NOT NULL,
                gdp REAL NOT NULL,
                gdp_growth_rate REAL,
                population REAL,
                gdp_per_capita REAL,
                FOREIGN KEY (province_code) REFERENCES provinces(code),
                UNIQUE(province_code, year)
            )
        ''')

        conn.commit()
        conn.close()
        self.insert_sample_data()

    def insert_sample_data(self):
        """插入真实的中国各省份GDP数据（单位：亿元）"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 省份数据
        provinces = [
            ('BJ', '北京', '华北'), ('TJ', '天津', '华北'), ('HE', '河北', '华北'),
            ('SX', '山西', '华北'), ('NM', '内蒙古', '华北'),
            ('LN', '辽宁', '东北'), ('JL', '吉林', '东北'), ('HL', '黑龙江', '东北'),
            ('SH', '上海', '华东'), ('JS', '江苏', '华东'), ('ZJ', '浙江', '华东'),
            ('AH', '安徽', '华东'), ('FJ', '福建', '华东'), ('JX', '江西', '华东'),
            ('SD', '山东', '华东'),
            ('HA', '河南', '华中'), ('HB', '湖北', '华中'), ('HN', '湖南', '华中'),
            ('GD', '广东', '华南'), ('GX', '广西', '华南'), ('HI', '海南', '华南'),
            ('CQ', '重庆', '西南'), ('SC', '四川', '西南'), ('GZ', '贵州', '西南'),
            ('YN', '云南', '西南'), ('XZ', '西藏', '西南'),
            ('SN', '陕西', '西北'), ('GS', '甘肃', '西北'), ('QH', '青海', '西北'),
            ('NX', '宁夏', '西北'), ('XJ', '新疆', '西北')
        ]

        # 插入省份数据
        for code, name, region in provinces:
            cursor.execute('''
                INSERT OR IGNORE INTO provinces (code, name, region) VALUES (?, ?, ?)
            ''', (code, name, region))

        # 真实GDP数据（2019-2023年，单位：亿元）
        gdp_data = {
            'GD': [(2019, 107671, 6.2), (2020, 110761, 2.3), (2021, 124370, 8.0),
                   (2022, 129118, 1.9), (2023, 135673, 4.8)],
            'JS': [(2019, 99632, 6.1), (2020, 102700, 3.7), (2021, 116364, 8.6),
                   (2022, 122875, 2.8), (2023, 128222, 5.8)],
            'SD': [(2019, 71068, 5.5), (2020, 73129, 3.6), (2021, 83096, 8.3),
                   (2022, 87435, 3.9), (2023, 92069, 6.0)],
            'ZJ': [(2019, 62352, 6.8), (2020, 64613, 3.6), (2021, 73516, 8.5),
                   (2022, 77715, 3.1), (2023, 82553, 6.0)],
            'HA': [(2019, 54997, 7.0), (2020, 54997, 1.3), (2021, 58887, 6.3),
                   (2022, 61345, 3.1), (2023, 59132, 4.1)],
            'SC': [(2019, 46616, 7.5), (2020, 48599, 3.8), (2021, 53851, 8.2),
                   (2022, 56750, 2.9), (2023, 60133, 6.0)],
            'FJ': [(2019, 42395, 7.6), (2020, 43904, 3.3), (2021, 48810, 8.0),
                   (2022, 53110, 4.7), (2023, 54355, 4.5)],
            'HB': [(2019, 45828, 7.5), (2020, 43443, -5.0), (2021, 50013, 12.9),
                   (2022, 53735, 4.3), (2023, 55804, 6.0)],
            'HN': [(2019, 39752, 7.6), (2020, 41881, 3.8), (2021, 46063, 7.7),
                   (2022, 48670, 4.5), (2023, 50013, 4.6)],
            'SH': [(2019, 38155, 6.0), (2020, 38701, 1.7), (2021, 43214, 8.1),
                   (2022, 44653, -0.2), (2023, 47219, 5.0)],
            'AH': [(2019, 37114, 7.5), (2020, 38761, 3.9), (2021, 42959, 8.3),
                   (2022, 45045, 3.5), (2023, 47051, 5.8)],
            'HE': [(2019, 35105, 6.8), (2020, 36207, 3.9), (2021, 40391, 6.5),
                   (2022, 42370, 3.8), (2023, 43944, 5.5)],
            'BJ': [(2019, 35445, 6.1), (2020, 36103, 1.2), (2021, 40270, 8.5),
                   (2022, 41611, 0.7), (2023, 43761, 5.2)],
            'SN': [(2019, 25793, 6.0), (2020, 26182, 2.2), (2021, 29801, 6.5),
                   (2022, 32773, 4.3), (2023, 33786, 4.3)],
            'JX': [(2019, 24758, 8.0), (2020, 25692, 3.8), (2021, 29620, 8.8),
                   (2022, 32074, 4.7), (2023, 32200, 4.1)],
            'CQ': [(2019, 23606, 6.3), (2020, 25003, 3.9), (2021, 27894, 8.3),
                   (2022, 29129, 2.6), (2023, 30146, 6.1)],
            'LN': [(2019, 24909, 5.5), (2020, 25115, 0.6), (2021, 27584, 5.8),
                   (2022, 28975, 2.1), (2023, 30209, 5.3)],
            'YN': [(2019, 23224, 8.1), (2020, 23024, 4.0), (2021, 27147, 7.3),
                   (2022, 28954, 4.3), (2023, 30022, 4.4)],
            'GX': [(2019, 21237, 6.0), (2020, 22157, 3.7), (2021, 24741, 7.5),
                   (2022, 26301, 2.9), (2023, 27202, 5.2)],
            'SX': [(2019, 17026, 6.2), (2020, 17652, 3.6), (2021, 22590, 9.1),
                   (2022, 25643, 4.4), (2023, 25698, 5.0)],
            'NM': [(2019, 17213, 5.2), (2020, 17360, 0.2), (2021, 20514, 6.3),
                   (2022, 23159, 4.2), (2023, 24627, 7.3)],
            'GZ': [(2019, 16769, 8.3), (2020, 17827, 4.5), (2021, 19587, 8.1),
                   (2022, 20165, 1.2), (2023, 20913, 4.9)],
            'XJ': [(2019, 13597, 6.2), (2020, 13800, 3.4), (2021, 16000, 7.0),
                   (2022, 17741, 3.2), (2023, 19126, 6.8)],
            'TJ': [(2019, 14104, 4.8), (2020, 14084, 1.5), (2021, 15695, 6.6),
                   (2022, 16312, 1.0), (2023, 16737, 4.3)],
            'HL': [(2019, 13612, 4.2), (2020, 13699, 1.0), (2021, 14879, 6.1),
                   (2022, 15901, 2.7), (2023, 15884, 2.6)],
            'JL': [(2019, 11727, 3.0), (2020, 12311, 2.4), (2021, 13236, 6.6),
                   (2022, 13070, -1.9), (2023, 13531, 6.3)],
            'GS': [(2019, 8718, 6.2), (2020, 9017, 3.9), (2021, 10243, 6.9),
                   (2022, 11202, 4.5), (2023, 11863, 6.4)],
            'HI': [(2019, 5309, 5.8), (2020, 5532, 3.5), (2021, 6475, 11.2),
                   (2022, 6818, 0.2), (2023, 7551, 9.2)],
            'NX': [(2019, 3748, 6.5), (2020, 3921, 3.9), (2021, 4522, 6.7),
                   (2022, 5070, 4.0), (2023, 5315, 6.6)],
            'QH': [(2019, 2966, 6.3), (2020, 3005, 1.5), (2021, 3347, 5.7),
                   (2022, 3610, 2.3), (2023, 3799, 5.3)],
            'XZ': [(2019, 1698, 8.1), (2020, 1903, 7.8), (2021, 2080, 6.7),
                   (2022, 2133, 1.1), (2023, 2393, 9.5)]
        }

        # 插入GDP数据
        for province_code, data_list in gdp_data.items():
            for year, gdp, growth_rate in data_list:
                cursor.execute('''
                    INSERT OR REPLACE INTO gdp_data 
                    (province_code, year, gdp, gdp_growth_rate) 
                    VALUES (?, ?, ?, ?)
                ''', (province_code, year, gdp, growth_rate))

        conn.commit()
        conn.close()

    def get_all_provinces(self):
        """获取所有省份"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT code, name, region FROM provinces ORDER BY name')
        result = cursor.fetchall()
        conn.close()
        return result

    def get_gdp_by_year(self, year):
        """获取某年所有省份GDP数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.name, p.region, g.gdp, g.gdp_growth_rate 
            FROM gdp_data g 
            JOIN provinces p ON g.province_code = p.code 
            WHERE g.year = ? 
            ORDER BY g.gdp DESC
        ''', (year,))
        result = cursor.fetchall()
        conn.close()
        return result

    def get_gdp_by_province(self, province_code):
        """获取某省份历年GDP数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT year, gdp, gdp_growth_rate 
            FROM gdp_data 
            WHERE province_code = ? 
            ORDER BY year
        ''', (province_code,))
        result = cursor.fetchall()
        conn.close()
        return result

    def get_years(self):
        """获取所有年份"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT year FROM gdp_data ORDER BY year')
        result = [row[0] for row in cursor.fetchall()]
        conn.close()
        return result

    def get_region_data(self, year):
        """获取区域汇总数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.region, SUM(g.gdp) as total_gdp
            FROM gdp_data g 
            JOIN provinces p ON g.province_code = p.code 
            WHERE g.year = ?
            GROUP BY p.region
            ORDER BY total_gdp DESC
        ''', (year,))
        result = cursor.fetchall()
        conn.close()
        return result


class GDPVisualizationApp:
    """GDP数据可视化主应用类"""

    def __init__(self, root):
        self.root = root
        self.root.title("中国各省份GDP数据可视化系统")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)

        # 初始化数据库
        self.db = DatabaseManager()

        # 获取数据
        self.provinces = self.db.get_all_provinces()
        self.years = self.db.get_years()

        # 当前选中的图表类型
        self.current_chart = tk.StringVar(value="bar")
        self.selected_year = tk.IntVar(value=self.years[-1] if self.years else 2023)
        self.selected_province = tk.StringVar(value="GD")
        self.top_n = tk.IntVar(value=10)

        # 创建界面
        self.create_menu()
        self.create_main_layout()
        self.update_chart()

    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导出数据(CSV)", command=self.export_csv)
        file_menu.add_command(label="导出数据(JSON)", command=self.export_json)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)

    def create_main_layout(self):
        """创建主界面布局"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左侧控制面板
        self.create_control_panel(main_frame)

        # 右侧图表区域
        self.create_chart_panel(main_frame)

        # 底部数据表格
        self.create_data_table()

    def create_control_panel(self, parent):
        """创建控制面板"""
        control_frame = ttk.LabelFrame(parent, text="控制面板", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # 图表类型选择
        chart_frame = ttk.LabelFrame(control_frame, text="图表类型", padding=5)
        chart_frame.pack(fill=tk.X, pady=5)

        chart_types = [
            ("bar", "柱状图"),
            ("line", "折线图"),
            ("pie", "饼图"),
            ("region", "区域对比")
        ]
        for value, text in chart_types:
            ttk.Radiobutton(chart_frame, text=text, variable=self.current_chart,
                          value=value, command=self.update_chart).pack(anchor=tk.W, pady=2)

        # 年份选择
        year_frame = ttk.LabelFrame(control_frame, text="年份选择", padding=5)
        year_frame.pack(fill=tk.X, pady=5)

        year_combo = ttk.Combobox(year_frame, textvariable=self.selected_year,
                                  values=self.years, state="readonly", width=15)
        year_combo.pack(pady=5)
        year_combo.bind("<<ComboboxSelected>>", lambda e: self.update_chart())

        # 省份选择（用于折线图）
        province_frame = ttk.LabelFrame(control_frame, text="省份选择(折线图)", padding=5)
        province_frame.pack(fill=tk.X, pady=5)

        province_names = {p[0]: p[1] for p in self.provinces}
        province_combo = ttk.Combobox(province_frame, textvariable=self.selected_province,
                                      values=[f"{p[0]} - {p[1]}" for p in self.provinces],
                                      state="readonly", width=15)
        province_combo.pack(pady=5)
        province_combo.bind("<<ComboboxSelected>>", lambda e: self.on_province_select(province_names))

        # Top N 选择
        topn_frame = ttk.LabelFrame(control_frame, text="显示数量", padding=5)
        topn_frame.pack(fill=tk.X, pady=5)

        ttk.Scale(topn_frame, from_=5, to=31, variable=self.top_n,
                 orient=tk.HORIZONTAL, command=lambda x: self.update_chart()).pack(fill=tk.X, pady=5)
        ttk.Label(topn_frame, textvariable=self.top_n).pack()

        # 统计信息
        self.stats_frame = ttk.LabelFrame(control_frame, text="统计信息", padding=5)
        self.stats_frame.pack(fill=tk.X, pady=5)

        self.total_gdp_label = ttk.Label(self.stats_frame, text="全国GDP: ")
        self.total_gdp_label.pack(anchor=tk.W, pady=2)

        self.avg_growth_label = ttk.Label(self.stats_frame, text="平均增速: ")
        self.avg_growth_label.pack(anchor=tk.W, pady=2)

        self.top_province_label = ttk.Label(self.stats_frame, text="最高省份: ")
        self.top_province_label.pack(anchor=tk.W, pady=2)

        # 操作按钮
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="刷新数据", command=self.update_chart).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="保存图表", command=self.save_chart).pack(fill=tk.X, pady=2)

    def create_chart_panel(self, parent):
        """创建图表显示区域"""
        chart_frame = ttk.LabelFrame(parent, text="数据可视化", padding=5)
        chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Matplotlib图形
        self.fig = Figure(figsize=(10, 7), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.draw()

        # 添加工具栏
        toolbar = NavigationToolbar2Tk(self.canvas, chart_frame)
        toolbar.update()

        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar.pack(fill=tk.X)

    def create_data_table(self):
        """创建数据表格"""
        table_frame = ttk.LabelFrame(self.root, text="数据详情", padding=5)
        table_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)

        # 创建树形表格
        columns = ("排名", "省份", "地区", "GDP(亿元)", "增速(%)")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.CENTER)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def on_province_select(self, province_names):
        """处理省份选择"""
        selected = self.selected_province.get()
        if " - " in selected:
            self.selected_province.set(selected.split(" - ")[0])
        self.update_chart()

    def update_chart(self):
        """更新图表"""
        chart_type = self.current_chart.get()
        year = self.selected_year.get()

        self.ax.clear()

        if chart_type == "bar":
            self.draw_bar_chart(year)
        elif chart_type == "line":
            self.draw_line_chart()
        elif chart_type == "pie":
            self.draw_pie_chart(year)
        elif chart_type == "region":
            self.draw_region_chart(year)

        self.fig.tight_layout()
        self.canvas.draw()
        self.update_table(year)
        self.update_stats(year)

    def draw_bar_chart(self, year):
        """绘制柱状图"""
        data = self.db.get_gdp_by_year(year)[:self.top_n.get()]

        provinces = [d[0] for d in data]
        gdp_values = [d[2] for d in data]
        colors = plt.cm.viridis(np.linspace(0, 1, len(provinces)))

        bars = self.ax.barh(provinces[::-1], gdp_values[::-1], color=colors[::-1])
        self.ax.set_xlabel("GDP (亿元)", fontsize=11)
        self.ax.set_title(f"{year}年中国各省份GDP排名 (TOP {self.top_n.get()})", fontsize=13)

        # 添加数值标签
        for bar, value in zip(bars, gdp_values[::-1]):
            self.ax.text(value + 1000, bar.get_y() + bar.get_height()/2,
                        f'{value:,.0f}', va='center', fontsize=9)

        self.ax.set_xlim(0, max(gdp_values) * 1.15)

    def draw_line_chart(self):
        """绘制折线图"""
        province_code = self.selected_province.get()
        province_name = next((p[1] for p in self.provinces if p[0] == province_code), "")

        data = self.db.get_gdp_by_province(province_code)
        years = [d[0] for d in data]
        gdp_values = [d[1] for d in data]

        self.ax.plot(years, gdp_values, marker='o', linewidth=2, markersize=8,
                    label=f'{province_name} GDP趋势')
        self.ax.fill_between(years, gdp_values, alpha=0.3)

        # 添加数值标签
        for year, gdp in zip(years, gdp_values):
            self.ax.annotate(f'{gdp:,.0f}', xy=(year, gdp),
                           xytext=(0, 10), textcoords='offset points',
                           ha='center', fontsize=9)

        self.ax.set_xlabel("年份", fontsize=11)
        self.ax.set_ylabel("GDP (亿元)", fontsize=11)
        self.ax.set_title(f"{province_name}历年GDP变化趋势", fontsize=13)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.legend()

    def draw_pie_chart(self, year):
        """绘制饼图"""
        data = self.db.get_gdp_by_year(year)[:self.top_n.get()]

        provinces = [d[0] for d in data]
        gdp_values = [d[2] for d in data]

        colors = plt.cm.Set3(np.linspace(0, 1, len(provinces)))

        wedges, texts, autotexts = self.ax.pie(gdp_values, labels=provinces, autopct='%1.1f%%',
                                               colors=colors, startangle=90)
        self.ax.set_title(f"{year}年GDP占比分布 (TOP {self.top_n.get()})", fontsize=13)

    def draw_region_chart(self, year):
        """绘制区域对比图"""
        data = self.db.get_region_data(year)

        regions = [d[0] for d in data]
        gdp_values = [d[1] for d in data]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']

        bars = self.ax.bar(regions, gdp_values, color=colors[:len(regions)])
        self.ax.set_ylabel("GDP (亿元)", fontsize=11)
        self.ax.set_title(f"{year}年各大区域GDP对比", fontsize=13)

        # 添加数值标签
        for bar, value in zip(bars, gdp_values):
            self.ax.text(bar.get_x() + bar.get_width()/2, value + 1000,
                        f'{value:,.0f}', ha='center', fontsize=10)

        self.ax.set_ylim(0, max(gdp_values) * 1.15)

    def update_table(self, year):
        """更新数据表格"""
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 获取数据
        data = self.db.get_gdp_by_year(year)

        # 插入数据
        for i, (name, region, gdp, growth) in enumerate(data, 1):
            growth_str = f"{growth:.1f}%" if growth else "N/A"
            self.tree.insert("", tk.END, values=(i, name, region, f"{gdp:,.0f}", growth_str))

    def update_stats(self, year):
        """更新统计信息"""
        data = self.db.get_gdp_by_year(year)

        if data:
            total_gdp = sum(d[2] for d in data)
            avg_growth = sum(d[3] for d in data if d[3]) / len([d for d in data if d[3]])
            top_province = data[0][0]

            self.total_gdp_label.config(text=f"全国GDP: {total_gdp:,.0f} 亿元")
            self.avg_growth_label.config(text=f"平均增速: {avg_growth:.1f}%")
            self.top_province_label.config(text=f"最高省份: {top_province}")

    def export_csv(self):
        """导出CSV文件"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            try:
                year = self.selected_year.get()
                data = self.db.get_gdp_by_year(year)

                with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(["排名", "省份", "地区", "GDP(亿元)", "增速(%)"])
                    for i, (name, region, gdp, growth) in enumerate(data, 1):
                        writer.writerow([i, name, region, gdp, growth])

                messagebox.showinfo("成功", f"数据已导出到:\n{file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败:\n{str(e)}")

    def export_json(self):
        """导出JSON文件"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                year = self.selected_year.get()
                data = self.db.get_gdp_by_year(year)

                export_data = {
                    "year": year,
                    "export_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "data": [
                        {
                            "rank": i,
                            "province": name,
                            "region": region,
                            "gdp": gdp,
                            "growth_rate": growth
                        }
                        for i, (name, region, gdp, growth) in enumerate(data, 1)
                    ]
                }

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)

                messagebox.showinfo("成功", f"数据已导出到:\n{file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败:\n{str(e)}")

    def save_chart(self):
        """保存图表"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"),
                      ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo("成功", f"图表已保存到:\n{file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败:\n{str(e)}")

    def show_help(self):
        """显示帮助信息"""
        help_text = """
中国各省份GDP数据可视化系统 - 使用说明

功能概述：
1. 柱状图：展示指定年份各省份GDP排名
2. 折线图：展示选定省份历年GDP变化趋势
3. 饼图：展示GDP占比分布
4. 区域对比：展示各大区域GDP对比

操作说明：
- 使用左侧控制面板切换图表类型
- 选择年份查看不同年度的数据
- 选择省份查看特定省份的趋势
- 可调节显示数量（Top N）
- 支持导出数据和保存图表

数据来源：国家统计局公开数据
        """
        messagebox.showinfo("使用说明", help_text)

    def show_about(self):
        """显示关于信息"""
        about_text = """
中国各省份GDP数据可视化系统
版本: 1.0

基于Python的大数据可视化实践
技术栈: Tkinter + Matplotlib + SQLite3

作者: 徐嘉泽
学校: 中国矿业大学
日期: 2026年3月
        """
        messagebox.showinfo("关于", about_text)


def main():
    """主函数"""
    root = tk.Tk()
    app = GDPVisualizationApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
