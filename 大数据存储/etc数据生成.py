cat << 'EOF' > / usr / local / kafka / generate_etc_data.py
# -*- coding: utf-8 -*-
import time
import json
import random
from datetime import datetime
from kafka import KafkaProducer

# --- 配置 ---
KAFKA_TOPIC = 'etc_traffic_data'
KAFKA_SERVER = 'master:9092'
TARGET_TPS = 50  # 目标：每秒50条

# --- 字典 (基于徐州样例) ---
DISTRICTS_MAP = {
    '云龙区': 'G30连霍高速徐州南收费站',
    '鼓楼区': 'G3京台高速徐州北收费站',
    '泉山区': '三环西路与徐萧公路交叉口',
    '铜山县': '徐州市铜山县G311徐州-西峡K207卡口',
    '新沂市': '徐州市新沂市G235国道235K10卡口',
    '邳州市': '徐州市邳州市S250宿邳线K1卡口',
    '高速五大队': 'G3京台高速K731苏鲁界省际卡口'
}
DIRECTIONS = ['1', '2']
PLATE_TYPES = ['01', '02', '52', '06']
BRANDS = ['北京牌-H6', '金程牌-赛风', '大众-迈腾', '徐工-重卡', '宝马-X5', '丰田-凯美瑞']

# 用于模拟套牌：缓存最近生成的10个车牌
recent_plates = []


def generate_plate():
    """生成完整的车牌号 (不脱敏)"""
    # 5% 的概率从缓存中抽取车牌，模拟“套牌”或“短时间内重复出现”
    if len(recent_plates) > 0 and random.random() < 0.05:
        return random.choice(recent_plates)

    provinces = "苏鲁豫皖京冀浙"
    header = random.choice(provinces) + random.choice("ABCDEFGHJKL")

    # 随机生成新能源(6位)或普通车(5位)
    is_new_energy = random.random() < 0.2
    body_len = 6 if is_new_energy else 5
    body = "".join(random.sample("0123456789ABCDEFGHJKLMNPQRSTUVWXYZ", body_len))

    plate = header + body

    # 更新缓存供套牌模拟使用
    if len(recent_plates) > 20: recent_plates.pop(0)
    recent_plates.append(plate)

    return plate


def generate_full_id():
    return "G320300109" + "".join([str(random.randint(0, 9)) for _ in range(9)])


def main():
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_SERVER,
            batch_size=65536,  # 增加批处理大小提升吞吐量
            linger_ms=10,  # 微小延迟合并数据
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
        )
        print(f"✅ 启动成功！正在以 {TARGET_TPS}条/秒 的速度写入徐州ETC全量数据...")

        seq = 100000
        while True:
            t_start = time.time()

            # 批量生成 50 条
            for _ in range(TARGET_TPS):
                dist = random.choice(list(DISTRICTS_MAP.keys()))
                data = {
                    "GCXH": generate_full_id(),
                    "XZQHMC": dist,
                    "KKMC": DISTRICTS_MAP[dist],
                    "FXLX": random.choice(DIRECTIONS),
                    "GCSJ": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "HPZL": random.choice(PLATE_TYPES),
                    "HPHM": generate_plate(),  # 完整车牌
                    "CLPPXH": random.choice(BRANDS)
                }
                producer.send(KAFKA_TOPIC, data)
                seq += 1

            # 仅每1000条在控制台打一个点，避免IO阻塞速度
            if seq % 1000 == 0:
                print(f"已累计发送 {seq} 条数据... 当前车牌样例: {data['HPHM']}")

            # 严格频率控制
            t_elapsed = time.time() - t_start
            if t_elapsed < 1.0:
                time.sleep(1.0 - t_elapsed)

    except Exception as e:
        print(f"❌ 运行错误: {e}")


if __name__ == "__main__":
    main()
EOF