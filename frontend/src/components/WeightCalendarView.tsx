import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon } from 'lucide-react';

const WeightCalendarView = ({ onDayClick }) => {
  const [currentDate, setCurrentDate] = useState(new Date());
  
  // Mock weight data for calendar
  const mockWeightData = {
    '2026-03-01': 70.6,
    '2026-03-02': 70.5,
    '2026-03-03': null, // No entry
    '2026-03-04': 70.4,
    '2026-03-05': 70.3,
    '2026-03-06': null,
    '2026-03-07': 70.2,
    '2026-02-28': 70.7,
    '2026-02-27': 70.8,
    // Add more sample data
    '2026-02-26': 70.9,
    '2026-02-25': 71.0,
    '2026-02-24': 71.1,
    '2026-02-23': 71.2,
    '2026-02-22': 71.3,
  };

  // Navigation functions
  const prevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  // Get calendar data for current month
  const getCalendarDays = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    // First day of month
    const firstDay = new Date(year, month, 1);
    // Last day of month
    const lastDay = new Date(year, month + 1, 0);
    // Starting day (Sunday)
    const startDay = firstDay.getDay();
    // Number of days in month
    const daysInMonth = lastDay.getDate();
    
    const days = [];
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startDay; i++) {
      days.push(null);
    }
    
    // Add cells for each day of the month
    for (let i = 1; i <= daysInMonth; i++) {
      const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
      days.push({
        date: i,
        dateStr,
        weight: mockWeightData[dateStr] || null
      });
    }
    
    return days;
  };

  const calendarDays = getCalendarDays();
  const monthNames = [
    "一月", "二月", "三月", "四月", "五月", "六月",
    "七月", "八月", "九月", "十月", "十一月", "十二月"
  ];

  const getDayClass = (day) => {
    if (!day) return '';
    
    const today = new Date();
    const isToday = day.dateStr === `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
    
    let classes = 'h-20 w-20 flex flex-col items-center justify-center rounded-lg border ';
    
    if (day.weight) {
      // Color coding based on weight change, or just indicate entry availability
      classes += 'bg-blue-50 border-blue-200 hover:bg-blue-100 cursor-pointer ';
    } else {
      classes += 'bg-gray-50 border-gray-200 text-gray-400 ';
    }
    
    if (isToday) {
      classes += 'ring-2 ring-blue-500 ';
    }
    
    return classes;
  };

  return (
    <div className="bg-white rounded-xl shadow p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
          <CalendarIcon className="w-5 h-5" />
          减重日历
        </h2>
        <div className="flex items-center gap-2">
          <button
            onClick={prevMonth}
            className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50"
          >
            <ChevronLeft className="w-4 h-4 text-gray-600" />
          </button>
          <span className="text-lg font-medium text-gray-900">
            {currentDate.getFullYear()}年 {monthNames[currentDate.getMonth()]}
          </span>
          <button
            onClick={nextMonth}
            className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50"
          >
            <ChevronRight className="w-4 h-4 text-gray-600" />
          </button>
        </div>
      </div>
      
      {/* Calendar grid */}
      <div className="grid grid-cols-7 gap-2 mb-2">
        {['日', '一', '二', '三', '四', '五', '六'].map((day) => (
          <div key={day} className="text-center text-sm font-medium text-gray-500 py-2">
            {day}
          </div>
        ))}
      </div>
      
      <div className="grid grid-cols-7 gap-2">
        {calendarDays.map((day, index) => {
          if (!day) {
            return <div key={`empty-${index}`} className="h-20 w-20"></div>;
          }
          
          return (
            <div 
              key={day.dateStr}
              className={getDayClass(day)}
              onClick={() => onDayClick && onDayClick(day)}
            >
              <span className="text-sm font-medium text-gray-700">{day.date}</span>
              {day.weight !== null ? (
                <div className="text-xs mt-1">
                  <span className="font-bold" style={{ color: '#3B82F6' }}>
                    {day.weight}
                  </span>
                  <span className="text-gray-500">kg</span>
                </div>
              ) : (
                <div className="text-xs text-gray-400">—</div>
              )}
            </div>
          );
        })}
      </div>
      
      {/* Calendar info */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
            <span className="text-gray-600">已记录</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-gray-200"></div>
            <span className="text-gray-600">未记录</span>
          </div>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          点击日期查看详情 • 绿色圆点表示有健身或饮食记录
        </p>
      </div>
    </div>
  );
};

export default WeightCalendarView;