import React from 'react';
import { ExerciseStat } from './Cards';
import { Dumbbell, Timer, CheckCircle, ChevronRight } from 'lucide-react';

interface ExerciseData {
  total_duration_minutes: number;
  total_calories_burned: number;
  sessions_count: number;
  progress_percentage?: number;
  exercise_types?: string[];
}

interface ExerciseSectionProps {
  exerciseData: ExerciseData;
  navigate: (path: string) => void;
}

export const ExerciseSection: React.FC<ExerciseSectionProps> = ({ 
  exerciseData,
  navigate 
}) => (
  <div className="bg-white rounded-xl shadow p-6 mb-8">
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center">
        <Dumbbell className="w-6 h-6 text-orange-500 mr-3" />
        <h3 className="font-bold text-gray-800">今日运动</h3>
      </div>
      <button
        onClick={() => navigate('/exercise-checkin')}
        className="text-orange-600 hover:text-orange-700 text-sm font-medium flex items-center"
      >
        详情 <ChevronRight className="w-4 h-4 ml-1" />
      </button>
    </div>
    <div className="grid grid-cols-3 gap-4">
      <ExerciseStat
        icon={<Timer className="w-4 h-4 text-orange-500 mr-1" />}
        value={exerciseData.total_duration_minutes}
        unit="分钟"
        label="运动时长"
        infoText="所有运动打卡的时长总和"
      />
      
      <ExerciseStat
        icon={<Timer className="w-4 h-4 text-red-500 mr-1" />}
        value={exerciseData.total_calories_burned}
        unit="kcal"
        label="运动消耗"
        infoText="所有运动打卡计算的卡路里总和"
      />
      
      <ExerciseStat
        icon={<CheckCircle className="w-4 h-4 text-blue-500 mr-1" />}
        value={exerciseData.sessions_count}
        unit="次"
        label="运动次数"
        infoText="今日完成的运动打卡总次数"
      />
    </div>
    
    {exerciseData.progress_percentage !== undefined && (
      <div className="mt-4">
        <div className="flex justify-between text-xs text-gray-600 mb-1">
          <span>今日目标进度</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-full bg-gray-200 rounded-full h-2 flex-1">
            <div 
              className="bg-gradient-to-r from-orange-500 to-red-500 h-2 rounded-full transition-all"
              style={{ width: `${Math.min(exerciseData.progress_percentage, 100)}%` }}
            ></div>
          </div>
          
          {/* 进度提示按钮 */}
          <div className="relative group ml-1">
            <button className="text-gray-300 hover:text-gray-500 focus:outline-none">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>
            <div className="absolute right-0 top-full mt-2 w-48 p-3 bg-white border border-gray-200 rounded-lg shadow-lg z-10 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300">
              <p className="text-xs text-gray-600">
                <strong>目标进度来源：</strong><br/>
                当前运动量与今日运动目标的比例
              </p>
            </div>
          </div>
        </div>
      </div>
    )}
  </div>
);
