import { Thermometer, Droplets, Wind, Clock } from 'lucide-react';

interface WeatherInfoProps {
  temp: number;
  humidity: number;
  windLevel: string;
  timestamp: string;
  primaryPollutant: string;
  aqi: number;
  level: string;
  color: string;
}

export default function WeatherInfo({
  temp,
  humidity,
  windLevel,
  timestamp,
  level,
  color,
}: WeatherInfoProps) {
  const updateTime = new Date(timestamp).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-3">
      <div className="grid grid-cols-4 gap-2">
        <div className="flex flex-col items-center justify-center p-2 rounded-xl bg-blue-50">
          <Thermometer className="w-4 h-4 text-blue-500 mb-1" />
          <span className="text-sm font-bold text-gray-900">{temp}°C</span>
          <span className="text-[10px] text-gray-500">温度</span>
        </div>
        <div className="flex flex-col items-center justify-center p-2 rounded-xl bg-cyan-50">
          <Droplets className="w-4 h-4 text-cyan-500 mb-1" />
          <span className="text-sm font-bold text-gray-900">{humidity}%</span>
          <span className="text-[10px] text-gray-500">湿度</span>
        </div>
        <div className="flex flex-col items-center justify-center p-2 rounded-xl bg-teal-50">
          <Wind className="w-4 h-4 text-teal-500 mb-1" />
          <span className="text-sm font-bold text-gray-900">{windLevel}</span>
          <span className="text-[10px] text-gray-500">风力</span>
        </div>
        <div className="flex flex-col items-center justify-center p-2 rounded-xl" style={{ backgroundColor: `${color}18` }}>
          <div className="w-4 h-4 rounded-full mb-1" style={{ backgroundColor: color }} />
          <span className="text-sm font-bold" style={{ color: '#1a1a1a' }}>{level}</span>
          <span className="text-[10px] text-gray-500">首要污染物</span>
        </div>
      </div>
      <div className="mt-2 flex items-center justify-center gap-1 text-[10px] text-gray-400">
        <Clock className="w-3 h-3" />
        <span>数据更新于 {updateTime} · 每30秒自动刷新</span>
      </div>
    </div>
  );
}
