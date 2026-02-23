import { useState } from 'react';
import { Send, Stethoscope, User } from 'lucide-react';
import { api } from '../api/client'; // 导入API客户端

export function NutritionistChat() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: '你好！我是营养师。我可以提供专业的营养建议、饮食搭配指导和健康饮食计划。请告诉我你今天吃了什么，或你有关于营养的任何问题。',
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
      // 发送到AI服务，特别指定为营养师角色
      const aiResponse = await api.sendRoleMessage(input, "nutritionist");
      
      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: aiResponse.response,
      };
      
      setMessages([...updatedMessages, aiMessage]);
    } catch (error) {
      console.error('Error sending message to nutritionist:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: '抱歉，我在处理您的营养咨询时遇到了问题。请稍后再试。',
      };
      
      setMessages([...updatedMessages, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col bg-white rounded-2xl shadow-sm border border-green-200">
      <div className="p-4 border-b border-green-200 bg-green-50">
        <div className="flex items-center">
          <Stethoscope className="w-6 h-6 text-green-600 mr-2" />
          <h1 className="text-lg font-semibold text-gray-900">专业营养师</h1>
        </div>
        <p className="text-sm text-gray-500 pl-8">提供专业的营养饮食建议</p>
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
                  : 'bg-green-100 text-green-600'
              }`}
            >
              {message.role === 'user' ? <User className="w-4 h-4" /> : <Stethoscope className="w-4 h-4" />}
            </div>
            
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-green-100 text-gray-900'
              }`}
            >
              <p className="text-sm">{message.content}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 bg-green-100 text-green-600">
              <Stethoscope className="w-4 h-4" />
            </div>
            
            <div className="max-w-[80%] rounded-2xl px-4 py-2 bg-green-100 text-gray-900">
              <p className="text-sm">营养师正在分析您的营养需求...</p>
            </div>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-green-200 bg-green-50">
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !loading && handleSend()}
            placeholder={loading ? "营养师思考中..." : "询问有关营养的问题或记录今天的饮食..."}
            disabled={loading}
            className={`flex-1 px-4 py-2 border rounded-xl focus:ring-2 focus:outline-none ${
              loading 
                ? 'border-gray-200 bg-gray-100 text-gray-500 cursor-not-allowed' 
                : 'border-green-200 focus:border-green-500 focus:ring-green-200'
            }`}
          />
          <button
            onClick={handleSend}
            disabled={loading}
            className={`p-2 rounded-xl transition-colors ${
              loading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-green-600 text-white hover:bg-green-700'
            }`}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="mt-2 text-xs text-gray-500">例如：我今天午餐吃什么好？或 我早餐吃了燕麦、牛奶和香蕉</p>
      </div>
    </div>
  );
}