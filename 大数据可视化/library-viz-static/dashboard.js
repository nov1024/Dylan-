/**
 * 图书馆大数据可视化大屏 - 静态演示版本
 * 使用模拟数据展示ECharts图表效果
 */

let collectionChart, categoryPieChart, readerChart;
let entryChart, trendChart;
let categoryBarChart, borrowCategoryChart;

const colorPalette = [
    '#00d4ff', '#00ff88', '#ffaa00', '#ff6b6b', '#a855f7',
    '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
    '#0ea5e9', '#22c55e', '#eab308', '#f97316', '#ec4899'
];

// 粒子背景系统
class ParticleSystem {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.init();
    }
    init() {
        this.resize();
        window.addEventListener('resize', () => this.resize());
        this.createParticles();
        this.animate();
    }
    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }
    createParticles() {
        const count = Math.floor((this.canvas.width * this.canvas.height) / 12000);
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
        this.particles.forEach(p => {
            p.x += p.vx; p.y += p.vy;
            if (p.x < 0 || p.x > this.canvas.width) p.vx *= -1;
            if (p.y < 0 || p.y > this.canvas.height) p.vy *= -1;
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            this.ctx.fillStyle = `rgba(0, 212, 255, ${p.opacity})`;
            this.ctx.fill();
        });
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

// 模拟数据
const mockData = {
    collection: {
        categories: ['中文图书', '电子资源', '外文图书', '期刊杂志', '学位论文', '多媒体资源'],
        total: [285000, 120000, 65000, 45000, 35000, 15000],
        available: [256500, 120000, 61750, 43200, 33250, 14250],
        borrowed: [28500, 0, 3250, 1800, 1750, 750],
        total_collection: 565000
    },
    entry: {
        hours: ['08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00','20:00','21:00','22:00'],
        entry: [120,280,350,290,380,320,270,310,340,290,180,150,90,60,30],
        exit: [80,150,220,260,310,280,250,290,320,350,280,220,140,80,40]
    },
    categories: {
        categories: ['T-工业技术','I-文学','F-经济','G-文化教育','O-数理科学','H-语言文字','K-历史地理','D-政治法律','R-医药卫生','J-艺术'],
        book_counts: [68900,45600,35600,28900,25600,22300,19500,18900,18600,16800],
        borrow_counts: [12500,8900,6500,5200,4800,4100,3600,3200,3400,3100]
    },
    trends: {
        dates: ['03-22','03-23','03-24','03-25','03-26','03-27','03-28','03-29','03-30','03-31','04-01','04-02','04-03','04-04','04-05','04-06','04-07','04-08','04-09','04-10','04-11','04-12','04-13','04-14','04-15','04-16','04-17','04-18','04-19','04-20'],
        borrow: [320,280,350,310,290,340,380,360,320,300,340,370,350,310,330,360,340,320,350,380,370,340,360,390,370,350,380,400,380,360],
        return: [290,260,320,300,270,310,350,340,300,280,320,350,330,290,310,340,320,300,330,360,350,320,340,370,350,330,360,380,360,340]
    },
    hotBooks: [
        {rank:1,name:'Python编程：从入门到实践',author:'埃里克·马瑟斯',category:'计算机',times:256},
        {rank:2,name:'活着',author:'余华',category:'文学',times:234},
        {rank:3,name:'三体',author:'刘慈欣',category:'科幻',times:228},
        {rank:4,name:'经济学原理',author:'曼昆',category:'经济',times:215},
        {rank:5,name:'人类简史',author:'尤瓦尔·赫拉利',category:'历史',times:198},
        {rank:6,name:'深度学习',author:'Ian Goodfellow',category:'计算机',times:187},
        {rank:7,name:'百年孤独',author:'马尔克斯',category:'文学',times:176},
        {rank:8,name:'数据结构与算法',author:'严蔚敏',category:'计算机',times:168},
        {rank:9,name:'心理学与生活',author:'理查德·格里格',category:'心理学',times:156},
        {rank:10,name:'机器学习',author:'周志华',category:'计算机',times:145}
    ],
    readers: [
        {name:'本科生',value:25680},
        {name:'研究生',value:8960},
        {name:'教职工',value:3680},
        {name:'博士生',value:2350},
        {name:'校外读者',value:1250}
    ]
};

document.addEventListener('DOMContentLoaded', function() {
    new ParticleSystem('particleCanvas');
    initCharts();
    updateDateTime();
    renderAll();
    setInterval(updateDateTime, 1000);
    setInterval(simulateRealtime, 5000);
});

function updateDateTime() {
    const now = new Date();
    document.getElementById('currentDate').textContent = now.toLocaleDateString('zh-CN', {year:'numeric',month:'2-digit',day:'2-digit',weekday:'long'});
    document.getElementById('currentTime').textContent = now.toLocaleTimeString('zh-CN', {hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false});
}

function initCharts() {
    collectionChart = echarts.init(document.getElementById('collectionChart'));
    categoryPieChart = echarts.init(document.getElementById('categoryPieChart'));
    readerChart = echarts.init(document.getElementById('readerChart'));
    entryChart = echarts.init(document.getElementById('entryChart'));
    trendChart = echarts.init(document.getElementById('trendChart'));
    categoryBarChart = echarts.init(document.getElementById('categoryBarChart'));
    borrowCategoryChart = echarts.init(document.getElementById('borrowCategoryChart'));
    window.addEventListener('resize', () => {
        [collectionChart,categoryPieChart,readerChart,entryChart,trendChart,categoryBarChart,borrowCategoryChart].forEach(c => c && c.resize());
    });
}

function renderAll() {
    renderCollectionStats();
    renderEntryRecords();
    renderBookCategories();
    renderBorrowTrends();
    renderHotBooks();
    renderReaderStats();
}

function renderCollectionStats() {
    const d = mockData.collection;
    document.getElementById('totalCollection').textContent = d.total_collection.toLocaleString();
    collectionChart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, backgroundColor: 'rgba(0,0,0,0.85)', borderColor: '#00d4ff', borderWidth: 1, textStyle: { color: '#fff' } },
        legend: { data: ['总量','可借','已借'], textStyle: { color: 'rgba(0,212,255,0.8)', fontSize: 11 }, top: 5 },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '18%', containLabel: true },
        xAxis: { type: 'category', data: d.categories, axisLine: { lineStyle: { color: 'rgba(0,212,255,0.4)' } }, axisLabel: { color: 'rgba(0,212,255,0.7)', fontSize: 10, rotate: 25 } },
        yAxis: { type: 'value', axisLine: { lineStyle: { color: 'rgba(0,212,255,0.4)' } }, axisLabel: { color: 'rgba(0,212,255,0.7)', fontSize: 10 }, splitLine: { lineStyle: { color: 'rgba(0,212,255,0.08)' } } },
        series: [
            { name: '总量', type: 'bar', data: d.total, itemStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#00d4ff'},{offset:1,color:'#0066aa'}]), borderRadius: [4,4,0,0] }, barWidth: '25%' },
            { name: '可借', type: 'bar', data: d.available, itemStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#00ff88'},{offset:1,color:'#008844'}]), borderRadius: [4,4,0,0] }, barWidth: '25%' },
            { name: '已借', type: 'bar', data: d.borrowed, itemStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#ffaa00'},{offset:1,color:'#cc6600'}]), borderRadius: [4,4,0,0] }, barWidth: '25%' }
        ]
    });
}

