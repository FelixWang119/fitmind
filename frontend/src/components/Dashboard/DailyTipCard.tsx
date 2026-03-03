/**
 * 每日科普卡片组件
 * Story 9.2: Dashboard 科普卡片组件
 * 
 * 功能：
 * - 显示当日科普内容（标题 + 摘要）
 * - 展开/收起全文
 * - 已读/未读状态跟踪
 * - 分享功能
 */

import React, { useState, useEffect, useRef } from 'react';
import { Lightbulb, ChevronDown, ChevronUp, Share2, Check, Copy, X } from 'lucide-react';
import { getTodayTip, DailyTip } from '../../api/dailyTip';

const READ_STATUS_KEY = 'bmad_daily_tip_read_status';

/**
 * 获取已读状态
 */
function getReadStatus(tipId: number): boolean {
  try {
    const status = localStorage.getItem(READ_STATUS_KEY);
    if (status) {
      const parsed = JSON.parse(status);
      return parsed[tipId] === true;
    }
  } catch (e) {
    console.error('读取已读状态失败:', e);
  }
  return false;
}

/**
 * 设置已读状态
 */
function setReadStatus(tipId: number): void {
  try {
    const status = localStorage.getItem(READ_STATUS_KEY);
    const parsed = status ? JSON.parse(status) : {};
    parsed[tipId] = true;
    localStorage.setItem(READ_STATUS_KEY, JSON.stringify(parsed));
  } catch (e) {
    console.error('设置已读状态失败:', e);
  }
}

interface DailyTipCardProps {
  className?: string;
}

export const DailyTipCard: React.FC<DailyTipCardProps> = ({ className = '' }) => {
  const [tip, setTip] = useState<DailyTip | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState<boolean>(false);
  const [isRead, setIsRead] = useState<boolean>(false);
  const [showShareMenu, setShowShareMenu] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);
  const contentRef = useRef<HTMLDivElement>(null);

  // 加载当日科普内容
  useEffect(() => {
    const loadTip = async () => {
      try {
        setLoading(true);
        const data = await getTodayTip();
        setTip(data);
        // 检查已读状态
        const read = getReadStatus(data.id);
        setIsRead(read);
        setError(null);
      } catch (err) {
        console.error('加载科普内容失败:', err);
        setError('暂无今日科普');
      } finally {
        setLoading(false);
      }
    };

    loadTip();
  }, []);

  // 处理展开
  const handleExpand = () => {
    if (!isRead && tip) {
      setReadStatus(tip.id);
      setIsRead(true);
    }
    setIsExpanded(true);
  };

  // 处理收起
  const handleCollapse = () => {
    setIsExpanded(false);
  };

  // 处理分享
  const handleShare = async () => {
    if (!tip) return;

    // 如果支持 Web Share API
    if (navigator.share) {
      try {
        await navigator.share({
          title: tip.title,
          text: `${tip.title}\n\n${tip.summary}`,
          url: window.location.href,
        });
      } catch (err) {
        // 用户取消分享
        if ((err as Error).name !== 'AbortError') {
          console.error('分享失败:', err);
        }
      }
    } else {
      // 不支持则显示分享菜单
      setShowShareMenu(!showShareMenu);
    }
  };

  // 复制链接
  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('复制失败:', err);
    }
  };

  // 加载状态
  if (loading) {
    return (
      <div className={`bg-white rounded-xl shadow p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-green-100 p-3 rounded-full">
              <div className="h-6 w-6 bg-green-200 rounded-full" />
            </div>
            <div className="h-6 bg-gray-200 rounded w-32" />
          </div>
          <div className="h-4 bg-gray-200 rounded w-full mb-2" />
          <div className="h-4 bg-gray-200 rounded w-3/4" />
        </div>
      </div>
    );
  }

  // 错误状态
  if (error || !tip) {
    return (
      <div className={`bg-white rounded-xl shadow p-6 ${className}`}>
        <div className="flex items-center gap-3">
          <div className="bg-green-100 p-3 rounded-full">
            <Lightbulb className="h-6 w-6 text-green-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-800">💡 每日科普</h3>
            <p className="text-sm text-gray-500">{error || '暂无科普内容'}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-xl shadow p-6 ${className}`}>
      {/* 标题区域 */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="bg-green-100 p-3 rounded-full">
            <Lightbulb className="h-6 w-6 text-green-600" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-gray-800">💡 每日科普</h3>
              {/* 未读状态提示 */}
              {!isRead && (
                <span className="w-2 h-2 bg-green-500 rounded-full" title="未读" />
              )}
            </div>
            <p className="text-xs text-gray-500">{tip.topic}</p>
          </div>
        </div>
      </div>

      {/* 内容区域 */}
      <div className="mb-4">
        <h4 className="font-medium text-gray-900 mb-2">{tip.title}</h4>
        
        {/* 摘要（收起状态） */}
        {!isExpanded && (
          <p className="text-sm text-gray-600 mb-3 line-clamp-2">{tip.summary}</p>
        )}

        {/* 展开内容 */}
        {isExpanded && (
          <div 
            ref={contentRef}
            className="text-sm text-gray-600 mb-3 overflow-hidden"
            style={{
              maxHeight: '500px',
              transition: 'max-height 300ms ease-in-out',
            }}
          >
            <p className="whitespace-pre-wrap">{tip.content}</p>
            
            {/* 医学免责声明 */}
            {tip.disclaimer && (
              <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-xs text-yellow-800">
                  <strong>⚕️ 医学声明：</strong>{tip.disclaimer}
                </p>
              </div>
            )}
          </div>
        )}

        {/* 展开/收起按钮 */}
        <button
          onClick={isExpanded ? handleCollapse : handleExpand}
          className="text-sm text-green-600 hover:text-green-700 font-medium flex items-center gap-1 transition-colors"
        >
          {isExpanded ? (
            <>
              <ChevronUp className="h-4 w-4" />
              收起
            </>
          ) : (
            <>
              <ChevronDown className="h-4 w-4" />
              展开看全文
            </>
          )}
        </button>
      </div>

      {/* 底部区域 */}
      <div className="pt-4 border-t border-gray-100 flex items-center justify-between">
        <p className="text-xs text-gray-500">明天同一时间更新</p>
        
        {/* 分享按钮 */}
        <div className="relative">
          <button
            onClick={handleShare}
            className="text-gray-500 hover:text-gray-700 transition-colors"
            title="分享"
          >
            <Share2 className="h-5 w-5" />
          </button>

          {/* 分享菜单 */}
          {showShareMenu && (
            <div className="absolute right-0 bottom-full mb-2 w-40 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
              <button
                onClick={handleCopyLink}
                className="w-full px-4 py-2 text-sm text-left hover:bg-gray-50 flex items-center gap-2 rounded-t-lg"
              >
                {copied ? (
                  <>
                    <Check className="h-4 w-4 text-green-600" />
                    <span className="text-green-600">已复制</span>
                  </>
                ) : (
                  <>
                    <Copy className="h-4 w-4" />
                    复制链接
                  </>
                )}
              </button>
              <button
                onClick={() => setShowShareMenu(false)}
                className="w-full px-4 py-2 text-sm text-left hover:bg-gray-50 flex items-center gap-2 rounded-b-lg"
              >
                <X className="h-4 w-4" />
                关闭
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DailyTipCard;
