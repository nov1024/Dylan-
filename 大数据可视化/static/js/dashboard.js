/**
 * 图书馆大数据可视化大屏 - 前端交互脚本
 * 功能：ECharts图表渲染、粒子背景、实时数据更新、数字动画
 */

// ============================================
// 全局变量
// ============================================
let collectionChart, categoryPieChart, readerChart;
let entryChart, trendChart;
let categoryBarChart, borrowCategoryChart;

// ECharts配色方案
const colorPalette = [
    '#00d4ff', '#00ff88', '#ffaa00', '#ff6b6b', '#a855f7',
    '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
    '#0ea5e9', '#22c55e', '#eab308', '#f97316', '#ec4899'
];

// 图表通用主题配置
const chartTheme = {
    backgroundColor: 'transparent',
    textStyle: { fontFamily: 'Microsoft YaHei, PingFang SC, sans-serif' }
};

// ============================================
// 粒子背景系统
// ============================================
class ParticleSystem {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.connections = [];
        this.mouse = { x: null, y: null };
        this.init();
    }

    init() {
        this.resize();
        window.addEventListener('resize', () => this.resize());
        document.addEventListener('mousemove', (e) => {
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
        });
        this.createParticles();
        this.animate();
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    createParticles() {
        const count = Math.floor((this.canvas.width * this.canvas.height) / 12000);
        this.particles = [];
        for (let i = 0; i < count; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                radius: Math.random() * 2 + 0.5,
                opacity: Math.random() * 0.5 + 0.1
            });
        }
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // 更新和绘制粒子
        this.particles.forEach(p => {
            p.x += p.vx;
            p.y += p.vy;

            if (p.x < 0 || p.x > this.canvas.width) p.vx *= -1;
            if (p.y < 0 || p.y > this.canvas.height) p.vy *= -1;

            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            this.ctx.fillStyle = `rgba(0, 212, 255, ${p.opacity})`;
            this.ctx.fill();
        });

        // 绘制连线
        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const dx = this.particles[i].x - this.particles[j].x;
                const dy = this.particles[i].y - this.particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 120) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
                    this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
                    this.ctx.strokeStyle = `rgba(0, 212, 255, ${0.15 * (1 - dist / 120)})`;
                    this.ctx.lineWidth = 0.5;
                    this.ctx.stroke();
                }
            }
        }

        requestAnimationFrame(() => this.animate());
    }
}

// ============================================
// 初始化入口
// ============================================
$(document).ready(function() {
    // 启动粒子背景
    new ParticleSystem('particleCanvas');

    // 初始化图表
    initCharts();

    // 更新时间
    updateDateTime();

    // 加载所有数据
    loadAllData();

    // 定时刷新
    setInterval(updateDateTime, 1000);
    setInterval(loadRealtimeData, 5000);
    setInterval(loadEntryRecords, 30000);
    setInterval(loadAllData, 60000);
});

// ============================================
// 日期时间更新
// ============================================
function updateDateTime() {
    const now = new Date();
    const dateStr = now.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        weekday: 'long'
    });
    const timeStr = now.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
    $('#currentDate').text(dateStr);
    $('#currentTime').text(timeStr);
}

// ============================================
// 初始化所有ECharts图表
// ============================================
function initCharts() {
    collectionChart = echarts.init(document.getElementById('collectionChart'));
    categoryPieChart = echarts.init(document.getElementById('categoryPieChart'));
    readerChart = echarts.init(document.getElementById('readerChart'));
    entryChart = echarts.init(document.getElementById('entryChart'));
    trendChart = echarts.init(document.getElementById('trendChart'));
    categoryBarChart = echarts.init(document.getElementById('categoryBarChart'));
    borrowCategoryChart = echarts.init(document.getElementById('borrowCategoryChart'));

    // 响应式重绘
    window.addEventListener('resize', function() {
        collectionChart && collectionChart.resize();
        categoryPieChart && categoryPieChart.resize();
        readerChart && readerChart.resize();
        entryChart && entryChart.resize();
        trendChart && trendChart.resize();
        categoryBarChart && categoryBarChart.resize();
        borrowCategoryChart && borrowCategoryChart.resize();
    });
}

