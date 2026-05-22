import { useMemo } from 'react';
import ReactEChartsCore from 'echarts-for-react/lib/core';
import * as echarts from 'echarts/core';
import { BarChart } from 'echarts/charts';
import { CanvasRenderer } from 'echarts/renderers';
import { TooltipComponent, GridComponent } from 'echarts/components';
import type { CityAirQuality } from '@/types/airQuality';

echarts.use([BarChart, CanvasRenderer, TooltipComponent, GridComponent]);

interface CityRankingProps {
  cities: CityAirQuality[];
  selectedCityId: string;
  onSelect: (cityId: string) => void;
}

export default function CityRanking({ cities, selectedCityId, onSelect }: CityRankingProps) {
  const sorted = useMemo(() => {
    return [...cities].sort((a, b) => a.aqi - b.aqi);
  }, [cities]);

  const option = useMemo(() => {
    return {
      grid: {
        top: 10,
        right: 50,
        bottom: 10,
        left: 5,
        containLabel: true,
      },
      tooltip: {
        trigger: 'axis' as const,
        axisPointer: { type: 'shadow' as const },
        formatter: (params: Array<{ name: string; value: number; marker: string; data: { city: CityAirQuality } }>) => {
          const c = params[0].data.city;
          return `${params[0].marker} <strong>${c.cityName}</strong><br/>AQI: ${c.aqi} (${c.level})<br/>首要污染物: ${c.primaryPollutant}`;
        },
      },
      xAxis: {
        type: 'value' as const,
        max: 350,
        axisLabel: {
          fontSize: 9,
          color: '#888',
        },
        splitLine: { lineStyle: { color: '#f0f0f0' } },
      },
      yAxis: {
        type: 'category' as const,
        data: sorted.map(c => c.cityName).reverse(),
        axisLabel: {
          fontSize: 11,
          color: '#333',
        },
        axisLine: { show: false },
        axisTick: { show: false },
      },
      series: [
        {
          type: 'bar',
          barWidth: '55%',
          data: sorted.map(c => ({
            value: c.aqi,
            city: c,
            itemStyle: {
              color: c.cityId === selectedCityId
                ? '#4285f4'
                : c.color,
              borderRadius: [0, 6, 6, 0],
              opacity: c.cityId === selectedCityId ? 1 : 0.8,
            },
          })).reverse(),
          label: {
            show: true,
            position: 'right' as const,
            fontSize: 10,
            color: '#555',
            formatter: '{c}',
          },
          animationDuration: 800,
          animationEasing: 'cubicOut' as const,
        },
      ],
    };
  }, [sorted, selectedCityId]);

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-2">
      <div className="px-2 pt-2">
        <h3 className="text-sm font-bold text-gray-900">城市空气质量排名</h3>
        <p className="text-xs text-gray-400 mt-0.5">AQI由低到高（优→差）</p>
      </div>
      <ReactEChartsCore
        echarts={echarts}
        option={option}
        style={{ height: '280px', width: '100%' }}
        opts={{ renderer: 'canvas' }}
        onEvents={{
          click: (params: { data: { city: CityAirQuality } }) => {
            if (params?.data?.city) {
              onSelect(params.data.city.cityId);
            }
          },
        }}
      />
    </div>
  );
}
