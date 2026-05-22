import type { CityAirQuality, CityHistory, HistoryEntry, AqiLevel } from '@/types/airQuality';

export const AQI_LEVELS: AqiLevel[] = [
  { level: '优', color: '#00e400', min: 0, max: 50, advice: '空气质量令人满意，基本无空气污染，各类人群可正常活动。' },
  { level: '良', color: '#ffff00', min: 51, max: 100, advice: '空气质量可接受，但某些污染物可能对极少数异常敏感人群健康有较弱影响。' },
  { level: '轻度污染', color: '#ff7e00', min: 101, max: 150, advice: '易感人群症状有轻度加剧，健康人群出现刺激症状。建议儿童、老年人及心脏病、呼吸系统疾病患者应减少长时间、高强度的户外锻炼。' },
  { level: '中度污染', color: '#ff0000', min: 151, max: 200, advice: '进一步加剧易感人群症状，可能对健康人群心脏、呼吸系统有影响。建议疾病患者避免长时间、高强度的户外锻练，一般人群适量减少户外运动。' },
  { level: '重度污染', color: '#99004c', min: 201, max: 300, advice: '心脏病和肺病患者症状显著加剧，运动耐受力降低，健康人群普遍出现症状。建议儿童、老年人和病人应停留在室内，停止户外运动，一般人群减少户外运动。' },
  { level: '严重污染', color: '#7e0023', min: 301, max: 500, advice: '健康人群运动耐受力降低，有明显强烈症状，提前出现某些疾病。建议儿童、老年人和病人应停留在室内，避免体力消耗，一般人群避免户外活动。' },
];

export function getAqiLevel(aqi: number): AqiLevel {
  for (const level of AQI_LEVELS) {
    if (aqi >= level.min && aqi <= level.max) return level;
  }
  return AQI_LEVELS[AQI_LEVELS.length - 1];
}

// 初始城市数据（基于中国主要城市2025年典型空气质量数据）
export const INITIAL_CITIES: CityAirQuality[] = [
  {
    cityId: 'beijing',
    cityName: '北京',
    province: '北京市',
    aqi: 95,
    level: '良',
    color: '#ffff00',
    primaryPollutant: 'PM2.5',
    pollutants: { pm25: 68, pm10: 95, so2: 8, no2: 42, co: 0.9, o3: 110 },
    timestamp: new Date().toISOString(),
    temp: 22,
    humidity: 45,
    windLevel: '3级',
  },
  {
    cityId: 'shanghai',
    cityName: '上海',
    province: '上海市',
    aqi: 72,
    level: '良',
    color: '#ffff00',
    primaryPollutant: 'PM2.5',
    pollutants: { pm25: 48, pm10: 72, so2: 9, no2: 38, co: 0.7, o3: 95 },
    timestamp: new Date().toISOString(),
    temp: 25,
    humidity: 65,
    windLevel: '2级',
  },
  {
    cityId: 'guangzhou',
    cityName: '广州',
    province: '广东省',
    aqi: 58,
    level: '良',
    color: '#ffff00',
    primaryPollutant: 'O3',
    pollutants: { pm25: 32, pm10: 55, so2: 10, no2: 45, co: 0.8, o3: 138 },
    timestamp: new Date().toISOString(),
    temp: 30,
    humidity: 78,
    windLevel: '2级',
  },
  {
    cityId: 'shenzhen',
    cityName: '深圳',
    province: '广东省',
    aqi: 42,
    level: '优',
    color: '#00e400',
    primaryPollutant: '-',
    pollutants: { pm25: 22, pm10: 38, so2: 6, no2: 28, co: 0.5, o3: 85 },
    timestamp: new Date().toISOString(),
    temp: 29,
    humidity: 75,
    windLevel: '2级',
  },
  {
    cityId: 'chengdu',
    cityName: '成都',
    province: '四川省',
    aqi: 118,
    level: '轻度污染',
    color: '#ff7e00',
    primaryPollutant: 'PM2.5',
    pollutants: { pm25: 88, pm10: 120, so2: 12, no2: 55, co: 1.1, o3: 75 },
    timestamp: new Date().toISOString(),
    temp: 20,
    humidity: 70,
    windLevel: '1级',
  },
  {
    cityId: 'xian',
    cityName: '西安',
    province: '陕西省',
    aqi: 135,
    level: '轻度污染',
    color: '#ff7e00',
    primaryPollutant: 'PM10',
    pollutants: { pm25: 78, pm10: 155, so2: 15, no2: 62, co: 1.3, o3: 88 },
    timestamp: new Date().toISOString(),
    temp: 23,
    humidity: 50,
    windLevel: '2级',
  },
  {
    cityId: 'wuhan',
    cityName: '武汉',
    province: '湖北省',
    aqi: 85,
    level: '良',
    color: '#ffff00',
    primaryPollutant: 'NO2',
    pollutants: { pm25: 55, pm10: 82, so2: 11, no2: 58, co: 0.9, o3: 102 },
    timestamp: new Date().toISOString(),
    temp: 24,
    humidity: 60,
    windLevel: '2级',
  },
  {
    cityId: 'hangzhou',
    cityName: '杭州',
    province: '浙江省',
    aqi: 65,
    level: '良',
    color: '#ffff00',
    primaryPollutant: 'O3',
    pollutants: { pm25: 38, pm10: 62, so2: 8, no2: 35, co: 0.6, o3: 125 },
    timestamp: new Date().toISOString(),
    temp: 26,
    humidity: 68,
    windLevel: '2级',
  },
  {
    cityId: 'nanjing',
    cityName: '南京',
    province: '江苏省',
    aqi: 88,
    level: '良',
    color: '#ffff00',
    primaryPollutant: 'PM2.5',
    pollutants: { pm25: 62, pm10: 88, so2: 10, no2: 48, co: 0.8, o3: 108 },
    timestamp: new Date().toISOString(),
    temp: 25,
    humidity: 58,
    windLevel: '3级',
  },
  {
    cityId: 'chongqing',
    cityName: '重庆',
    province: '重庆市',
    aqi: 105,
    level: '轻度污染',
    color: '#ff7e00',
    primaryPollutant: 'PM2.5',
    pollutants: { pm25: 75, pm10: 98, so2: 14, no2: 52, co: 1.0, o3: 68 },
    timestamp: new Date().toISOString(),
    temp: 28,
    humidity: 72,
    windLevel: '1级',
  },
  {
    cityId: 'tianjin',
    cityName: '天津',
    province: '天津市',
    aqi: 108,
    level: '轻度污染',
    color: '#ff7e00',
    primaryPollutant: 'PM2.5',
    pollutants: { pm25: 78, pm10: 115, so2: 18, no2: 55, co: 1.2, o3: 92 },
    timestamp: new Date().toISOString(),
    temp: 23,
    humidity: 55,
    windLevel: '3级',
  },
  {
    cityId: 'shenyang',
    cityName: '沈阳',
    province: '辽宁省',
    aqi: 82,
    level: '良',
    color: '#ffff00',
    primaryPollutant: 'PM2.5',
    pollutants: { pm25: 58, pm10: 85, so2: 20, no2: 45, co: 1.0, o3: 78 },
    timestamp: new Date().toISOString(),
    temp: 18,
    humidity: 48,
    windLevel: '3级',
  },
];

