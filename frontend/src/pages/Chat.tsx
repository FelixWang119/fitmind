import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, X } from 'lucide-react';
import { api } from '../api/client';

interface Message {
  id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

interface RoleInfo {
  id: string;
  name: string;
  emoji: string;
  color: string;
  description: string;
}

const ROLES: RoleInfo[] = [
  {
    id: 'nutritionist',
    name: '营养师',
    emoji: '🥗',
    color: 'bg-green-100 text-green-700 border-green-200',
    description: '饮食分析、食谱推荐、营养计算'
  },
  {
    id: 'behavior_coach',
    name: '行为教练',
    emoji: '🏃',
    color: 'bg-blue-100 text-blue-700 border-blue-200',
    description: '习惯养成、目标设定、动力激励'
  },
  {
    id: 'emotional_companion',
    name: '情感陪伴',
    emoji: '💬',
    color: 'bg-purple-100 text-purple-700 border-purple-200',
    description: '情绪支持、倾听陪伴、心理疏导'
  }
];

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 0,
      role: 'assistant',
      content: '你好！我是你的体重管理AI助手。我可以帮助你制定健康的饮食计划、跟踪你的进度，并提供情感支持。\n\n我可以自动根据你的话题切换角色，你也可以点击下方的按钮手动选择模式。今天有什么我可以帮你的吗？',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentRole, setCurrentRole] = useState<string>('general');
  const [roleSwitched, setRoleSwitched] = useState(false);
  const [previousRole, setPreviousRole] = useState<string | null>(null);
  const [isFusion, setIsFusion] = useState(false);
  const [notification, setNotification] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<number | undefined>(undefined);
  const [manualMode, setManualMode] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Clear notification after 3 seconds
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => {
        setNotification(null);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now(),
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput('');
    setLoading(true);

    try {
      const response = await api.sendChatMessage(
        input,
        conversationId,
        manualMode ? currentRole : undefined
      );

      // Update conversation ID if new
      if (!conversationId && response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      // Handle role switching
      if (response.role_switched) {
        setRoleSwitched(true);
        setPreviousRole(response.previous_role);
        setCurrentRole(response.current_role);
        
        if (response.is_fusion) {
          setIsFusion(true);
        } else {
          setIsFusion(false);
        }

        // Show notification
        if (response.notification) {
          setNotification(response.notification);
        }
      }

      // Check if manual mode was triggered
      if (response.current_role && !manualMode) {
        // Auto mode - role was switched automatically
      }

      // Add AI response
      const aiMessage: Message = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString(),
      };

      setMessages([...updatedMessages, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);

      const errorMessage: Message = {
        id: Date.now() + 1,
        role: 'assistant',
        content: '抱歉，我在处理您的消息时遇到了问题。请稍后再试。',
      };

      setMessages([...updatedMessages, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleRoleSwitch = async (roleId: string) => {
    if (roleId === currentRole && !manualMode) return;

    setManualMode(true);
    setCurrentRole(roleId);
    setIsFusion(false);

    // If we have an active conversation, switch role on backend
    if (conversationId) {
      try {
        await api.switchRole(conversationId, roleId);
        setNotification(`已切换到${ROLES.find(r => r.id === roleId)?.name}模式`);
      } catch (error) {
        console.error('Error switching role:', error);
      }
    } else {
      setNotification(`已切换到${ROLES.find(r => r.id === roleId)?.name}模式`);
    }
  };

  const getCurrentRoleInfo = () => {
    return ROLES.find(r => r.id === currentRole) || {
      id: 'general',
      name: 'AI助手',
      emoji: '🤖',
      color: 'bg-gray-100 text-gray-700 border-gray-200',
      description: '综合助手'
    };
  };

  const currentRoleInfo = getCurrentRoleInfo();

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
      {/* Role Notification Toast */}
      {notification && (
        <div className="fixed top-20 left-1/2 transform -translate-x-1/2 z-50 animate-fade-in">
          <div className="bg-gray-900 text-white px-4 py-2 rounded-full shadow-lg flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-yellow-400" />
            <span className="text-sm">{notification}</span>
          </div>
        </div>
      )}

      {/* Header with Role Badge */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <span>AI健康助手</span>
              {isFusion && (
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gradient-to-r from-green-500 to-blue-500 text-white">
                  综合分析
                </span>
              )}
            </h1>
            <p className="text-sm text-gray-500 flex items-center space-x-1">
              <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${currentRoleInfo.color}`}>
                {currentRoleInfo.emoji} {currentRoleInfo.name}
              </span>
              {roleSwitched && previousRole && (
                <span className="text-xs text-gray-400 ml-1">
                  (从{ROLES.find(r => r.id === previousRole)?.name}切换)
                </span>
              )}
            </p>
          </div>
        </div>
      </div>

      {/* Role Selector Buttons */}
      <div className="px-4 py-2 border-b border-gray-100 bg-gray-50">
        <div className="flex items-center space-x-2">
          <span className="text-xs text-gray-500 mr-1">选择模式:</span>
          {ROLES.map((role) => (
            <button
              key={role.id}
              onClick={() => handleRoleSwitch(role.id)}
              disabled={loading}
              className={`flex items-center space-x-1 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                currentRole === role.id
                  ? `${role.color} ring-2 ring-offset-1`
                  : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-100'
              } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <span>{role.emoji}</span>
              <span>{role.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex items-start space-x-3 ${
              message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
            }`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : currentRoleInfo.color
              }`}
            >
              {message.role === 'user' ? (
                <User className="w-4 h-4" />
              ) : (
                <Bot className="w-4 h-4" />
              )}
            </div>
            
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              {message.timestamp && (
                <p className={`text-xs mt-1 ${message.role === 'user' ? 'text-blue-200' : 'text-gray-400'}`}>
                  {new Date(message.timestamp).toLocaleTimeString()}
                </p>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex items-start space-x-3">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${currentRoleInfo.color}`}>
              <Bot className="w-4 h-4" />
            </div>
            
            <div className="max-w-[80%] rounded-2xl px-4 py-2 bg-gray-100 text-gray-900">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !loading && handleSend()}
            placeholder={loading ? "AI正在回复..." : "输入你的问题... (说'切换到XX模式'可改变角色)"}
            disabled={loading}
            className={`flex-1 px-4 py-2 border rounded-xl focus:ring-2 focus:outline-none ${
              loading 
                ? 'border-gray-200 bg-gray-100 text-gray-500 cursor-not-allowed' 
                : 'border-gray-200 focus:border-blue-500 focus:ring-blue-200'
            }`}
          />
          <button
            onClick={handleSend}
            disabled={loading}
            className={`p-2 rounded-xl transition-colors ${
              loading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <div className="mt-2 text-xs text-gray-400 text-center">
          试试说："我心情不好" 或 "怎么健康减肥" 或 "想运动但坚持不了"
        </div>
      </div>
    </div>
  );
}

export default Chat;