// ============================================
// 加载所有数据
// ============================================
function loadAllData() {
    loadCollectionStats();
    loadEntryRecords();
    loadBookCategories();
    loadBorrowTrends();
    loadHotBooks();
    loadReaderStats();
    loadRealtimeData();
}

// ============================================
// 馆藏统计数据
// ============================================
function loadCollectionStats() {
    $.ajax({
        url: '/api/collection_stats',
        method: 'GET',
        success: function(data) {
            $('#totalCollection').text(formatNumber(data.total_collection));

            const option = {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: { type: 'shadow' },
                    backgroundColor: 'rgba(0,0,0,0.85)',
                    borderColor: '#00d4ff',
                    borderWidth: 1,
                    textStyle: { color: '#fff', fontSize: 12 }
                },
                legend: {
                    data: ['总量', '可借', '已借'],
                    textStyle: { color: 'rgba(0,212,255,0.8)', fontSize: 11 },
                    top: 5,
                    itemWidth: 18,
                    itemHeight: 10
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    top: '18%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    data: data.categories,
                    axisLine: { lineStyle: { color: 'rgba(0,212,255,0.4)' } },
                    axisLabel: {
                        color: 'rgba(0,212,255,0.7)',
                        fontSize: 10,
                        rotate: 25
                    },
                    axisTick: { lineStyle: { color: 'rgba(0,212,255,0.2)' } }
                },
                yAxis: {
                    type: 'value',
                    axisLine: { lineStyle: { color: 'rgba(0,212,255,0.4)' } },
                    axisLabel: { color: 'rgba(0,212,255,0.7)', fontSize: 10 },
                    splitLine: { lineStyle: { color: 'rgba(0,212,255,0.08)' } }
                },
                series: [
                    {
                        name: '总量',
                        type: 'bar',
                        data: data.total,
                        itemStyle: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                { offset: 0, color: '#00d4ff' },
                                { offset: 1, color: '#0066aa' }
                            ]),
                            borderRadius: [4, 4, 0, 0]
                        },
                        barWidth: '25%'
                    },
                    {
                        name: '可借',
                        type: 'bar',
                        data: data.available,
                        itemStyle: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                { offset: 0, color: '#00ff88' },
                                { offset: 1, color: '#008844' }
                            ]),
                            borderRadius: [4, 4, 0, 0]
                        },
                        barWidth: '25%'
                    },
                    {
                        name: '已借',
                        type: 'bar',
                        data: data.borrowed,
                        itemStyle: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                { offset: 0, color: '#ffaa00' },
                                { offset: 1, color: '#cc6600' }
                            ]),
                            borderRadius: [4, 4, 0, 0]
                        },
                        barWidth: '25%'
                    }
                ]
            };
            collectionChart.setOption(option);
        }
    });
}

