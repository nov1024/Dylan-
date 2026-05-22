import { useMemo } from 'react';
import ReactEChartsCore from 'echarts-for-react/lib/core';
import * as echarts from 'echarts/core';
import { GaugeChart } from 'echarts/charts';
import { CanvasRenderer } from 'echarts/renderers';
import { TooltipComponent, TitleComponent } from 'echarts/components';

echarts.use([GaugeChart, CanvasRenderer, TooltipComponent, TitleComponent]);

interface AqiGaugeProps {
  aqi: number;
  cityName: string;
  level: string;
  color: string;
}

export default function AqiGauge({ aqi, cityName, level, color }: AqiGaugeProps) {
  const option = useMemo(() => ({
    series: [
      {
        type: 'gauge',
        startAngle: 210,
        endAngle: -30,
        min: 0,
        max: 300,
        splitNumber: 6,
        radius: '92%',
        center: ['50%', '55%'],
        itemStyle: { color },
        progress: {
          show: true,
          width: 16,
          roundCap: true,
        },
        pointer: {
          show: true,
          length: '60%',
          width: 5,
          itemStyle: { color: '#333' },
        },
        axisLine: {
          roundCap: true,
          lineStyle: {
            width: 16,
            color: [
              [0.167, '#00e400'],
              [0.333, '#ffff00'],
              [0.5, '#ff7e00'],
              [0.667, '#ff0000'],
              [0.833, '#99004c'],
              [1, '#7e0023'],
            ],
          },
        },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: {
          distance: 20,
          fontSize: 9,
          color: '#666',
        },
        title: {
          offsetCenter: [0, '28%'],
          fontSize: 13,
          color: '#333',
          fontWeight: 'bold' as const,
        },
        detail: {
          valueAnimation: true,
          offsetCenter: [0, '-5%'],
          fontSize: 36,
          fontWeight: 'bold' as const,
          formatter: '{value}',
          color: '#1a1a1a',
        },
        data: [
          {
            value: aqi,
            name: level,
          },
        ],
        animationDuration: 1000,
        animationEasing: 'cubicOut' as const,
      },
    ],
    title: {
      text: `${cityName} · AQI`,
      left: 'center',
      top: 5,
      textStyle: {
        fontSize: 15,
        fontWeight: 'bold',
        color: '#1a1a1a',
      },
    },
    tooltip: {
      trigger: 'item' as const,
      formatter: `{b}: {c}<br/>更新时间: ${new Date().toLocaleTimeString()}`,
    },
  }), [aqi, cityName, level, color]);

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-2">
      <ReactEChartsCore
        echarts={echarts}
        option={option}
        style={{ height: '200px', width: '100%' }}
        opts={{ renderer: 'canvas' }}
      />
    </div>
  );
}
