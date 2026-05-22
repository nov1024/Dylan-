import { useState, useEffect, useRef, useCallback } from 'react';
import { INITIAL_CITIES, generateAllHistory, simulateDataUpdate } from '@/data/cityData';
import type { CityAirQuality, CityHistory } from '@/types/airQuality';

const UPDATE_INTERVAL = 30000; // 30秒自动刷新

export function useAirQuality() {
  const [cities, setCities] = useState<CityAirQuality[]>(INITIAL_CITIES);
  const [histories, setHistories] = useState<CityHistory[]>(() => generateAllHistory(INITIAL_CITIES));
  const [selectedCityId, setSelectedCityId] = useState<string>('beijing');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const selectedCity = cities.find(c => c.cityId === selectedCityId) || cities[0];
  const selectedHistory = histories.find(h => h.cityId === selectedCityId)?.hourly || [];

  // 模拟数据刷新
  const refreshData = useCallback(() => {
    setIsRefreshing(true);
    
    // 模拟网络延迟
    setTimeout(() => {
      setCities(prev => {
        const updated = prev.map(city => simulateDataUpdate(city));
        
        // 同步更新历史数据
        setHistories(prevHist => 
          prevHist.map(h => {
            const updatedCity = updated.find(c => c.cityId === h.cityId);
            if (!updatedCity) return h;
            
            const newHourly = [...h.hourly.slice(1), {
              time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
              aqi: updatedCity.aqi,
              pm25: updatedCity.pollutants.pm25,
              pm10: updatedCity.pollutants.pm10,
              so2: updatedCity.pollutants.so2,
              no2: updatedCity.pollutants.no2,
              co: updatedCity.pollutants.co,
              o3: updatedCity.pollutants.o3,
            }];
            
            return { ...h, hourly: newHourly };
          })
        );
        
        return updated;
      });
      
      setIsRefreshing(false);
    }, 600);
  }, []);

  // 自动定时刷新
  useEffect(() => {
    intervalRef.current = setInterval(refreshData, UPDATE_INTERVAL);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [refreshData]);

  // 手动刷新后立即重置定时器
  const handleManualRefresh = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    refreshData();
    intervalRef.current = setInterval(refreshData, UPDATE_INTERVAL);
  }, [refreshData]);

  return {
    cities,
    selectedCity,
    selectedHistory,
    selectedCityId,
    setSelectedCityId,
    isRefreshing,
    refreshData: handleManualRefresh,
    lastUpdate: selectedCity.timestamp,
  };
}
