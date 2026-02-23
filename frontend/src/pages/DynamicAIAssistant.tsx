import { useState } from 'react';
import { Send, BrainCircuit, User, Stethoscope, Target, Heart, Sparkles } from 'lucide-react';
import { api } from '../api/client'; // Import API client

export function DynamicAIAssistant() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      current_role: 'general',
      content: '你好！我是我的全能健康AI助手。我可以作为营养师、行为教练或情感陪伴为你服务。告诉我你需要哪方面的帮助，我会自动切换到最适合的角色！',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentRole, setCurrentRole] = useState('general');
  const [autoMode, setAutoMode] = useState(true); // Auto role switching mode

  // Map role to icon  
  const getRoleIcon = (role: string) => {
    switch(role) {
      case 'nutritionist':
        return Stethoscope;
      case 'behavior_coach':
        return Target;
      case 'emotional_support':
        return Heart;
      case 'general':
      default:
        return BrainCircuit;
    }
  };

  const getRoleColor = (role: string) => {
    switch(role) {
      case 'nutritionist':
        return 'text-green-600';
      case 'behavior_coach':
        return 'text-purple-600';
      case 'emotional_support':
        return 'text-pink-500';
      case 'general':
      default:
        return 'text-blue-600';
    }
  };
  
  const getRoleName = (role: string) => {
    switch(role) {
      case 'nutritionist': return '营养师';
      case 'behavior_coach': return '行为教练';
      case 'emotional_support': return '情感陪伴';
      default: return '通用助手';
    }
  };
  
  // Manual role switch
  const handleManualRoleSwitch = (role: string) => {
    setCurrentRole(role);
    setAutoMode(false);
    setMessages(prev => [...prev, {
      id: Date.now(),
      role: 'assistant',
      current_role: role,
      content: `好的，我现在是您的${getRoleName(role)}。请告诉我您需要什么帮助？`
    }]);
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const newMessage = {
      id: Date.now(),
      role: 'user',
      content: input,
    };

    const updatedMessages = [...messages, newMessage];
    setMessages(updatedMessages);
    setInput('');
    setLoading(true);

    try {
      // Send to the main AI chat endpoint which handles role switching
      const aiResponse = await api.sendMessage(input, {
        current_role: autoMode ? undefined : currentRole // Use manual role if not in auto mode
      });
      
      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: aiResponse.response,
        current_role: aiResponse.current_role || currentRole
      };
      
      setMessages([...updatedMessages, aiMessage]);
      if (autoMode) {
        setCurrentRole(aiResponse.current_role || 'general');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        current_role: currentRole,
        content: '抱歉，我在处理你的消息时遇到了问题。我会继续为你提供帮助，请再试一次。',
      };
      
      setMessages([...updatedMessages, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl shadow-sm border border-blue-100">
      <div className="p-4 border-b border-blue-100 bg-gradient-to-r from-blue-100 to-indigo-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className={`p-1 rounded-md mr-2 ${currentRole === 'nutritionist' ? 'bg-green-100' : currentRole === 'behavior_coach' ? 'bg-purple-100' : currentRole === 'emotional_support' ? 'bg-pink-100' : 'bg-blue-100'}`}>
              {getRoleIcon(currentRole)({ className: `w-6 h-6 ${getRoleColor(currentRole)}` })}
            </div>
            <h1 className="text-lg font-semibold text-gray-900">智能健康助手</h1>
            <span className={`ml-2 text-xs px-2 py-1 rounded-full ${autoMode ? 'bg-blue-200 text-blue-800' : 'bg-amber-200 text-amber-800'}`}>
              {autoMode ? '自动角色切换' : `手动：${getRoleName(currentRole)}`}
            </span>
          </div>
          
          {/* Mode Toggle */}
          <button
            onClick={() => setAutoMode(!autoMode)}
            className="text-xs px-3 py-1 rounded-full bg-white border border-blue-200 hover:bg-blue-50 transition-colors flex items-center gap-1"
          >
            <Sparkles className="w-3 h-3" />
            {autoMode ? '切换手动模式' : '切换自动模式'}
          </button>
        </div>
        
        {/* Manual Role Buttons (only in manual mode) */}
        {!autoMode && (
          <div className="flex gap-2 mt-3 pl-8">
            <button
              onClick={() => handleManualRoleSwitch('nutritionist')}
              className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${currentRole === 'nutritionist' ? 'bg-green-500 text-white border-green-500' : 'bg-white text-green-600 border-green-200 hover:bg-green-50'}`}
            >
              <Stethoscope className="w-3 h-3 inline mr-1" />
              营养师
            </button>
            <button
              onClick={() => handleManualRoleSwitch('behavior_coach')}
              className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${currentRole === 'behavior_coach' ? 'bg-purple-500 text-white border-purple-500' : 'bg-white text-purple-600 border-purple-200 hover:bg-purple-50'}`}
            >
              <Target className="w-3 h-3 inline mr-1" />
              行为教练
            </button>
            <button
              onClick={() => handleManualRoleSwitch('emotional_support')}
              className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${currentRole === 'emotional_support' ? 'bg-pink-500 text-white border-pink-500' : 'bg-white text-pink-600 border-pink-200 hover:bg-pink-50'}`}
            >
              <Heart className="w-3 h-3 inline mr-1" />
              情感陪伴
            </button>
          </div>
        )}
        
        {!autoMode && (
          <p className="text-xs text-gray-500 pl-8 mt-2">💡 已切换到手动模式，点击上方按钮选择角色</p>
        )}
        {autoMode && (
          <p className="text-sm text-gray-500 pl-8 mt-2">基于对话内容智能切换角色</p>
        )}
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => {
          const RoleIcon = message.current_role ? getRoleIcon(message.current_role) : BrainCircuit;
          const roleColor = message.current_role ? getRoleColor(message.current_role) : 'text-blue-600';
          
          return (
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
                    : `${message.current_role === 'nutritionist' ? 'bg-green-100' : message.current_role === 'behavior_coach' ? 'bg-purple-100' : message.current_role === 'emotional_support' ? 'bg-gradient-to-r from-pink-100 to-purple-100' : 'bg-blue-100'}`
                }`}
              >
                {message.role === 'user' ? <User className="w-4 h-4" /> : <RoleIcon className={`w-4 h-4 ${roleColor}`} />}
              </div>
              
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : `${message.current_role === 'nutritionist' ? 'bg-green-50 border border-green-100' : message.current_role === 'behavior_coach' ? 'bg-purple-50 border border-purple-100' : message.current_role === 'emotional_support' ? 'bg-gradient-to-r from-pink-50 to-purple-50 border border-pink-100' : 'bg-white border border-blue-100' }`
                }`}
              >
                <p className="text-sm">{message.content}</p>
                {message.current_role && (
                  <p className="text-xs opacity-70 mt-1">
                    角色：{getRoleName(message.current_role)}
                  </p>
                )}
              </div>
            </div>
          );
        })}
        {loading && (
          <div className="flex items-start space-x-3">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${currentRole === 'nutritionist' ? 'bg-green-100' : currentRole === 'behavior_coach' ? 'bg-purple-100' : currentRole === 'emotional_support' ? 'bg-gradient-to-r from-pink-100 to-purple-100' : 'bg-blue-100'}`}>
              {getRoleIcon(currentRole)({ className: `w-4 h-4 ${getRoleColor(currentRole)}` })}
            </div>
            
            <div className={`max-w-[80%] rounded-2xl px-4 py-2 ${currentRole === 'nutritionist' ? 'bg-green-50 border border-green-100' : currentRole === 'behavior_coach' ? 'bg-purple-50 border border-purple-100' : currentRole === 'emotional_support' ? 'bg-gradient-to-r from-pink-50 to-purple-50 border border-pink-100' : 'bg-white border border-blue-100'}`}>
              <p className="text-sm">AI正在分析你的需求并切换到最适合的角色...</p>
            </div>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-blue-100 bg-gradient-to-r from-blue-50 to-indigo-50">
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !loading && handleSend()}
            placeholder={loading ? "AI思考中..." : "询问营养、运动、情绪，我将自动切换角色"}
            disabled={loading}
            className={`flex-1 px-4 py-2 border rounded-xl focus:ring-2 focus:outline-none ${
              loading 
                ? 'border-gray-200 bg-gray-100 text-gray-500 cursor-not-allowed' 
                : 'border-blue-200 focus:border-blue-500 focus:ring-blue-200 bg-white'
            }`}
          />
          <button
            onClick={handleSend}
            disabled={loading}
            className={`p-2 rounded-xl transition-colors ${
              loading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white hover:from-blue-600 hover:to-indigo-600'
            }`}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="mt-2 text-xs text-gray-500">例如：“给我推荐个晚餐” (角色将切换至营养师) 或 “如何保持锻炼动机？” (角色将切换至行为教练)</p>
      </div>
    </div>
  );
}