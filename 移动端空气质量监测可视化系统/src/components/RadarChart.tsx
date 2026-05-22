import { useMemo } from 'react';
import ReactEChartsCore from 'echarts-for-react/lib/core';
import * as echarts from 'echarts/core';
import { RadarChart } from 'echarts/charts';
import { CanvasRenderer } from 'echarts/renderers';
import { TooltipComponent, LegendComponent } from 'echarts/components';
import type { PollutantData } from '@/types/airQuality';

echarts.use([RadarChart, CanvasRenderer, TooltipComponent, LegendComponent]);

interface RadarChartProps {
  pollutants: PollutantData;
  cityName: string;
}

// 污染物标准限值（用于归一化）
const LIMITS: Record<string, number> = {
  PM25: 75,   // μg/m³
  PM10: 150,  // μg/m³
  SO2: 150,   // μg/m³
  NO2: 100,   // μg/m³
  CO: 10,     // mg/m³
  O3: 160,    // μg/m³
};

export default function RadarChartComponent({ pollutants, cityName }: RadarChartProps) {
  const option = useMemo(() => {
    const values = [
      Math.min(100, (pollutants.pm25 / LIMITS.PM25) * 100),
      Math.min(100, (pollutants.pm10 / LIMITS.PM10) * 100),
      Math.min(100, (pollutants.so2 / LIMITS.SO2) * 100),
      Math.min(100, (pollutants.no2 / LIMITS.NO2) * 100),
      Math.min(100, (pollutants.co / LIMITS.CO) * 100),
      Math.min(100, (pollutants.o3 / LIMITS.O3) * 100),
    ];

    return {
      title: {
        text: '污染物综合指标',
        left: 'center',
        top: 5,
        textStyle: { fontSize: 14, fontWeight: 'bold', color: '#1a1a1a' },
      },
      tooltip: {
        trigger: 'item' as const,
        formatter: () => {
          return `
            <div style="font-weight:bold;margin-bottom:4px">${cityName}</div>
            <div>PM2.5: ${pollutants.pm25} μg/m³</div>
            <div>PM10: ${pollutants.pm10} μg/m³</div>
            <div>SO2: ${pollutants.so2} μg/m³</div>
            <div>NO2: ${pollutants.no2} μg/m³</div>
            <div>CO: ${pollutants.co} mg/m³</div>
            <div>O3: ${pollutants.o3} μg/m³</div>
          `;
        },
      },
      radar: {
        indicator: [
          { name: 'PM2.5', max: 100 },
          { name: 'PM10', max: 100 },
          { name: 'SO2', max: 100 },
          { name: 'NO2', max: 100 },
          { name: 'CO', max: 100 },
          { name: 'O3', max: 100 },
        ],
        shape: 'polygon' as const,
        splitNumber: 4,
        axisName: {
          color: '#555',
          fontSize: 10,
        },
        splitLine: { lineStyle: { color: '#eee' } },
        splitArea: {
          areaStyle: {
            color: ['#f8f9fa', '#f1f3f4', '#e8eaed', '#dadce0'].reverse(),
          },
        },
        axisLine: { lineStyle: { color: '#ddd' } },
      },
      series: [
        {
          type: 'radar' as const,
          data: [
            {
              value: values,
              name: cityName,
              areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
                  { offset: 0, color: 'rgba(66, 133, 244, 0.4)' },
                  { offset: 1, color: 'rgba(66, 133, 244, 0.1)' },
                ]),
              },
              lineStyle: { color: '#4285f4', width: 2 },
              itemStyle: { color: '#4285f4' },
            },
          ],
          animationDuration: 1000,
        },
      ],
    };
  }, [pollutants, cityName]);

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-2">
      <ReactEChartsCore
        echarts={echarts}
        option={option}
        style={{ height: '220px', width: '100%' }}
        opts={{ renderer: 'canvas' }}
      />
    </div>
  );
}