// ============================================
// 出入馆记录
// ============================================
function loadEntryRecords() {
    $.ajax({
        url: '/api/entry_records',
        method: 'GET',
        success: function(data) {
            $('#entryInfo').text(`入馆: ${formatNumber(data.total_entry)} | 出馆: ${formatNumber(data.total_exit)}`);

            const option = {
                tooltip: {
                    trigger: 'axis',
                    backgroundColor: 'rgba(0,0,0,0.85)',
                    borderColor: '#00d4ff',
                    borderWidth: 1,
                    textStyle: { color: '#fff' }
                },
                legend: {
                    data: ['入馆人数', '出馆人数'],
                    textStyle: { color: 'rgba(0,212,255,0.8)' },
                    top: 5
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    top: '15%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    boundaryGap: false,
                    data: data.hours,
                    axisLine: { lineStyle: { color: 'rgba(0,212,255,0.4)' } },
                    axisLabel: { color: 'rgba(0,212,255,0.7)', fontSize: 11 }
                },
                yAxis: {
                    type: 'value',
                    axisLine: { lineStyle: { color: 'rgba(0,212,255,0.4)' } },
                    axisLabel: { color: 'rgba(0,212,255,0.7)' },
                    splitLine: { lineStyle: { color: 'rgba(0,212,255,0.08)' } }
                },
                series: [
                    {
                        name: '入馆人数',
                        type: 'line',
                        smooth: true,
                        symbol: 'circle',
                        symbolSize: 8,
                        data: data.entry,
                        lineStyle: { color: '#00ff88', width: 3 },
                        areaStyle: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                { offset: 0, color: 'rgba(0,255,136,0.35)' },
                                { offset: 1, color: 'rgba(0,255,136,0.02)' }
                            ])
                        },
                        itemStyle: { color: '#00ff88', borderWidth: 2, borderColor: '#fff' }
                    },
                    {
                        name: '出馆人数',
                        type: 'line',
                        smooth: true,
                        symbol: 'circle',
                        symbolSize: 8,
                        data: data.exit,
                        lineStyle: { color: '#ff6b6b', width: 3 },
                        areaStyle: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                { offset: 0, color: 'rgba(255,107,107,0.35)' },
                                { offset: 1, color: 'rgba(255,107,107,0.02)' }
                            ])
                        },
                        itemStyle: { color: '#ff6b6b', borderWidth: 2, borderColor: '#fff' }
                    }
                ]
            };
            entryChart.setOption(option);
        }
    });
}

// ============================================
// 图书分类数据
// ============================================
function loadBookCategories() {
    $.ajax({
        url: '/api/book_categories',
        method: 'GET',
        success: function(data) {
            // 饼图
            const pieOption = {
                tooltip: {
                    trigger: 'item',
                    formatter: '{b}: {c}册 ({d}%)',
                    backgroundColor: 'rgba(0,0,0,0.85)',
                    borderColor: '#00d4ff',
                    borderWidth: 1,
                    textStyle: { color: '#fff' }
                },
                series: [{
                    type: 'pie',
                    radius: ['38%', '68%'],
                    center: ['50%', '55%'],
                    avoidLabelOverlap: true,
                    padAngle: 3,
                    itemStyle: {
                        borderRadius: 6,
                        borderColor: '#0a1a4a',
                        borderWidth: 2
                    },
                    label: {
                        show: true,
                        position: 'outside',
                        color: 'rgba(0,212,255,0.8)',
                        fontSize: 10,
                        formatter: '{b}\n{d}%'
                    },
                    labelLine: {
                        lineStyle: { color: 'rgba(0,212,255,0.4)' },
                        length: 12,
                        length2: 8
                    },
                    emphasis: {
                        label: { fontSize: 13, fontWeight: 'bold' },
                        itemStyle: {
                            shadowBlur: 20,
                            shadowColor: 'rgba(0,212,255,0.4)'
                        }
                    },
                    data: data.pie_data,
                    color: colorPalette
                }]
            };
            categoryPieChart.setOption(pieOption);

            // 横向柱状图（TOP10）
            const top10 = {
                categories: data.categories.slice(0, 10).reverse(),
                counts: data.book_counts.slice(0, 10).reverse()
            };

            const barOption = {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: { type: 'shadow' },
                    backgroundColor: 'rgba(0,0,0,0.85)',
                    borderColor: '#00d4ff',
                    borderWidth: 1,
                    textStyle: { color: '#fff' }
                },
                grid: {
                    left: '3%',
                    right: '10%',
                    bottom: '3%',
                    top: '3%',
                    containLabel: true
                },
                xAxis: {
                    type: 'value',
                    axisLine: { lineStyle: { color: 'rgba(0,212,255,0.4)' } },
                    axisLabel: { color: 'rgba(0,212,255,0.7)', fontSize: 10 },
                    splitLine: { lineStyle: { color: 'rgba(0,212,255,0.08)' } }
                },
                yAxis: {
                    type: 'category',
                    data: top10.categories,
                    axisLine: { lineStyle: { color: 'rgba(0,212,255,0.4)' } },
                    axisLabel: {
                        color: 'rgba(0,212,255,0.7)',
                        fontSize: 10,
                        width: 90,
                        overflow: 'truncate'
                    }
                },
                series: [{
                    type: 'bar',
                    data: top10.counts,
                    itemStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                            { offset: 0, color: '#00a8e8' },
                            { offset: 1, color: '#00ff88' }
                        ]),
                        borderRadius: [0, 6, 6, 0]
                    },
                    label: {
                        show: true,
                        position: 'right',
                        color: '#00d4ff',
                        fontSize: 10,
                        formatter: '{c}'
                    },
                    barWidth: '55%'
                }]
            };
            categoryBarChart.setOption(barOption);

            // 借阅分类统计
            const borrowOption = {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: { type: 'shadow' },
                    backgroundColor: 'rgba(0,0,0,0.85)',
                    borderColor: '#00d4ff',
                    borderWidth: 1,
                    textStyle: { color: '#fff' }
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    top: '3%',
                    containLabel: true
                },
                xAxis: {
                    type: 'value',
                    axisLine: { lineStyle: { color: 'rgba(0,212,255,0.4)' } },
                    axisLabel: { color: 'rgba(0,212,255,0.7)', fontSize: 10 },
                    splitLine: { lineStyle: { color: 'rgba(0,212,255,0.08)' } }
                },
                yAxis: {
                    type: 'category',
                    data: data.categories.slice(0, 8).reverse(),
                    axisLine: { lineStyle: { color: 'rgba(0,212,255,0.4)' } },
                    axisLabel: {
                        color: 'rgba(0,212,255,0.7)',
                        fontSize: 9,
                        width: 75,
                        overflow: 'truncate'
                    }
                },
                series: [{
                    type: 'bar',
                    data: data.borrow_counts.slice(0, 8).reverse(),
                    itemStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                            { offset: 0, color: '#ff6b6b' },
                            { offset: 1, color: '#ffaa00' }
                        ]),
                        borderRadius: [0, 6, 6, 0]
                    },
                    barWidth: '55%'
                }]
            };
            borrowCategoryChart.setOption(borrowOption);
        }
    });
}

