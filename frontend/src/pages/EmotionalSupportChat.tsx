import { useState } from 'react';
import { Send, Heart, User } from 'lucide-react';
import { api } from '../api/client'; // Import API client

export function EmotionalSupportChat() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: '你好！我是你的情感陪伴伙伴。我在这里聆听你的心声，给你情感上的支持与温暖。请随时与我分享你的感受、担忧或者开心的事。',
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
      // Send to AI service, specifically for emotional support role
      const aiResponse = await api.sendRoleMessage(input, "emotional_support");
      
      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: aiResponse.response,
      };
      
      setMessages([...updatedMessages, aiMessage]);
    } catch (error) {
      console.error('Error sending message to emotional support:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: '很抱歉，我在处理您的情感支持请求时遇到了问题。但我仍然在这里倾听你，你可以继续分享你的感受。',
      };
      
      setMessages([...updatedMessages, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col bg-gradient-to-br from-pink-50 to-purple-50 rounded-2xl shadow-sm border border-pink-200">
      <div className="p-4 border-b border-pink-200 bg-gradient-to-r from-pink-100 to-purple-100">
        <div className="flex items-center">
          <Heart className="w-6 h-6 text-pink-500 mr-2" />
          <h1 className="text-lg font-semibold text-gray-900">专属情感陪伴</h1>
        </div>
        <p className="text-sm text-gray-500 pl-8">温暖倾听，用心陪伴每一段历程</p>
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
                  : 'bg-gradient-to-r from-pink-100 to-purple-100 text-pink-500'
              }`}
            >
              {message.role === 'user' ? <User className="w-4 h-4" /> : <Heart className="w-4 h-4" />}
            </div>
            
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border border-pink-100 text-gray-900 shadow-sm'
              }`}
            >
              <p className="text-sm">{message.content}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 bg-gradient-to-r from-pink-100 to-purple-100 text-pink-500">
              <Heart className="w-4 h-4" />
            </div>
            
            <div className="max-w-[80%] rounded-2xl px-4 py-2 bg-white border border-pink-100 text-gray-900 shadow-sm">
              <p className="text-sm">情感陪伴正在温暖地倾听你的感受...</p>
            </div>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-pink-200 bg-gradient-to-r from-pink-50 to-purple-50">
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !loading && handleSend()}
            placeholder={loading ? "陪伴听取得..." : "分享你的感受、担忧或想法..."}
            disabled={loading}
            className={`flex-1 px-4 py-2 border rounded-xl focus:ring-2 focus:outline-none ${
              loading 
                ? 'border-gray-200 bg-gray-100 text-gray-500 cursor-not-allowed' 
                : 'border-pink-200 focus:border-pink-500 focus:ring-pink-200 bg-white'
            }`}
          />
          <button
            onClick={handleSend}
            disabled={loading}
            className={`p-2 rounded-xl transition-colors ${
              loading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-pink-500 to-purple-500 text-white hover:from-pink-600 hover:to-purple-600'
            }`}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="mt-2 text-xs text-gray-500">比如：我今天压力有点大，或者我为自己的进步感到开心</p>
      </div>
    </div>
  );
}