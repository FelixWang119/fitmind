import { useState } from 'react';
import { Send, Target, User } from 'lucide-react';
import { api } from '../api/client'; // Import API client

export function BehaviorCoachChat() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: '你好！我是你的行为教练。我帮助你建立和维持健康的习惯，克服挑战，并保持长期的行为改变。请告诉我你现在面临的习惯形成方面的挑战，或你想寻求的行为策略。',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

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
      // Send to AI service, specifically for behavior coach role
      const aiResponse = await api.sendRoleMessage(input, "behavior_coach");
      
      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: aiResponse.response,
      };
      
      setMessages([...updatedMessages, aiMessage]);
    } catch (error) {
      console.error('Error sending message to behavior coach:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: '抱歉，我在处理您的行为咨询时遇到了问题。请稍后再试。',
      };
      
      setMessages([...updatedMessages, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col bg-white rounded-2xl shadow-sm border border-purple-200">
      <div className="p-4 border-b border-purple-200 bg-purple-50">
        <div className="flex items-center">
          <Target className="w-6 h-6 text-purple-600 mr-2" />
          <h1 className="text-lg font-semibold text-gray-900">专业行为教练</h1>
        </div>
        <p className="text-sm text-gray-500 pl-8">助您养成持久的健康习惯与行为模式</p>
      </div>
      
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
                  : 'bg-purple-100 text-purple-600'
              }`}
            >
              {message.role === 'user' ? <User className="w-4 h-4" /> : <Target className="w-4 h-4" />}
            </div>
            
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-purple-100 text-gray-900'
              }`}
            >
              <p className="text-sm">{message.content}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 bg-purple-100 text-purple-600">
              <Target className="w-4 h-4" />
            </div>
            
            <div className="max-w-[80%] rounded-2xl px-4 py-2 bg-purple-100 text-gray-900">
              <p className="text-sm">行为教练正在分析您的习惯模式...</p>
            </div>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-purple-200 bg-purple-50">
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !loading && handleSend()}
            placeholder={loading ? "教练思考中..." : "寻求习惯养成建议或行为策略..."}
            disabled={loading}
            className={`flex-1 px-4 py-2 border rounded-xl focus:ring-2 focus:outline-none ${
              loading 
                ? 'border-gray-200 bg-gray-100 text-gray-500 cursor-not-allowed' 
                : 'border-purple-200 focus:border-purple-500 focus:ring-purple-200'
            }`}
          />
          <button
            onClick={handleSend}
            disabled={loading}
            className={`p-2 rounded-xl transition-colors ${
              loading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-purple-600 text-white hover:bg-purple-700'
            }`}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="mt-2 text-xs text-gray-500">例如：我如何坚持每天运动30分钟？或者怎样建立健康的晨间例程？</p>
      </div>
    </div>
  );
}