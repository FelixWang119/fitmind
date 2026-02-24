import React from 'react';
import { Dumbbell, Droplets, Flame, Calendar, ChevronRight } from 'lucide-react';

interface ActivityCardProps {
  icon: React.ReactNode;
  title: string;
  stats: Array<{
    value: number | string;
    unit: string;
    label: string;
    color: string;
  }>;
  progress?: number;
  progressLabel?: string;
  onClick: () => void;
  infoText: string;
}

export const ActivityCard: React.FC<ActivityCardProps> = ({ 
  icon, 
  title, 
  stats, 
  progress, 
  progressLabel = "进度",
  onClick,
  infoText
}) => (
  <div className="bg-white rounded-xl shadow p-5 hover:shadow-md transition-shadow">
    <div className="flex justify-between items-start mb-3">
      <div className="flex items-center">
        <div className="p-2 rounded-lg bg-gradient-to-br from-blue-50 to-indigo-100 mr-3">
          {icon}
        </div>
        <div>
          <h3 className="font-semibold text-gray-800 text-lg">{title}</h3>
        </div>
      </div>
      <button 
        onClick={onClick}
        className="text-blue-600 hover:text-blue-800 flex items-center gap-1 text-sm font-medium"
      >
        详情 <ChevronRight className="w-4 h-4" />
      </button>
    </div>
    
    <div className="mb-4">
      <div className="grid grid-cols-3 gap-2">
        {stats.map((stat, index) => (
          <div key={index} className="text-center py-2">
            <div className="flex items-center justify-center mb-1">
              <div className={`w-6 h-6 rounded-full flex items-center justify-center ${stat.color}`} />
            </div>
            <div className="text-xl font-bold text-gray-900">{stat.value}</div>
            <div className="text-xs text-gray-500 truncate">{stat.unit}</div>
            <div className="text-xs text-gray-400">{stat.label}</div>
          </div>
        ))}
      </div>
    </div>
    
    {progress !== undefined && (
      <div className="mt-2">
        <div className="flex justify-between text-xs text-gray-600 mb-1">
          <span>{progressLabel}</span>
          <span>{progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full transition-all"
            style={{ width: `${Math.min(progress, 100)}%` }}
          ></div>
        </div>
        <div className="relative ml-auto w-fit">
          <button className="text-gray-300 hover:text-gray-500 focus:outline-none text-xs -ml-3">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>
          <div className="absolute right-0 top-full mt-1 w-44 p-2 bg-white border border-gray-200 rounded-lg shadow-lg z-10 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300">
            <p className="text-xs text-gray-600">{infoText}</p>
          </div>
        </div>
      </div>
    )}
  </div>
);