// 生成24小时历史数据
function generateHourlyHistory(city: CityAirQuality): CityHistory {
  const hourly: HistoryEntry[] = [];
  const now = new Date();
  const baseAqi = city.aqi;
  
  for (let i = 23; i >= 0; i--) {
    const t = new Date(now.getTime() - i * 60 * 60 * 1000);
    const hour = t.getHours();
    // 模拟日内变化：早晚高峰AQI略高
    const rushFactor = (hour >= 7 && hour <= 9) || (hour >= 17 && hour <= 19) ? 1.15 : 1.0;
    const randomFactor = 0.85 + Math.random() * 0.3;
    const aqi = Math.round(baseAqi * rushFactor * randomFactor);
    const ratio = aqi / baseAqi;
    
    hourly.push({
      time: `${hour.toString().padStart(2, '0')}:00`,
      aqi,
      pm25: Math.round(city.pollutants.pm25 * ratio),
      pm10: Math.round(city.pollutants.pm10 * ratio),
      so2: Math.round(city.pollutants.so2 * ratio * 10) / 10,
      no2: Math.round(city.pollutants.no2 * ratio),
      co: Math.round(city.pollutants.co * ratio * 10) / 10,
      o3: Math.round(city.pollutants.o3 * ratio),
    });
  }
  
  return { cityId: city.cityId, hourly };
}

// 生成所有城市的历史数据
export function generateAllHistory(cities: CityAirQuality[]): CityHistory[] {
  return cities.map(c => generateHourlyHistory(c));
}

// 模拟数据动态更新
export function simulateDataUpdate(city: CityAirQuality): CityAirQuality {
  const drift = 0.95 + Math.random() * 0.1; // ±5% 波动
  const newAqi = Math.max(10, Math.min(500, Math.round(city.aqi * drift)));
  const level = getAqiLevel(newAqi);
  const ratio = newAqi / Math.max(city.aqi, 1);
  
  return {
    ...city,
    aqi: newAqi,
    level: level.level,
    color: level.color,
    primaryPollutant: newAqi > 100 ? 'PM2.5' : (newAqi > 60 ? 'O3' : '-'),
    pollutants: {
      pm25: Math.max(5, Math.round(city.pollutants.pm25 * ratio)),
      pm10: Math.max(10, Math.round(city.pollutants.pm10 * ratio)),
      so2: Math.max(2, Math.round(city.pollutants.so2 * ratio * 10) / 10),
      no2: Math.max(5, Math.round(city.pollutants.no2 * ratio)),
      co: Math.max(0.2, Math.round(city.pollutants.co * ratio * 10) / 10),
      o3: Math.max(10, Math.round(city.pollutants.o3 * ratio)),
    },
    temp: city.temp + Math.round((Math.random() - 0.5) * 2),
    humidity: Math.max(20, Math.min(95, city.humidity + Math.round((Math.random() - 0.5) * 5))),
    timestamp: new Date().toISOString(),
  };
}