// ============================================
// 借阅趋势
// ============================================
function loadBorrowTrends() {
    $.ajax({
        url: '/api/borrow_trends',
        method: 'GET',
        success: function(data) {
            const option = {
                tooltip: {
                    trigger: 'axis',
                    backgroundColor: 'rgba(0,0,0,0.85)',
                    borderColor: '#00d4ff',
                    borderWidth: 1,
                    textStyle: { color: '#fff' }
                },
                legend: {
                    data: ['借阅量', '归还量'],
                    textStyle: { color: 'rgba(0,212,255,0.8)' },
                    top: 5
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    top: '15%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    boundaryGap: false,
                    data: data.dates,
                    axisLine: { lineStyle: { color: 'rgba(0,212,255,0.4)' } },
                    axisLabel: {
                        color: 'rgba(0,212,255,0.7)',
                        fontSize: 10,
                        rotate: 45
                    }
                },
                yAxis: {
                    type: 'value',
                    axisLine: { lineStyle: { color: 'rgba(0,212,255,0.4)' } },
                    axisLabel: { color: 'rgba(0,212,255,0.7)' },
                    splitLine: { lineStyle: { color: 'rgba(0,212,255,0.08)' } }
                },
                series: [
                    {
                        name: '借阅量',
                        type: 'line',
                        smooth: true,
                        symbol: 'circle',
                        symbolSize: 6,
                        data: data.borrow,
                        lineStyle: { color: '#a855f7', width: 2.5 },
                        areaStyle: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                { offset: 0, color: 'rgba(168,85,247,0.35)' },
                                { offset: 1, color: 'rgba(168,85,247,0.02)' }
                            ])
                        },
                        itemStyle: { color: '#a855f7', borderWidth: 2, borderColor: '#fff' }
                    },
                    {
                        name: '归还量',
                        type: 'line',
                        smooth: true,
                        symbol: 'circle',
                        symbolSize: 6,
                        data: data.return,
                        lineStyle: { color: '#06b6d4', width: 2.5 },
                        areaStyle: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                { offset: 0, color: 'rgba(6,182,212,0.35)' },
                                { offset: 1, color: 'rgba(6,182,212,0.02)' }
                            ])
                        },
                        itemStyle: { color: '#06b6d4', borderWidth: 2, borderColor: '#fff' }
                    }
                ]
            };
            trendChart.setOption(option);
        }
    });
}

