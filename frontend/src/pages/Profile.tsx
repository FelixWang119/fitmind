import { useEffect, useState } from 'react';
import api from '../api/client';

interface UserProfile {
  id?: number;
  email?: string;
  username?: string;
  full_name?: string;
  age?: number;
  gender?: string;
  height?: number;
  initial_weight?: number;  // 存储千克，展示给用户也以千克
  target_weight?: number;   // 存储千克，展示给用户也以千克
  activity_level?: string;
  dietary_preferences?: string[];
}

const Profile = () => {
  const [profile, setProfile] = useState<UserProfile>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const data = await api.getCurrentUser();
      // 处理数据格式转换：如果初始体重和目标体重是克单位，转换为千克
      const formattedData = {
        ...data,
        initial_weight: data.initial_weight ? data.initial_weight / 1000 : undefined,
        target_weight: data.target_weight ? data.target_weight / 1000 : undefined,
      };
      setProfile(formattedData);
    } catch (err) {
      setError('Failed to load profile');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    let processedValue: string | number | string[] = value;

    // Convert values to appropriate types
    if (name === 'age' || name === 'height' || name === 'initial_weight' || name === 'target_weight') {
      processedValue = value ? Number(value) : null;
    } else if (name === 'dietary_preferences') {
      processedValue = value.split(',').map(item => item.trim()).filter(item => item);
    }
    
    setProfile(prev => ({
      ...prev,
      [name]: processedValue
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    
    try {
      // 体重处理：从KG转换为克（因为数据库可能是按克存储）
      const updatedProfile = { ...profile };
      if (updatedProfile.initial_weight) {
        updatedProfile.initial_weight = updatedProfile.initial_weight * 1000; // Convert kg to g
      }
      if (updatedProfile.target_weight) {
        updatedProfile.target_weight = updatedProfile.target_weight * 1000; // Convert kg to g
      }

      await api.updateUserProfile(updatedProfile);
      alert('Profile updated successfully!');
    } catch (err) {
      setError('Failed to update profile');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">个人资料设置</h1>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow p-6 space-y-6">
        {/* Basic Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">姓名</label>
            <input
              type="text"
              name="full_name"
              value={profile.full_name || ''}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-lg focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">用户名</label>
            <input
              type="text"
              name="username"
              value={profile.username || ''}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-lg focus:ring-blue-500 focus:border-blue-500"
              disabled
            />
            <p className="text-xs text-gray-500 mt-1">用户名不可更改</p>
          </div>
        </div>
        
        {/* Personal Details */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">年龄</label>
            <input
              type="number"
              name="age"
              value={profile.age || ''}
              onChange={handleChange}
              min="1"
              max="120"
              className="w-full px-4 py-2 border rounded-lg focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">性别</label>
            <select
              name="gender"
              value={profile.gender || ''}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-lg focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">请选择</option>
              <option value="male">男</option>
              <option value="female">女</option>
              <option value="other">其他</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">身高 (厘米)</label>
            <input
              type="number"
              name="height"
              value={profile.height || ''}
              onChange={handleChange}
              min="100"
              max="250"
              className="w-full px-4 py-2 border rounded-lg focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
        
        {/* Health Details */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">初始体重 (公斤)</label>
            <input
              type="number"
              step="0.1"
              name="initial_weight"
              value={profile.initial_weight ? profile.initial_weight : ''} // 直接显示公斤值
              onChange={handleChange}
              min="30"
              max="300"
              className="w-full px-4 py-2 border rounded-lg focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">目标体重 (公斤)</label>
            <input
              type="number"
              step="0.1"
              name="target_weight"
              value={profile.target_weight ? profile.target_weight : ''} // 直接显示公斤值
              onChange={handleChange}
              min="30"
              max="300"
              className="w-full px-4 py-2 border rounded-lg focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">活动水平</label>
            <select
              name="activity_level"
              value={profile.activity_level || ''}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-lg focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">请选择</option>
              <option value="sedentary">久坐不动</option>
              <option value="light">轻度活动</option>
              <option value="moderate">中度活动</option>
              <option value="active">活跃</option>
              <option value="very_active">非常活跃</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">饮食偏好</label>
            <input
              type="text"
              placeholder="请用逗号分隔，例如：素食,低碳水,无麸质"
              name="dietary_preferences"
              value={Array.isArray(profile.dietary_preferences) ? profile.dietary_preferences.join(', ') : ''}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-lg focus:ring-blue-500 focus:border-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">用逗号分隔多个偏好</p>
          </div>
        </div>
        
        <div className="flex justify-end pt-4">
          <button
            type="submit"
            disabled={saving}
            className={`px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
              saving ? 'opacity-75 cursor-not-allowed' : ''
            }`}
          >
            {saving ? '保存中...' : '保存资料'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default Profile;