function renderEntryRecords() {
    const d = mockData.entry;
    entryChart.setOption({
        tooltip: { trigger: 'axis', backgroundColor: 'rgba(0,0,0,0.85)', borderColor: '#00d4ff', borderWidth: 1, textStyle: { color: '#fff' } },
        legend: { data: ['入馆人数','出馆人数'], textStyle: { color: 'rgba(0,212,255,0.8)' }, top: 5 },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
        xAxis: { type: 'category', boundaryGap: false, data: d.hours, axisLine: { lineStyle: { color: 'rgba(0,212,255,0.4)' } }, axisLabel: { color: 'rgba(0,212,255,0.7)', fontSize: 11 } },
        yAxis: { type: 'value', axisLine: { lineStyle: { color: 'rgba(0,212,255,0.4)' } }, axisLabel: { color: 'rgba(0,212,255,0.7)' }, splitLine: { lineStyle: { color: 'rgba(0,212,255,0.08)' } } },
        series: [
            { name: '入馆人数', type: 'line', smooth: true, symbol: 'circle', symbolSize: 8, data: d.entry, lineStyle: { color: '#00ff88', width: 3 }, areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(0,255,136,0.35)'},{offset:1,color:'rgba(0,255,136,0.02)'}]) }, itemStyle: { color: '#00ff88', borderWidth: 2, borderColor: '#fff' } },
            { name: '出馆人数', type: 'line', smooth: true, symbol: 'circle', symbolSize: 8, data: d.exit, lineStyle: { color: '#ff6b6b', width: 3 }, areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(255,107,107,0.35)'},{offset:1,color:'rgba(255,107,107,0.02)'}]) }, itemStyle: { color: '#ff6b6b', borderWidth: 2, borderColor: '#fff' } }
        ]
    });
}

function renderBookCategories() {
    const d = mockData.categories;
    const pieData = d.categories.slice(0,10).map((c,i) => ({ name: c.split('-')[1], value: d.book_counts[i] }));
    categoryPieChart.setOption({
        tooltip: { trigger: 'item', formatter: '{b}: {c}册 ({d}%)', backgroundColor: 'rgba(0,0,0,0.85)', borderColor: '#00d4ff', borderWidth: 1, textStyle: { color: '#fff' } },
        series: [{ type: 'pie', radius: ['38%','68%'], center: ['50%','55%'], padAngle: 3, itemStyle: { borderRadius: 6, borderColor: '#0a1a4a', borderWidth: 2 }, label: { color: 'rgba(0,212,255,0.8)', fontSize: 10, formatter: '{b}\\n{d}%' }, labelLine: { lineStyle: { color: 'rgba(0,212,255,0.4)' }, length: 12, length2: 8 }, emphasis: { itemStyle: { shadowBlur: 20, shadowColor: 'rgba(0,212,255,0.4)' } }, data: pieData, color: colorPalette }]
    });
    const top10 = { categories: d.categories.slice(0,10).reverse(), counts: d.book_counts.slice(0,10).reverse() };
    categoryBarChart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, backgroundColor: 'rgba(0,0,0,0.85)', borderColor: '#00d4ff', textStyle: { color: '#fff' } },
        grid: { left: '3%', right: '10%', bottom: '3%', top: '3%', containLabel: true },
        xAxis: { type: 'value', axisLine: { lineStyle: { color: 'rgba(0,212,255,0.4)' } }, axisLabel: { color: 'rgba(0,212,255,0.7)', fontSize: 10 }, splitLine: { lineStyle: { color: 'rgba(0,212,255,0.08)' } } },
        yAxis: { type: 'category', data: top10.categories, axisLine: { lineStyle: { color: 'rgba(0,212,255,0.4)' } }, axisLabel: { color: 'rgba(0,212,255,0.7)', fontSize: 10, width: 90, overflow: 'truncate' } },
        series: [{ type: 'bar', data: top10.counts, itemStyle: { color: new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#00a8e8'},{offset:1,color:'#00ff88'}]), borderRadius: [0,6,6,0] }, label: { show: true, position: 'right', color: '#00d4ff', fontSize: 10, formatter: '{c}' }, barWidth: '55%' }]
    });
    borrowCategoryChart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, backgroundColor: 'rgba(0,0,0,0.85)', borderColor: '#00d4ff', textStyle: { color: '#fff' } },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '3%', containLabel: true },
        xAxis: { type: 'value', axisLine: { lineStyle: { color: 'rgba(0,212,255,0.4)' } }, axisLabel: { color: 'rgba(0,212,255,0.7)', fontSize: 10 }, splitLine: { lineStyle: { color: 'rgba(0,212,255,0.08)' } } },
        yAxis: { type: 'category', data: d.categories.slice(0,8).reverse(), axisLine: { lineStyle: { color: 'rgba(0,212,255,0.4)' } }, axisLabel: { color: 'rgba(0,212,255,0.7)', fontSize: 9, width: 75, overflow: 'truncate' } },
        series: [{ type: 'bar', data: d.borrow_counts.slice(0,8).reverse(), itemStyle: { color: new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#ff6b6b'},{offset:1,color:'#ffaa00'}]), borderRadius: [0,6,6,0] }, barWidth: '55%' }]
    });
}

function renderBorrowTrends() {
    const d = mockData.trends;
    trendChart.setOption({
        tooltip: { trigger: 'axis', backgroundColor: 'rgba(0,0,0,0.85)', borderColor: '#00d4ff', borderWidth: 1, textStyle: { color: '#fff' } },
        legend: { data: ['借阅量','归还量'], textStyle: { color: 'rgba(0,212,255,0.8)' }, top: 5 },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
        xAxis: { type: 'category', boundaryGap: false, data: d.dates, axisLine: { lineStyle: { color: 'rgba(0,212,255,0.4)' } }, axisLabel: { color: 'rgba(0,212,255,0.7)', fontSize: 10, rotate: 45 } },
        yAxis: { type: 'value', axisLine: { lineStyle: { color: 'rgba(0,212,255,0.4)' } }, axisLabel: { color: 'rgba(0,212,255,0.7)' }, splitLine: { lineStyle: { color: 'rgba(0,212,255,0.08)' } } },
        series: [
            { name: '借阅量', type: 'line', smooth: true, symbol: 'circle', symbolSize: 6, data: d.borrow, lineStyle: { color: '#a855f7', width: 2.5 }, areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(168,85,247,0.35)'},{offset:1,color:'rgba(168,85,247,0.02)'}]) }, itemStyle: { color: '#a855f7', borderWidth: 2, borderColor: '#fff' } },
            { name: '归还量', type: 'line', smooth: true, symbol: 'circle', symbolSize: 6, data: d.return, lineStyle: { color: '#06b6d4', width: 2.5 }, areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(6,182,212,0.35)'},{offset:1,color:'rgba(6,182,212,0.02)'}]) }, itemStyle: { color: '#06b6d4', borderWidth: 2, borderColor: '#fff' } }
        ]
    });
}

function renderHotBooks() {
    const list = document.getElementById('hotBooksList');
    list.innerHTML = mockData.hotBooks.map(book => {
        let rc = book.rank === 1 ? 'top1' : book.rank === 2 ? 'top2' : book.rank === 3 ? 'top3' : 'normal';
        return `<div class="hot-book-item"><div class="hot-book-rank ${rc}">${book.rank}</div><div class="hot-book-info"><div class="hot-book-name" title="${book.name}">${book.name}</div><div class="hot-book-author">${book.author} · ${book.category}</div></div><div class="hot-book-times">${book.times}次</div></div>`;
    }).join('');
}

function renderReaderStats() {
    readerChart.setOption({
        tooltip: { trigger: 'item', formatter: '{b}: {c}人 ({d}%)', backgroundColor: 'rgba(0,0,0,0.85)', borderColor: '#00d4ff', borderWidth: 1, textStyle: { color: '#fff' } },
        series: [{ type: 'pie', radius: ['28%','58%'], center: ['50%','55%'], roseType: 'radius', padAngle: 3, itemStyle: { borderRadius: 6, borderColor: '#0a1a4a', borderWidth: 2 }, label: { color: 'rgba(0,212,255,0.8)', fontSize: 11, formatter: '{b}\\n{c}人' }, labelLine: { lineStyle: { color: 'rgba(0,212,255,0.4)' } }, emphasis: { itemStyle: { shadowBlur: 20, shadowColor: 'rgba(0,212,255,0.4)' } }, data: mockData.readers, color: ['#00d4ff','#00ff88','#ffaa00','#ff6b6b','#a855f7'] }]
    });
}

function simulateRealtime() {
    const visitors = document.getElementById('currentVisitors');
    const borrow = document.getElementById('todayBorrow');
    const ret = document.getElementById('todayReturn');
    visitors.textContent = (parseInt(visitors.textContent.replace(/,/g,'')) + Math.floor(Math.random()*41)-20).toLocaleString();
    borrow.textContent = (parseInt(borrow.textContent.replace(/,/g,'')) + Math.floor(Math.random()*4)).toLocaleString();
    ret.textContent = (parseInt(ret.textContent.replace(/,/g,'')) + Math.floor(Math.random()*4)).toLocaleString();
    document.getElementById('updateTime').textContent = new Date().toLocaleString('zh-CN');
}
