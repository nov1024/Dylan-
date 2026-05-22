import { useMemo } from 'react';
import ReactEChartsCore from 'echarts-for-react/lib/core';
import * as echarts from 'echarts/core';
import { LineChart } from 'echarts/charts';
import { CanvasRenderer } from 'echarts/renderers';
import { TooltipComponent, GridComponent, LegendComponent, DataZoomComponent } from 'echarts/components';
import type { HistoryEntry } from '@/types/airQuality';

echarts.use([LineChart, CanvasRenderer, TooltipComponent, GridComponent, LegendComponent, DataZoomComponent]);

interface TrendChartProps {
  data: HistoryEntry[];
  pollutants?: string[];
}

const POLLUTANT_COLORS: Record<string, string> = {
  aqi: '#333',
  pm25: '#ff6b6b',
  pm10: '#4ecdc4',
  so2: '#45b7d1',
  no2: '#96ceb4',
  co: '#ffeaa7',
  o3: '#dfe6e9',
};

const POLLUTANT_NAMES: Record<string, string> = {
  aqi: 'AQI',
  pm25: 'PM2.5',
  pm10: 'PM10',
  so2: 'SO2',
  no2: 'NO2',
  co: 'CO',
  o3: 'O3',
};

export default function TrendChart({ data, pollutants = ['aqi', 'pm25', 'pm10'] }: TrendChartProps) {
  const option = useMemo(() => {
    const times = data.map(d => d.time);
    const series = pollutants.map(key => ({
      name: POLLUTANT_NAMES[key] || key,
      type: 'line' as const,
      smooth: true,
      symbol: 'circle',
      symbolSize: 4,
      lineStyle: { width: 2 },
      itemStyle: { color: POLLUTANT_COLORS[key] || '#333' },
      areaStyle: key === 'aqi' ? {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(51,51,51,0.15)' },
          { offset: 1, color: 'rgba(51,51,51,0.01)' },
        ]),
      } : undefined,
      data: data.map(d => d[key as keyof HistoryEntry] as number),
      animationDuration: 800,
    }));

    return {
      grid: {
        top: 35,
        right: 10,
        bottom: 35,
        left: 5,
        containLabel: true,
      },
      legend: {
        top: 5,
        itemWidth: 15,
        itemHeight: 8,
        textStyle: { fontSize: 10 },
      },
      tooltip: {
        trigger: 'axis' as const,
        backgroundColor: 'rgba(255,255,255,0.95)',
        borderColor: '#eee',
        borderWidth: 1,
        textStyle: { fontSize: 11, color: '#333' },
        axisPointer: {
          type: 'cross' as const,
          crossStyle: { color: '#999' },
        },
      },
      xAxis: {
        type: 'category' as const,
        boundaryGap: false,
        data: times,
        axisLabel: {
          fontSize: 9,
          color: '#888',
          interval: 4,
        },
        axisLine: { lineStyle: { color: '#eee' } },
      },
      yAxis: {
        type: 'value' as const,
        axisLabel: {
          fontSize: 9,
          color: '#888',
        },
        splitLine: { lineStyle: { color: '#f0f0f0' } },
      },
      dataZoom: [
        {
          type: 'inside' as const,
          start: 0,
          end: 100,
        },
      ],
      series,
    };
  }, [data, pollutants]);

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-2">
      <div className="px-2 pt-2">
        <h3 className="text-sm font-bold text-gray-900">24小时变化趋势</h3>
        <p className="text-xs text-gray-400 mt-0.5">支持手势缩放查看</p>
      </div>
      <ReactEChartsCore
        echarts={echarts}
        option={option}
        style={{ height: '220px', width: '100%' }}
        opts={{ renderer: 'canvas' }}
      />
    </div>
  );
}
