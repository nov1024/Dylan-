from flask import Flask, render_template, jsonify
import sqlite3
import random
from datetime import datetime, timedelta

app = Flask(__name__)

# ============================================
# 数据库连接管理
# ============================================
def get_db_connection():
    """获取SQLite数据库连接"""
    conn = sqlite3.connect('lib.db')
    conn.row_factory = sqlite3.Row
    return conn


# ============================================
# 页面路由
# ============================================
@app.route('/')
def index():
    """渲染数据可视化大屏主页面"""
    return render_template('index.html')


# ============================================
# API接口 - 馆藏统计数据
# ============================================
@app.route('/api/collection_stats')
def get_collection_stats():
    """获取馆藏资源统计数据（中文图书、外文图书、期刊等）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT category, total_books, available_books, borrowed_books 
        FROM collection_stats 
        ORDER BY total_books DESC
    ''')
    rows = cursor.fetchall()
    conn.close()

    data = {
        'categories': [row['category'] for row in rows],
        'total': [row['total_books'] for row in rows],
        'available': [row['available_books'] for row in rows],
        'borrowed': [row['borrowed_books'] for row in rows],
        'total_collection': sum(row['total_books'] for row in rows)
    }
    return jsonify(data)


# ============================================
# API接口 - 出入馆记录
# ============================================
@app.route('/api/entry_records')
def get_entry_records():
    """获取今日每小时出入馆流量数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT hour, entry_count, exit_count 
        FROM entry_records 
        WHERE record_date = ?
        ORDER BY hour
    ''', (today,))
    rows = cursor.fetchall()
    conn.close()

    data = {
        'hours': [f"{row['hour']:02d}:00" for row in rows],
        'entry': [row['entry_count'] for row in rows],
        'exit': [row['exit_count'] for row in rows],
        'total_entry': sum(row['entry_count'] for row in rows),
        'total_exit': sum(row['exit_count'] for row in rows)
    }
    return jsonify(data)


# ============================================
# API接口 - 图书分类数据
# ============================================
@app.route('/api/book_categories')
def get_book_categories():
    """获取中图法分类统计数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT category_code, category_name, book_count, borrow_count 
        FROM book_categories
        ORDER BY book_count DESC
    ''')
    rows = cursor.fetchall()
    conn.close()

    data = {
        'categories': [f"{row['category_code']}-{row['category_name']}" for row in rows],
        'book_counts': [row['book_count'] for row in rows],
        'borrow_counts': [row['borrow_count'] for row in rows],
        'pie_data': [
            {'name': row['category_name'], 'value': row['book_count']}
            for row in rows[:10]
        ]
    }
    return jsonify(data)


# ============================================
# API接口 - 借阅趋势
# ============================================
@app.route('/api/borrow_trends')
def get_borrow_trends():
    """获取近30天借阅/归还趋势数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT record_date, borrow_count, return_count 
        FROM borrow_trends
        ORDER BY record_date DESC
        LIMIT 30
    ''')
    rows = cursor.fetchall()
    conn.close()

    # 反转数据使其按日期升序排列
    rows = list(reversed(rows))

    data = {
        'dates': [row['record_date'][5:] for row in rows],
        'borrow': [row['borrow_count'] for row in rows],
        'return': [row['return_count'] for row in rows]
    }
    return jsonify(data)


# ============================================
# API接口 - 热门图书
# ============================================
@app.route('/api/hot_books')
def get_hot_books():
    """获取热门图书TOP10排行"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT book_name, author, category, borrow_times 
        FROM hot_books
        ORDER BY borrow_times DESC
        LIMIT 10
    ''')
    rows = cursor.fetchall()
    conn.close()

    data = [{
        'rank': idx + 1,
        'name': row['book_name'],
        'author': row['author'],
        'category': row['category'],
        'times': row['borrow_times']
    } for idx, row in enumerate(rows)]
    return jsonify(data)


# ============================================
# API接口 - 读者统计
# ============================================
@app.route('/api/reader_stats')
def get_reader_stats():
    """获取读者构成统计数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT reader_type, count FROM reader_stats ORDER BY count DESC')
    rows = cursor.fetchall()
    conn.close()

    data = [{'name': row['reader_type'], 'value': row['count']} for row in rows]
    return jsonify(data)


# ============================================
# API接口 - 实时数据（动态模拟）
# ============================================
@app.route('/api/realtime_data')
def get_realtime_data():
    """获取实时数据并模拟动态变化效果"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM realtime_data ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()

    # 模拟实时数据变化
    current_visitors = row['current_visitors'] + random.randint(-25, 35)
    current_visitors = max(80, min(1600, current_visitors))

    today_borrow = row['today_borrow'] + random.randint(0, 6)
    today_return = row['today_return'] + random.randint(0, 5)
    today_new = row['today_new_readers'] + random.randint(0, 2)

    # 更新数据库
    cursor.execute('''
        UPDATE realtime_data 
        SET current_visitors = ?, today_borrow = ?, today_return = ?, 
            today_new_readers = ?, update_time = ?
        WHERE id = ?
    ''', (current_visitors, today_borrow, today_return, today_new,
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'), row['id']))
    conn.commit()
    conn.close()

    data = {
        'current_visitors': current_visitors,
        'today_borrow': today_borrow,
        'today_return': today_return,
        'today_new_readers': today_new,
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    return jsonify(data)


# ============================================
# API接口 - 更新出入馆数据（模拟）
# ============================================
@app.route('/api/update_entry')
def update_entry():
    """模拟当前小时出入馆人数变化"""
    conn = get_db_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    current_hour = datetime.now().hour

    if 8 <= current_hour <= 22:
        cursor.execute('''
            UPDATE entry_records 
            SET entry_count = entry_count + ?, exit_count = exit_count + ?
            WHERE record_date = ? AND hour = ?
        ''', (random.randint(1, 12), random.randint(1, 10), today, current_hour))
        conn.commit()

    conn.close()
    return jsonify({'status': 'success', 'message': 'Entry data updated'})


# ============================================
# API接口 - 获取系统状态
# ============================================
@app.route('/api/system_status')
def get_system_status():
    """获取系统运行状态信息"""
    data = {
        'status': 'running',
        'uptime': '99.9%',
        'api_version': 'v2.0',
        'database': 'SQLite3',
        'last_backup': (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
        'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    return jsonify(data)


# ============================================
# 应用入口
# ============================================
if __name__ == '__main__':
    print("=" * 50)
    print("图书馆大数据可视化系统启动中...")
    print("数据库: SQLite3 (lib.db)")
    print("前端框架: ECharts 5.4 + 原生JS")
    print("访问地址: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
