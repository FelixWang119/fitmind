/**
 * 系统配置管理组件
 * 包含配置项管理、功能开关、参数配置、预览功能
 */

import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Tabs, 
  Switch, 
  Input, 
  InputNumber, 
  Select, 
  Button, 
  message, 
  Space, 
  Divider, 
  Typography,
  Form,
  Radio,
  Slider,
  Badge
} from 'antd';
import { 
  SettingOutlined,
  EyeOutlined,
  SaveOutlined,
  QuestionCircleOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import type { TabsProps } from 'antd';

// 类型定义
interface ConfigOption {
  key: string;
  label: string;
  description: string;
  value: any;
  type: 'switch' | 'input' | 'select' | 'number' | 'slider';
  options?: { label: string; value: any }[];
  min?: number;
  max?: number;
  step?: number;
}

// 模拟配置数据
const MOCK_CONFIGS = {
  // 功能开关配置
  featureFlags: [
    { key: 'gamification_enabled', label: '游戏化系统', description: '启用积分、等级、徽章等游戏化功能', value: true },
    { key: 'community_enabled', label: '社区功能', description: '启用用户排行榜、成就分享、互助社区等功能', value: true },
    { key: 'hardware_integration_enabled', label: '智能硬件集成', description: '启用与智能穿戴设备的数据同步', value: true },
    { key: 'email_notifications_enabled', label: '邮件通知', description: '启用系统邮件通知功能', value: true },
    { key: 'wechatNotifications_enabled', label: '微信通知', description: '启用微信消息推送', value: true },
    { key: 'ai_coaching_enabled', label: 'AI健康教练', description: '启用AI健康建议和个性化指导', value: true },
  ] as ConfigOption[],
  
  // 参数配置
  parameters: [
    { key: 'weightUnit', label: '体重单位', description: '选择体重显示单位', value: 'kg', type: 'select', options: [
      { label: '公斤 (kg)', value: 'kg' },
      { label: '磅 (lb)', value: 'lb' },
      { label: '斤 (jin)', value: 'jin' },
    ]},
    { key: 'temperatureUnit', label: '温度单位', description: '选择温度显示单位', value: 'celsius', type: 'select', options: [
      { label: '摄氏度 (°C)', value: 'celsius' },
      { label: '华氏度 (°F)', value: 'fahrenheit' },
    ]},
    { key: 'caloriesTarget', label: '热量目标', description: '每日热量摄入目标（千卡）', value: 1800, type: 'number', min: 1000, max: 5000, step: 50 },
    { key: 'stepTarget', label: '步数目标', description: '每日步数目标', value: 10000, type: 'number', min: 5000, max: 50000, step: 1000 },
    { key: 'waterTarget', label: '饮水目标', description: '每日饮水杯数目标', value: 8, type: 'number', min: 4, max: 20, step: 1 },
    { key: 'sleepTarget', label: '睡眠目标', description: '每晚睡眠小时数目标', value: 8, type: 'slider', min: 4, max: 12, step: 0.5 },
  ] as ConfigOption[],
  
  // 预览配置
  previewOptions: [
    { key: 'darkMode', label: '深色模式', description: '启用深色主题界面', value: false, type: 'switch' },
    { key: 'compactMode', label: '紧凑模式', description: '减少界面间距，显示更多内容', value: false, type: 'switch' },
    { key: 'highContrast', label: '高对比度', description: '提高界面对比度，便于阅读', value: false, type: 'switch' },
  ] as ConfigOption[],
};

// 配置管理组件
export const SystemConfigManagement: React.FC = () => {
  const [configs, setConfigs] = useState(MOCK_CONFIGS);
  const [activeTab, setActiveTab] = useState('features');
  const [previewMode, setPreviewMode] = useState(false);

  // 处理配置变更
  const handleConfigChange = (key: string, value: any) => {
    setConfigs(prev => {
      const newConfigs = { ...prev };
      
      // 更新 featureFlags
      if (newConfigs.featureFlags) {
        const feature = newConfigs.featureFlags.find(f => f.key === key);
        if (feature) {
          feature.value = value;
          return newConfigs;
        }
      }
      
      // 更新 parameters
      if (newConfigs.parameters) {
        const param = newConfigs.parameters.find(p => p.key === key);
        if (param) {
          param.value = value;
          return newConfigs;
        }
      }
      
      // 更新 previewOptions
      if (newConfigs.previewOptions) {
        const preview = newConfigs.previewOptions.find(p => p.key === key);
        if (preview) {
          preview.value = value;
          return newConfigs;
        }
      }
      
      return newConfigs;
    });
  };

  // 保存配置
  const handleSave = () => {
    message.success('配置已保存');
    // 实际应该调用后端API保存配置
  };

  // 重置配置
  const handleReset = () => {
    setConfigs(MOCK_CONFIGS);
    message.success('配置已重置为默认值');
  };

  // 配置项组件
  const ConfigItem = ({ config }: { config: ConfigOption }) => {
    const [value, setValue] = useState(config.value);
    const [isModified, setIsModified] = useState(false);

    useEffect(() => {
      setValue(config.value);
      setIsModified(false);
    }, [config.value]);

    const handleChange = (newValue: any) => {
      setValue(newValue);
      setIsModified(true);
    };

    return (
      <div className={`flex flex-col space-y-3 p-4 rounded-xl transition-all ${
        isModified ? 'bg-blue-50 border border-blue-200' : 'hover:bg-gray-50'
      }`}>
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <div className="flex items-center space-x-2">
              <h4 className="font-semibold text-gray-800">{config.label}</h4>
              {config.key.includes('enabled') && (
                <Badge 
                  color={value ? 'green' : 'red'} 
                  text={value ? '已启用' : '已禁用'}
                  status={value ? 'success' : 'error'}
                />
              )}
            </div>
            <p className="text-sm text-gray-500 mt-1">{config.description}</p>
          </div>
          
          <div className="flex items-center">
            <button 
              className="text-gray-400 hover:text-blue-500 mr-3"
              title="帮助"
            >
              <QuestionCircleOutlined className="w-5 h-5" />
            </button>
            
            {config.type === 'switch' ? (
              <Switch 
                checked={value} 
                onChange={handleChange} 
                checkedChildren="启用" 
                unCheckedChildren="禁用" 
              />
            ) : (
              <span className="text-sm text-green-600 font-medium px-2 py-1 bg-green-50 rounded-lg">
                修改并保存
              </span>
            )}
          </div>
        </div>

        {/* 输入控件 */}
        {!config.key.includes('enabled') && (
          <div className="pl-8">
            {config.type === 'input' && (
              <Input 
                value={value as string}
                onChange={(e) => handleChange(e.target.value)}
                placeholder="请输入配置值"
              />
            )}
            
            {config.type === 'number' && (
              <InputNumber 
                value={value as number}
                onChange={(val) => handleChange(val)}
                min={config.min}
                max={config.max}
                step={config.step}
                style={{ width: '100%' }}
                placeholder={`请输入数字 (${config.min}-${config.max})`}
              />
            )}
            
            {config.type === 'select' && (
              <Select 
                value={value as string}
                onChange={(val) => handleChange(val)}
                style={{ width: '100%' }}
                options={(config.options || []).map(opt => ({
                  label: opt.label,
                  value: opt.value,
                }))}
              />
            )}
            
            {config.type === 'slider' && (
              <div className="space-y-2">
                <Slider 
                  value={value as number}
                  onChange={(val) => handleChange(val)}
                  min={config.min}
                  max={config.max}
                  step={config.step}
                  tooltip={{ formatter: null }}
                />
                <div className="text-center font-semibold text-gray-700">
                  {value} {config.key.includes('sleep') ? '小时' : ''}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  // 功能开关卡片
  const FeatureFlagsCard = () => (
    <Card title="功能开关配置" className="hover:shadow-lg transition-shadow">
      <div className="space-y-4">
        {configs.featureFlags.map(config => (
          <ConfigItem key={config.key} config={config} />
        ))}
      </div>
    </Card>
  );

  // 参数配置卡片
  const ParametersCard = () => (
    <Card title="系统参数配置" className="hover:shadow-lg transition-shadow">
      <div className="space-y-4">
        {configs.parameters.map(config => (
          <ConfigItem key={config.key} config={config} />
        ))}
      </div>
    </Card>
  );

  // 预览配置卡片
  const PreviewOptionsCard = () => (
    <Card title="界面预览配置" className="hover:shadow-lg transition-shadow">
      <div className="bg-gray-50 p-4 rounded-xl mb-4">
        <p className="text-sm text-gray-600 mb-3">
          <ClockCircleOutlined className="mr-1" />
          预览配置会在应用切换到新标签页时生效
        </p>
        <Button 
          type="primary" 
          icon={<EyeOutlined />}
          onClick={() => setPreviewMode(!previewMode)}
        >
          {previewMode ? '退出预览模式' : '进入预览模式'}
        </Button>
      </div>
      
      <div className="space-y-4">
        {configs.previewOptions.map(config => (
          <ConfigItem key={config.key} config={config} />
        ))}
      </div>
    </Card>
  );

  // 配置说明
  const ConfigInfo = () => (
    <div className="bg-blue-50 p-6 rounded-xl border border-blue-100 mb-6">
      <h4 className="font-bold text-lg mb-2 text-blue-800">系统配置说明</h4>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700">
        <div className="flex items-start">
          <CheckCircleOutlined className="text-green-500 mr-2 mt-1" />
          <div>
            <p className="font-semibold mb-1">配置立即生效</p>
            <p>大多数配置修改后会立即应用到当前会话，部分配置需要刷新页面生效。</p>
          </div>
        </div>
        <div className="flex items-start">
          <CheckCircleOutlined className="text-green-500 mr-2 mt-1" />
          <div>
            <p className="font-semibold mb-1">用户级配置</p>
            <p>所有配置均为用户个人设置，不影响其他用户，保证隐私安全。</p>
          </div>
        </div>
        <div className="flex items-start">
          <CheckCircleOutlined className="text-green-500 mr-2 mt-1" />
          <div>
            <p className="font-semibold mb-1">默认值保护</p>
            <p>关键配置都有默认值，即使误操作也能快速恢复。</p>
          </div>
        </div>
        <div className="flex items-start">
          <CheckCircleOutlined className="text-green-500 mr-2 mt-1" />
          <div>
            <p className="font-semibold mb-1">配置历史</p>
            <p>系统会记录配置修改历史，方便追踪和回溯。</p>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">⚙️ 系统配置管理</h1>
            <p className="text-gray-600 mt-2">配置系统功能、参数和界面偏好</p>
          </div>
          <Space>
            <Button 
              onClick={handleReset}
              icon={<ClockCircleOutlined />}
            >
              重置为默认
            </Button>
            <Button 
              type="primary" 
              icon={<SaveOutlined />}
              onClick={handleSave}
            >
              保存配置
            </Button>
          </Space>
        </div>
        
        <ConfigInfo />
      </div>

      {/* Tabs */}
      <Tabs 
        activeKey={activeTab} 
        onChange={setActiveTab}
        items={[
          {
            key: 'features',
            label: '功能开关',
            children: <FeatureFlagsCard />,
            icon: <SettingOutlined className="w-4 h-4" />,
          },
          {
            key: 'parameters',
            label: '参数配置',
            children: <ParametersCard />,
            icon: <span className="text-xl">⚙️</span>,
          },
          {
            key: 'preview',
            label: '界面预览',
            children: <PreviewOptionsCard />,
            icon: <EyeOutlined className="w-4 h-4" />,
          },
        ]}
      />

      {/* 配置快速预览 */}
      <div className="mt-8">
        <Card title="当前配置概览">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-6 rounded-xl text-white">
              <h4 className="font-semibold mb-2 text-blue-100">功能启用状态</h4>
              <div className="space-y-2 text-sm">
                {configs.featureFlags.map(f => (
                  <div key={f.key} className="flex justify-between items-center">
                    <span className="opacity-90 truncate max-w-[150px]">{f.label}</span>
                    <span className={`px-2 py-1 rounded-lg text-xs font-medium ${
                      f.value ? 'bg-white/20 text-white' : 'bg-white/10 text-gray-300'
                    }`}>
                      {f.value ? '已启用' : '已禁用'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="bg-gradient-to-br from-green-500 to-teal-600 p-6 rounded-xl text-white">
              <h4 className="font-semibold mb-2 text-green-100">核心参数</h4>
              <div className="space-y-3 text-sm">
                <div>
                  <span className="opacity-80 block mb-1">体重单位</span>
                  <span className="text-lg font-bold">
                    {configs.parameters.find(p => p.key === 'weightUnit')?.value === 'kg' ? '公斤 (kg)' : 
                     configs.parameters.find(p => p.key === 'weightUnit')?.value === 'lb' ? '磅 (lb)' : '斤 (jin)'}
                  </span>
                </div>
                <div>
                  <span className="opacity-80 block mb-1">热量目标</span>
                  <span className="text-lg font-bold">
                    {configs.parameters.find(p => p.key === 'caloriesTarget')?.value} 千卡/天
                  </span>
                </div>
                <div>
                  <span className="opacity-80 block mb-1">步数目标</span>
                  <span className="text-lg font-bold">
                    {configs.parameters.find(p => p.key === 'stepTarget')?.value.toLocaleString()} 步/天
                  </span>
                </div>
                <div>
                  <span className="opacity-80 block mb-1">饮水目标</span>
                  <span className="text-lg font-bold">
                    {configs.parameters.find(p => p.key === 'waterTarget')?.value} 杯/天
                  </span>
                </div>
              </div>
            </div>
            
            <div className="bg-gradient-to-br from-orange-500 to-red-600 p-6 rounded-xl text-white">
              <h4 className="font-semibold mb-2 text-orange-100">快捷设置</h4>
              <div className="space-y-3">
                <Button 
                  block 
                  size="small"
                  className="bg-white/20 hover:bg-white/30 border-transparent text-white"
                  onClick={() => {
                    setConfigs(prev => ({
                      ...prev,
                      parameters: prev.parameters.map(p => 
                        p.key === 'caloriesTarget' ? { ...p, value: 1500 } : p
                      )
                    }));
                  }}
                >
                  快速设置：1500千卡
                </Button>
                <Button 
                  block 
                  size="small"
                  className="bg-white/20 hover:bg-white/30 border-transparent text-white"
                  onClick={() => {
                    setConfigs(prev => ({
                      ...prev,
                      parameters: prev.parameters.map(p => 
                        p.key === 'stepTarget' ? { ...p, value: 8000 } : p
                      )
                    }));
                  }}
                >
                  快速设置：8000步
                </Button>
                <Button 
                  block 
                  size="small"
                  className="bg-white/20 hover:bg-white/30 border-transparent text-white"
                  onClick={() => {
                    setConfigs(prev => ({
                      ...prev,
                      parameters: prev.parameters.map(p => 
                        p.key === 'waterTarget' ? { ...p, value: 10 } : p
                      )
                    }));
                  }}
                >
                  快速设置：10杯水
                </Button>
                <Button 
                  block 
                  size="small"
                  className="bg-white/20 hover:bg-white/30 border-transparent text-white"
                  onClick={() => {
                    setConfigs(prev => ({
                      ...prev,
                      featureFlags: prev.featureFlags.map(f => ({ ...f, value: true }))
                    }));
                  }}
                >
                  启用所有功能
                </Button>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default SystemConfigManagement;
