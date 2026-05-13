"""
图书馆大数据可视化系统 - 数据库初始化模块
功能：创建SQLite数据库、初始化表结构、插入模拟数据
"""
import sqlite3
import random
from datetime import datetime, timedelta


def init_database():
    """初始化数据库并插入模拟数据"""
    conn = sqlite3.connect('lib.db')
    cursor = conn.cursor()

    print("[1/8] 正在创建数据表...")

    # 1. 馆藏统计表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collection_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category VARCHAR(50) NOT NULL,
            total_books INTEGER DEFAULT 0,
            available_books INTEGER DEFAULT 0,
            borrowed_books INTEGER DEFAULT 0,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. 出入馆记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entry_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_date DATE NOT NULL,
            hour INTEGER NOT NULL,
            entry_count INTEGER DEFAULT 0,
            exit_count INTEGER DEFAULT 0
        )
    ''')

    # 3. 图书分类表（中图法）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS book_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_code VARCHAR(10) NOT NULL,
            category_name VARCHAR(100) NOT NULL,
            book_count INTEGER DEFAULT 0,
            borrow_count INTEGER DEFAULT 0
        )
    ''')

    # 4. 借阅趋势表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS borrow_trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_date DATE NOT NULL,
            borrow_count INTEGER DEFAULT 0,
            return_count INTEGER DEFAULT 0
        )
    ''')

    # 5. 热门图书表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hot_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_name VARCHAR(200) NOT NULL,
            author VARCHAR(100),
            category VARCHAR(50),
            borrow_times INTEGER DEFAULT 0
        )
    ''')

    # 6. 读者统计表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reader_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reader_type VARCHAR(50) NOT NULL,
            count INTEGER DEFAULT 0
        )
    ''')

    # 7. 实时数据表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS realtime_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            current_visitors INTEGER DEFAULT 0,
            today_borrow INTEGER DEFAULT 0,
            today_return INTEGER DEFAULT 0,
            today_new_readers INTEGER DEFAULT 0,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 清空现有数据
    print("[2/8] 清空历史数据...")
    tables = ['collection_stats', 'entry_records', 'book_categories',
              'borrow_trends', 'hot_books', 'reader_stats', 'realtime_data']
    for table in tables:
        cursor.execute(f'DELETE FROM {table}')

    # 插入馆藏统计数据
    print("[3/8] 插入馆藏统计数据...")
    collections = [
        ('中文图书', 285000, 256500, 28500),
        ('外文图书', 65000, 61750, 3250),
        ('期刊杂志', 45000, 43200, 1800),
        ('电子资源', 120000, 120000, 0),
        ('学位论文', 35000, 33250, 1750),
        ('多媒体资源', 15000, 14250, 750)
    ]
    cursor.executemany('''
        INSERT INTO collection_stats (category, total_books, available_books, borrowed_books)
        VALUES (?, ?, ?, ?)
    ''', collections)

    # 插入出入馆记录（今日每小时数据）
    print("[4/8] 插入出入馆记录...")
    today = datetime.now().strftime('%Y-%m-%d')
    current_hour = datetime.now().hour
    for hour in range(8, 23):
        if hour <= current_hour:
            entry = random.randint(80, 400)
            exit_count = random.randint(50, 320)
        else:
            entry = 0
            exit_count = 0
        cursor.execute('''
            INSERT INTO entry_records (record_date, hour, entry_count, exit_count)
            VALUES (?, ?, ?, ?)
        ''', (today, hour, entry, exit_count))

    # 插入图书分类数据（中图法22大类）
    print("[5/8] 插入图书分类数据（中图法）...")
    categories = [
        ('A', '马克思主义', 8500, 1200),
        ('B', '哲学、宗教', 15600, 2800),
        ('C', '社会科学总论', 12300, 1900),
        ('D', '政治、法律', 18900, 3200),
        ('E', '军事', 5600, 800),
        ('F', '经济', 35600, 6500),
        ('G', '文化、教育', 28900, 5200),
        ('H', '语言、文字', 22300, 4100),
        ('I', '文学', 45600, 8900),
        ('J', '艺术', 16800, 3100),
        ('K', '历史、地理', 19500, 3600),
        ('N', '自然科学总论', 8900, 1500),
        ('O', '数理科学', 25600, 4800),
        ('P', '天文、地球科学', 9800, 1600),
        ('Q', '生物科学', 12300, 2200),
        ('R', '医药、卫生', 18600, 3400),
        ('S', '农业科学', 11200, 1800),
        ('T', '工业技术', 68900, 12500),
        ('U', '交通运输', 8900, 1400),
        ('V', '航空、航天', 6500, 1100),
        ('X', '环境科学', 7800, 1300),
        ('Z', '综合性图书', 9600, 1500)
    ]
    cursor.executemany('''
        INSERT INTO book_categories (category_code, category_name, book_count, borrow_count)
        VALUES (?, ?, ?, ?)
    ''', categories)

    # 插入借阅趋势数据（最近30天）
    print("[6/8] 插入借阅趋势数据...")
    for i in range(30, 0, -1):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        borrow = random.randint(200, 500)
        return_count = random.randint(180, 480)
        cursor.execute('''
            INSERT INTO borrow_trends (record_date, borrow_count, return_count)
            VALUES (?, ?, ?)
        ''', (date, borrow, return_count))

    # 插入热门图书数据
    print("[7/8] 插入热门图书数据...")
    hot_books = [
        ('Python编程：从入门到实践', '埃里克·马瑟斯', '计算机', 256),
        ('活着', '余华', '文学', 234),
        ('三体', '刘慈欣', '科幻', 228),
        ('经济学原理', '曼昆', '经济', 215),
        ('人类简史', '尤瓦尔·赫拉利', '历史', 198),
        ('深度学习', 'Ian Goodfellow', '计算机', 187),
        ('百年孤独', '加西亚·马尔克斯', '文学', 176),
        ('数据结构与算法', '严蔚敏', '计算机', 168),
        ('心理学与生活', '理查德·格里格', '心理学', 156),
        ('机器学习', '周志华', '计算机', 145)
    ]
    cursor.executemany('''
        INSERT INTO hot_books (book_name, author, category, borrow_times)
        VALUES (?, ?, ?, ?)
    ''', hot_books)

    # 插入读者统计数据
    print("[8/8] 插入读者统计数据...")
    readers = [
        ('本科生', 25680),
        ('研究生', 8960),
        ('博士生', 2350),
        ('教职工', 3680),
        ('校外读者', 1250)
    ]
    cursor.executemany('''
        INSERT INTO reader_stats (reader_type, count)
        VALUES (?, ?)
    ''', readers)

    # 插入初始实时数据
    cursor.execute('''
        INSERT INTO realtime_data (current_visitors, today_borrow, today_return, today_new_readers)
        VALUES (?, ?, ?, ?)
    ''', (random.randint(500, 1200), random.randint(200, 400),
          random.randint(180, 380), random.randint(10, 50)))

    conn.commit()
    conn.close()

    print("\n" + "=" * 45)
    print("数据库初始化完成！")
    print("数据库文件: lib.db")
    print("数据表: 7个")
    print("模拟数据: 已生成")
    print("=" * 45)


if __name__ == '__main__':
    init_database()
