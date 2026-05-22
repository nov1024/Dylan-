import { useMemo } from 'react';
import ReactEChartsCore from 'echarts-for-react/lib/core';
import * as echarts from 'echarts/core';
import { BarChart } from 'echarts/charts';
import { CanvasRenderer } from 'echarts/renderers';
import { TooltipComponent, GridComponent } from 'echarts/components';
import type { PollutantData } from '@/types/airQuality';

echarts.use([BarChart, CanvasRenderer, TooltipComponent, GridComponent]);

interface PollutantBarProps {
  pollutants: PollutantData;
}

export default function PollutantBar({ pollutants }: PollutantBarProps) {
  const option = useMemo(() => {
    const data = [
      { name: 'PM2.5', value: pollutants.pm25, unit: 'μg/m³', limit: 75 },
      { name: 'PM10', value: pollutants.pm10, unit: 'μg/m³', limit: 150 },
      { name: 'SO2', value: pollutants.so2, unit: 'μg/m³', limit: 150 },
      { name: 'NO2', value: pollutants.no2, unit: 'μg/m³', limit: 100 },
      { name: 'CO', value: pollutants.co, unit: 'mg/m³', limit: 10 },
      { name: 'O3', value: pollutants.o3, unit: 'μg/m³', limit: 160 },
    ];

    return {
      grid: {
        top: 15,
        right: 55,
        bottom: 25,
        left: 5,
        containLabel: true,
      },
      tooltip: {
        trigger: 'axis' as const,
        axisPointer: { type: 'shadow' as const },
        formatter: (params: Array<{ name: string; value: number; data: { unit: string; limit: number } }>) => {
          const p = params[0];
          const ratio = ((p.value / p.data.limit) * 100).toFixed(1);
          return `${p.name}: ${p.value} ${p.data.unit}<br/>标准限值: ${p.data.limit} ${p.data.unit}<br/>占标率: ${ratio}%`;
        },
      },
      xAxis: {
        type: 'category' as const,
        data: data.map(d => d.name),
        axisLabel: {
          fontSize: 10,
          color: '#555',
        },
        axisLine: { lineStyle: { color: '#eee' } },
        axisTick: { show: false },
      },
      yAxis: {
        type: 'value' as const,
        axisLabel: { show: false },
        splitLine: { show: false },
      },
      series: [
        {
          type: 'bar',
          barWidth: '55%',
          data: data.map(d => ({
            value: d.value,
            unit: d.unit,
            limit: d.limit,
            itemStyle: {
              color: d.value > d.limit
                ? '#e74c3c'
                : new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: '#4285f4' },
                    { offset: 1, color: '#34a853' },
                  ]),
              borderRadius: [6, 6, 0, 0],
            },
          })),
          label: {
            show: true,
            position: 'right' as const,
            fontSize: 10,
            color: '#555',
            formatter: (p: { value: number; data: { unit: string } }) => `${p.value} ${p.data.unit}`,
          },
          animationDuration: 800,
          animationEasing: 'cubicOut' as const,
        },
      ],
    };
  }, [pollutants]);

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-2">
      <div className="px-2 pt-2">
        <h3 className="text-sm font-bold text-gray-900">各污染物浓度</h3>
        <p className="text-xs text-gray-400 mt-0.5">红色表示超标</p>
      </div>
      <ReactEChartsCore
        echarts={echarts}
        option={option}
        style={{ height: '200px', width: '100%' }}
        opts={{ renderer: 'canvas' }}
      />
    </div>
  );
}