// ============================================
// 热门图书
// ============================================
function loadHotBooks() {
    $.ajax({
        url: '/api/hot_books',
        method: 'GET',
        success: function(data) {
            let html = '';
            data.forEach(function(book) {
                let rankClass = 'normal';
                if (book.rank === 1) rankClass = 'top1';
                else if (book.rank === 2) rankClass = 'top2';
                else if (book.rank === 3) rankClass = 'top3';

                html += `
                    <div class="hot-book-item">
                        <div class="hot-book-rank ${rankClass}">${book.rank}</div>
                        <div class="hot-book-info">
                            <div class="hot-book-name" title="${book.name}">${book.name}</div>
                            <div class="hot-book-author">${book.author} · ${book.category}</div>
                        </div>
                        <div class="hot-book-times">${book.times}次</div>
                    </div>
                `;
            });
            $('#hotBooksList').html(html);
        }
    });
}

// ============================================
// 读者统计
// ============================================
function loadReaderStats() {
    $.ajax({
        url: '/api/reader_stats',
        method: 'GET',
        success: function(data) {
            const option = {
                tooltip: {
                    trigger: 'item',
                    formatter: '{b}: {c}人 ({d}%)',
                    backgroundColor: 'rgba(0,0,0,0.85)',
                    borderColor: '#00d4ff',
                    borderWidth: 1,
                    textStyle: { color: '#fff' }
                },
                series: [{
                    type: 'pie',
                    radius: ['28%', '58%'],
                    center: ['50%', '55%'],
                    roseType: 'radius',
                    padAngle: 3,
                    itemStyle: {
                        borderRadius: 6,
                        borderColor: '#0a1a4a',
                        borderWidth: 2
                    },
                    label: {
                        show: true,
                        color: 'rgba(0,212,255,0.8)',
                        fontSize: 11,
                        formatter: '{b}\n{c}人'
                    },
                    labelLine: {
                        lineStyle: { color: 'rgba(0,212,255,0.4)' }
                    },
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 20,
                            shadowColor: 'rgba(0,212,255,0.4)'
                        }
                    },
                    data: data,
                    color: ['#00d4ff', '#00ff88', '#ffaa00', '#ff6b6b', '#a855f7']
                }]
            };
            readerChart.setOption(option);
        }
    });
}

// ============================================
// 实时数据（带数字动画）
// ============================================
function loadRealtimeData() {
    $.ajax({
        url: '/api/realtime_data',
        method: 'GET',
        success: function(data) {
            animateNumber('currentVisitors', data.current_visitors);
            animateNumber('todayBorrow', data.today_borrow);
            animateNumber('todayReturn', data.today_return);
            $('#updateTime').text(data.update_time);
        }
    });

    // 触发入馆数据更新
    $.get('/api/update_entry');
}

// ============================================
// 数字动画效果
// ============================================
function animateNumber(elementId, targetValue) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const currentValue = parseInt(element.textContent.replace(/,/g, '')) || 0;
    if (currentValue === targetValue) return;

    const diff = targetValue - currentValue;
    const duration = 600;
    const steps = 25;
    const stepValue = diff / steps;
    const stepDuration = duration / steps;

    let step = 0;
    const timer = setInterval(function() {
        step++;
        const newValue = Math.round(currentValue + stepValue * step);
        element.textContent = formatNumber(newValue);
        if (step >= steps) {
            clearInterval(timer);
            element.textContent = formatNumber(targetValue);
        }
    }, stepDuration);
}

// ============================================
// 格式化数字（千分位）
// ============================================
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}
