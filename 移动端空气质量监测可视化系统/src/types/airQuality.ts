export interface PollutantData {
  pm25: number;   // PM2.5 (μg/m³)
  pm10: number;   // PM10 (μg/m³)
  so2: number;    // SO2 (μg/m³)
  no2: number;    // NO2 (μg/m³)
  co: number;     // CO (mg/m³)
  o3: number;     // O3 (μg/m³)
}

export interface CityAirQuality {
  cityId: string;
  cityName: string;
  province: string;
  aqi: number;
  level: string;
  color: string;
  primaryPollutant: string;
  pollutants: PollutantData;
  timestamp: string;
  temp: number;      // 温度 (°C)
  humidity: number;  // 湿度 (%)
  windLevel: string; // 风力等级
}

export interface HistoryEntry {
  time: string;
  aqi: number;
  pm25: number;
  pm10: number;
  so2: number;
  no2: number;
  co: number;
  o3: number;
}

export interface CityHistory {
  cityId: string;
  hourly: HistoryEntry[];
}

export type AqiLevel = {
  level: string;
  color: string;
  min: number;
  max: number;
  advice: string;
};
