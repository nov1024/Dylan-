import { useState, useRef, useEffect } from 'react';
import { ChevronDown, MapPin, Search } from 'lucide-react';
import type { CityAirQuality } from '@/types/airQuality';

interface CitySelectorProps {
  cities: CityAirQuality[];
  selectedCityId: string;
  onSelect: (cityId: string) => void;
}

export default function CitySelector({ cities, selectedCityId, onSelect }: CitySelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);
  const selectedCity = cities.find(c => c.cityId === selectedCityId);

  const filteredCities = cities.filter(c =>
    c.cityName.includes(searchQuery) || c.province.includes(searchQuery)
  );

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div ref={containerRef} className="relative z-50">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 bg-white/90 backdrop-blur-sm border border-gray-200 rounded-full px-4 py-2 shadow-sm active:scale-95 transition-transform"
      >
        <MapPin className="w-4 h-4 text-blue-500" />
        <span className="text-sm font-bold text-gray-900">
          {selectedCity?.cityName || '选择城市'}
        </span>
        <span
          className="w-2 h-2 rounded-full"
          style={{ backgroundColor: selectedCity?.color || '#ccc' }}
        />
        <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute top-full mt-2 left-0 right-0 bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
          <div className="p-2 border-b border-gray-100">
            <div className="flex items-center gap-2 bg-gray-50 rounded-xl px-3 py-2">
              <Search className="w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="搜索城市..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 bg-transparent text-sm outline-none placeholder:text-gray-400"
                autoFocus
              />
            </div>
          </div>
          <div className="max-h-[280px] overflow-y-auto">
            {filteredCities.map(city => (
              <button
                key={city.cityId}
                onClick={() => {
                  onSelect(city.cityId);
                  setIsOpen(false);
                  setSearchQuery('');
                }}
                className={`w-full flex items-center justify-between px-4 py-3 hover:bg-blue-50 transition-colors ${
                  city.cityId === selectedCityId ? 'bg-blue-50' : ''
                }`}
              >
                <div className="flex items-center gap-3">
                  <MapPin className="w-4 h-4 text-gray-400" />
                  <div className="text-left">
                    <div className="text-sm font-medium text-gray-900">{city.cityName}</div>
                    <div className="text-xs text-gray-400">{city.province}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold" style={{ color: city.color }}>{city.aqi}</span>
                  <span
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: city.color }}
                  />
                </div>
              </button>
            ))}
            {filteredCities.length === 0 && (
              <div className="px-4 py-6 text-center text-sm text-gray-400">
                未找到匹配的城市
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
