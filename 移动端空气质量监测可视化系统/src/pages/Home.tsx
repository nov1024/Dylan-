import { useState } from 'react';
import { RefreshCw, Activity, BarChart3, TrendingUp, Globe } from 'lucide-react';
import { useAirQuality } from '@/hooks/useAirQuality';
import CitySelector from '@/components/CitySelector';
import AqiGauge from '@/components/AqiGauge';
import TrendChart from '@/components/TrendChart';
import RadarChartComponent from '@/components/RadarChart';
import PollutantBar from '@/components/PollutantBar';
import CityRanking from '@/components/CityRanking';
import WeatherInfo from '@/components/WeatherInfo';
import { AQI_LEVELS } from '@/data/cityData';

type TabKey = 'overview' | 'trend' | 'ranking';

const TABS: { key: TabKey; label: string; icon: typeof Activity }[] = [
  { key: 'overview', label: '概览', icon: Activity },
  { key: 'trend', label: '趋势', icon: TrendingUp },
  { key: 'ranking', label: '排名', icon: BarChart3 },
];

export default function Home() {
  const {
    cities,
    selectedCity,
    selectedHistory,
    selectedCityId,
    setSelectedCityId,
    isRefreshing,
    refreshData,
  } = useAirQuality();

  const [activeTab, setActiveTab] = useState<TabKey>('overview');

  const aqiAdvice = AQI_LEVELS.find(l => l.level === selectedCity.level)?.advice || '';

  return (
    <div className="min-h-screen bg-gradient-to-b from-sky-50 via-white to-gray-50">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-gray-100">
        <div className="max-w-lg mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-500 to-teal-400 flex items-center justify-center shadow-sm">
              <Globe className="w-4 h-4 text-white" />
            </div>
            <div>
              <h1 className="text-base font-bold text-gray-900 leading-tight">空气质量监测</h1>
              <p className="text-[10px] text-gray-400">全国城市实时AQI可视化</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <CitySelector
              cities={cities}
              selectedCityId={selectedCityId}
              onSelect={setSelectedCityId}
            />
            <button
              onClick={refreshData}
              disabled={isRefreshing}
              className="w-9 h-9 flex items-center justify-center rounded-full bg-gray-50 active:bg-gray-100 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 text-gray-600 ${isRefreshing ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-lg mx-auto px-4 py-4 pb-24 space-y-4">
        {/* AQI Gauge */}
        <AqiGauge
          aqi={selectedCity.aqi}
          cityName={selectedCity.cityName}
          level={selectedCity.level}
          color={selectedCity.color}
        />

        {/* Weather & Environment */}
        <WeatherInfo
          temp={selectedCity.temp}
          humidity={selectedCity.humidity}
          windLevel={selectedCity.windLevel}
          timestamp={selectedCity.timestamp}
          primaryPollutant={selectedCity.primaryPollutant}
          aqi={selectedCity.aqi}
          level={selectedCity.level}
          color={selectedCity.color}
        />

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="space-y-4 animate-in slide-in-from-right duration-300">
            <PollutantBar pollutants={selectedCity.pollutants} />
            <RadarChartComponent
              pollutants={selectedCity.pollutants}
              cityName={selectedCity.cityName}
            />
          </div>
        )}

        {activeTab === 'trend' && (
          <div className="space-y-4 animate-in slide-in-from-right duration-300">
            <TrendChart data={selectedHistory} pollutants={['aqi']} />
            <TrendChart data={selectedHistory} pollutants={['pm25', 'pm10']} />
            <TrendChart data={selectedHistory} pollutants={['so2', 'no2', 'o3']} />
          </div>
        )}

        {activeTab === 'ranking' && (
          <div className="space-y-4 animate-in slide-in-from-right duration-300">
            <CityRanking
              cities={cities}
              selectedCityId={selectedCityId}
              onSelect={setSelectedCityId}
            />
          </div>
        )}

        {/* Health Advice */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
          <h3 className="text-sm font-bold text-gray-900 mb-2">健康建议</h3>
          <p className="text-xs text-gray-600 leading-relaxed">{aqiAdvice}</p>
        </div>

        {/* AQI Reference */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
          <h3 className="text-sm font-bold text-gray-900 mb-3">AQI参考标准</h3>
          <div className="grid grid-cols-3 gap-2">
            {AQI_LEVELS.map(item => (
              <div key={item.level} className="flex items-center gap-2 p-2 rounded-lg bg-gray-50">
                <div className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
                <div>
                  <div className="text-xs font-medium text-gray-800">{item.level}</div>
                  <div className="text-[10px] text-gray-400">{item.min}-{item.max}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Data Source Note */}
        <div className="text-center py-2">
          <p className="text-[10px] text-gray-400">
            数据基于中国环境监测总站标准科学模拟 · 仅供学习参考
          </p>
        </div>
      </main>

      {/* Bottom Tab Bar */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white/90 backdrop-blur-md border-t border-gray-100 z-40">
        <div className="max-w-lg mx-auto flex items-center justify-around py-2">
          {TABS.map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.key;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex flex-col items-center gap-0.5 px-6 py-1.5 rounded-xl transition-all ${
                  isActive ? 'bg-blue-50' : ''
                }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-blue-500' : 'text-gray-400'}`} />
                <span className={`text-[10px] font-medium ${isActive ? 'text-blue-600' : 'text-gray-400'}`}>
                  {tab.label}
                </span>
              </button>
            );
          })}
        </div>
      </nav>
    </div>
  );
}
