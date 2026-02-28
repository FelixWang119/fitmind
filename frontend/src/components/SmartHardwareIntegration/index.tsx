/**
 * 智能硬件集成组件
 * 包含设备列表、设备绑定流程、数据同步界面、同步历史记录
 */

import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Tabs, 
  Button, 
  Space, 
  message, 
  Modal, 
  Progress, 
  List, 
  Avatar, 
  Tag, 
  Timeline,
  Row, 
  Col,
  Typography,
  Input,
  Form,
  Radio
} from 'antd';
import { 
  BluetoothOutlined, 
  PlusOutlined, 
  SyncOutlined, 
  ClockCircleOutlined,
  CheckCircleOutlined,
  PoweroffOutlined,
  SettingsOutlined
} from '@ant-design/icons';
import { useAuthStore } from '../../../store/authStore';

const { Title, Text, Paragraph } = Typography;

// 类型定义
interface Device {
  id: string;
  name: string;
  type: 'watch' | 'scale' | 'band' | 'earbuds' | 'phone';
  brand: string;
  model: string;
  status: 'connected' | 'disconnected' | 'syncing';
  lastSync: string;
  battery: number;
}

interface SyncRecord {
  id: string;
  deviceId: string;
  deviceName: string;
  timestamp: string;
  dataPoints: number;
  duration: string;
  status: 'success' | 'partial' | 'failed';
}

// 设备数据
const MOCK_DEVICES: Device[] = [
  { 
    id: '1', 
    name: 'Apple Watch Series 8', 
    type: 'watch', 
    brand: 'Apple', 
    model: 'Watch Series 8', 
    status: 'connected', 
    lastSync: '2024-01-15 18:30', 
    battery: 75 
  },
  { 
    id: '2', 
    name: '华为体脂秤', 
    type: 'scale', 
    brand: '华为', 
    model: 'Body Composition Scale 2', 
    status: 'disconnected', 
    lastSync: '2024-01-14 07:15', 
    battery: 80 
  },
];

const MOCK_SYNC_HISTORY: SyncRecord[] = [
  { id: '1', deviceId: '1', deviceName: 'Apple Watch Series 8', timestamp: '2024-01-15 18:30', dataPoints: 1250, duration: '23秒', status: 'success' },
  { id: '2', deviceId: '1', deviceName: 'Apple Watch Series 8', timestamp: '2024-01-15 08:15', dataPoints: 980, duration: '18秒', status: 'success' },
  { id: '3', deviceId: '2', deviceName: '华为体脂秤', timestamp: '2024-01-14 07:15', dataPoints: 45, duration: '5秒', status: 'success' },
  { id: '4', deviceId: '1', deviceName: 'Apple Watch Series 8', timestamp: '2024-01-14 19:00', dataPoints: 1120, duration: '25秒', status: 'success' },
];

// 品牌图标映射
const BRAND_ICONS = {
  Apple: '🍎',
  Huawei: ' Huawei',
  Xiaomi: ' Xiaomi',
  Samsung: ' Samsung',
  Garmin: ' Garmin',
  Fitbit: ' Fitbit',
  OPPO: ' OPPO',
  Vivo: ' Vivo',
};

// 智能硬件集成组件
export const SmartHardwareIntegration: React.FC = () => {
  const [devices, setDevices] = useState<MOCK_DEVICES>(MOCK_DEVICES);
  const [activeTab, setActiveTab] = useState('devices');
  const [isBindingModalVisible, setIsBindingModalVisible] = useState(false);
  const [bindingStep, setBindingStep] = useState(1);
  const [selectedDeviceType, setSelectedDeviceType] = useState<string>('watch');

  // 设备列表组件
  const DeviceList = () => (
    <div className="space-y-6">
      {/* 添加设备按钮 */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">我的设备</h2>
        <Button 
          type="primary" 
          icon={<PlusOutlined />}
          onClick={() => setIsBindingModalVisible(true)}
        >
          添加设备
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {devices.map((device) => (
          <Card 
            key={device.id} 
            className={`hover:shadow-xl transition-all duration-300 ${
              device.status === 'connected' 
                ? 'border-blue-200 ring-1 ring-blue-100' 
                : 'border-gray-200'
            }`}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-4">
                <div className={`w-16 h-16 rounded-xl flex items-center justify-center text-4xl ${
                  device.status === 'connected' ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white' : 'bg-gray-100 text-gray-400'
                }`}>
                  {BRAND_ICONS[device.brand as keyof typeof BRAND_ICONS] || '💻'}
                </div>
                <div>
                  <h3 className="font-bold text-lg text-gray-800">{device.name}</h3>
                  <p className="text-sm text-gray-500">{device.brand} - {device.model}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
                  device.status === 'connected' 
                    ? 'bg-green-100 text-green-700' 
                    : device.status === 'syncing'
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-gray-100 text-gray-600'
                }`}>
                  {device.status === 'connected' ? '已连接' : device.status === 'syncing' ? '同步中' : '已断开'}
                </div>
                <Button 
                  type="link" 
                  icon={<PoweroffOutlined />} 
                  onClick={() => {
                    if (device.status === 'connected') {
                      setDevices(prev => prev.map(d => d.id === device.id ? { ...d, status: 'disconnected' } : d));
                      message.success(`${device.name} 已断开连接`);
                    }
                  }}
                />
              </div>
            </div>

            <div className="space-y-3 text-sm">
              <div className="flex justify-between items-center">
                <span className="text-gray-500">最后同步</span>
                <span className="font-medium text-gray-800">{device.lastSync}</span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-gray-500">电量</span>
                <div className="flex items-center space-x-2">
                  <span className="font-medium text-gray-800">{device.battery}%</span>
                  <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full ${
                        device.battery > 80 ? 'bg-green-500' : 
                        device.battery > 50 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${device.battery}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              {device.status === 'connected' && (
                <div className="pt-3 border-t border-gray-100">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">实时同步</span>
                    <div className="flex items-center text-green-500">
                      <span className="mr-2">✅</span>
                      <span className="text-sm font-medium animate-pulse">实时同步中</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="mt-4 pt-4 border-t border-gray-100 flex justify-between items-center">
              <Button size="small" icon={<SyncOutlined />}>
                立即同步
              </Button>
              <Button size="small" icon={<SettingsOutlined />}>
                设置
              </Button>
            </div>
          </Card>
        ))}

        {/* 添加设备卡片 */}
        <Card 
          className="hover:shadow-xl transition-all duration-300 border-dashed border-2 border-gray-300 hover:border-blue-400 cursor-pointer bg-gray-50"
          onClick={() => setIsBindingModalVisible(true)}
        >
          <div className="flex flex-col items-center justify-center py-8">
            <div className="w-20 h-20 rounded-full bg-blue-100 flex items-center justify-center mb-4">
              <PlusOutlined className="w-10 h-10 text-blue-500" />
            </div>
            <h3 className="font-semibold text-lg text-gray-700">添加新设备</h3>
            <p className="text-sm text-gray-500 mt-2 text-center">
              支持Apple Watch、华为、小米等主流设备
            </p>
          </div>
        </Card>
      </div>

      {/* 设备统计 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-8">
        {[
          { label: '已绑定设备', value: devices.length, color: 'blue' },
          { label: '已连接', value: devices.filter(d => d.status === 'connected').length, color: 'green' },
          { label: '同步成功', value: MOCK_SYNC_HISTORY.filter(s => s.status === 'success').length, color: 'purple' },
          { label: '平均同步率', value: '98.5%', color: 'orange' },
        ].map((stat, index) => (
          <Card key={index}>
            <div className="flex items-center space-x-4">
              <div className={`p-4 rounded-xl bg-${stat.color}-100`}>
                <BluetoothOutlined className={`w-8 h-8 text-${stat.color}-600`} />
              </div>
              <div>
                <p className="text-gray-500 text-sm">{stat.label}</p>
                <p className="text-2xl font-bold text-gray-800">{stat.value}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );

  // 绑定流程模态框
  const BindingModal = () => (
    <Modal
      title="绑定智能设备"
      open={isBindingModalVisible}
      onCancel={() => setIsBindingModalVisible(false)}
      footer={null}
      width={600}
      destroyOnClose
    >
      <div className="space-y-6">
        {/* 步骤条 */}
        <div className="flex justify-between items-center">
          {[1, 2, 3].map((step) => (
            <div key={step} className="flex items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                bindingStep >= step ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-500'
              }`}>
                {step}
              </div>
              {step < 3 && (
                <div className={`w-16 h-1 mx-2 ${
                  bindingStep > step ? 'bg-blue-500' : 'bg-gray-200'
                }`}></div>
              )}
            </div>
          ))}
        </div>

        {bindingStep === 1 && (
          <div className="text-center space-y-6">
            <div className="w-24 h-24 mx-auto bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center text-white text-5xl">
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-800 mb-2">选择设备类型</h3>
              <p className="text-gray-500">支持多种智能设备，快速绑定</p>
            </div>
            <div className="grid grid-cols-3 gap-4">
              {[
                { type: 'watch', name: '智能手表', icon: '⌚' },
                { type: 'scale', name: '体脂秤', icon: '⚖️' },
                { type: 'band', name: '手环', icon: '💪' },
              ].map((item) => (
                <div 
                  key={item.type}
                  className={`p-6 rounded-xl border-2 cursor-pointer transition-all ${
                    selectedDeviceType === item.type 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-blue-300'
                  }`}
                  onClick={() => setSelectedDeviceType(item.type)}
                >
                  <div className="text-3xl mb-3">{item.icon}</div>
                  <div className="font-semibold text-gray-800">{item.name}</div>
                </div>
              ))}
            </div>
            <Button 
              type="primary" 
              size="large" 
              className="w-full"
              onClick={() => setBindingStep(2)}
              disabled={selectedDeviceType === ''}
            >
              继续
            </Button>
          </div>
        )}

        {bindingStep === 2 && (
          <div className="space-y-6">
            <div className="text-center mb-6">
              <h3 className="text-xl font-bold text-gray-800 mb-2">
                {selectedDeviceType === 'watch' ? '绑定智能手表' : 
                 selectedDeviceType === 'scale' ? '绑定体脂秤' : '绑定手环'}
              </h3>
              <p className="text-gray-500">请确保设备电量充足并打开蓝牙</p>
            </div>

            <div className="bg-blue-50 p-6 rounded-xl text-center">
              <div className="text-4xl mb-4">📱</div>
              <p className="text-gray-700 mb-4">
                1. 打开手机蓝牙和WeightAI应用<br/>
                2. 确保设备处于配对模式<br/>
                3. 点击下方按钮开始搜索
              </p>
              <Button 
                type="primary" 
                icon={<BluetoothOutlined />}
                size="large"
                className="w-full"
                onClick={() => {
                  message.success('正在搜索设备...');
                  setTimeout(() => {
                    message.success('设备搜索完成');
                    setBindingStep(3);
                  }, 1500);
                }}
              >
                搜索设备
              </Button>
            </div>

            <Button 
              type="ghost" 
              onClick={() => setBindingStep(1)}
            >
              返回上一步
            </Button>
          </div>
        )}

        {bindingStep === 3 && (
          <div className="text-center space-y-6">
            <div className="w-24 h-24 mx-auto bg-green-500 rounded-full flex items-center justify-center text-white text-5xl">
              <CheckCircleOutlined />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-gray-800 mb-2">绑定成功！</h3>
              <p className="text-gray-500">你的设备已成功连接到WeightAI</p>
            </div>

            <div className="bg-gray-50 p-6 rounded-xl space-y-4 text-left">
              <div className="flex justify-between items-center pb-4 border-b border-gray-200">
                <span className="text-gray-500">设备名称</span>
                <span className="font-semibold text-gray-800">
                  {selectedDeviceType === 'watch' ? 'Apple Watch Series 8' : 
                   selectedDeviceType === 'scale' ? '华为体脂秤' : '小米手环7'}
                </span>
              </div>
              <div className="flex justify-between items-center pb-4 border-b border-gray-200">
                <span className="text-gray-500">支持数据</span>
                <span className="font-semibold text-gray-800 text-sm">
                  {selectedDeviceType === 'watch' 
                    ? '步数、心率、睡眠、运动数据' 
                    : selectedDeviceType === 'scale' 
                    ? '体重、体脂率、肌肉量、水分' 
                    : '步数、心率、睡眠、_MESSAGES'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-500">自动同步</span>
                <span className="font-semibold text-green-600 flex items-center">
                  ✅ 已启用
                </span>
              </div>
            </div>

            <Space className="w-full">
              <Button 
                size="large" 
                className="flex-1"
                onClick={() => setIsBindingModalVisible(false)}
              >
                完成
              </Button>
              <Button 
                type="primary" 
                size="large" 
                className="flex-1"
                onClick={() => {
                  // 添加新设备到列表
                  const newDevice: Device = {
                    id: String(Date.now()),
                    name: selectedDeviceType === 'watch' ? 'Apple Watch Series 8' : 
                         selectedDeviceType === 'scale' ? '华为体脂秤' : '小米手环7',
                    type: selectedDeviceType as any,
                    brand: selectedDeviceType === 'watch' ? 'Apple' : '其他',
                    model: '新设备',
                    status: 'connected',
                    lastSync: '刚刚',
                    battery: 100,
                  };
                  setDevices(prev => [...prev, newDevice]);
                  setIsBindingModalVisible(false);
                  setBindingStep(1);
                }}
              >
                继续绑定
              </Button>
            </Space>
          </div>
        )}
      </div>
    </Modal>
  );

  // 同步历史组件
  const SyncHistory = () => (
    <div className="space-y-6">
      <Card>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800 flex items-center">
            <SyncOutlined className="mr-2" />
            同步历史记录
          </h2>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-500">时间范围：</span>
            <select className="px-4 py-2 border border-gray-300 rounded-lg text-sm">
              <option>最近7天</option>
              <option>最近30天</option>
              <option>最近90天</option>
            </select>
          </div>
        </div>

        <Timeline mode="alternate">
          {MOCK_SYNC_HISTORY.map((record, index) => (
            <Timeline.Item key={record.id}>
              <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                <div className="flex justify-between items-start mb-3">
                  <div className="flex items-center space-x-3">
                    <Avatar size="small" shape="square">
                      {record.deviceName.charAt(0)}
                    </Avatar>
                    <div>
                      <h4 className="font-semibold text-gray-800">{record.deviceName}</h4>
                      <p className="text-xs text-gray-500">{record.timestamp}</p>
                    </div>
                  </div>
                  <Tag 
                    color={record.status === 'success' ? 'green' : record.status === 'partial' ? 'orange' : 'red'}
                    className="text-xs font-medium"
                  >
                    {record.status === 'success' ? '成功' : record.status === 'partial' ? '部分成功' : '失败'}
                  </Tag>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center">
                      <span className="text-gray-500 mr-2">数据点：</span>
                      <span className="font-medium text-gray-800">{record.dataPoints.toLocaleString()}</span>
                    </div>
                    <div className="flex items-center">
                      <span className="text-gray-500 mr-2">耗时：</span>
                      <span className="font-medium text-gray-800">{record.duration}</span>
                    </div>
                  </div>
                  {record.status === 'success' && (
                    <div className="flex items-center text-green-500">
                      <CheckCircleOutlined className="mr-1" />
                      同步完成
                    </div>
                  )}
                </div>
              </div>
            </Timeline.Item>
          ))}
        </Timeline>

        <div className="text-center mt-6">
          <Button type="dashed" icon={<DownloadOutlined />}>
            下载全部历史
          </Button>
        </div>
      </Card>

      {/* 同步统计 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { label: '平均同步时间', value: '18秒', trend: 'fast', icon: '⚡' },
          { label: '同步成功率', value: '98.5%', trend: 'up', icon: '📈' },
          { label: '累计同步数据', value: '15,230', unit: '条', trend: 'up', icon: '📊' },
        ].map((stat, index) => (
          <Card key={index}>
            <div className="flex items-center space-x-4">
              <div className="p-4 rounded-xl bg-purple-100">
                <span className="text-3xl">{stat.icon}</span>
              </div>
              <div className="flex-1">
                <p className="text-gray-500 text-sm">{stat.label}</p>
                <div className="text-2xl font-bold text-gray-800 mt-1">
                  {stat.value} {stat.unit}
                </div>
                <div className={`text-xs font-medium ${stat.trend === 'fast' ? 'text-green-600' : 'text-green-600'}`}>
                  {stat.trend === 'fast' ? '同步速度超快' : '整体趋势向上'}
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">⚙️ 智能硬件集成</h1>
            <p className="text-gray-600 mt-2">连接智能设备，自动同步运动和健康数据</p>
          </div>
          <div className="flex items-center space-x-4">
            <Button 
              type="primary" 
              icon={<SyncOutlined />}
              onClick={() => {
                message.success('正在同步所有设备...');
                setTimeout(() => message.success('同步完成！'), 2000);
              }}
            >
              同步全部设备
            </Button>
            <Button 
              type="default" 
              icon={<PoweroffOutlined />}
              onClick={() => {
                setDevices(prev => prev.map(d => ({ ...d, status: 'disconnected' })));
                message.success('所有设备已断开连接');
              }}
            >
              断开所有设备
            </Button>
          </div>
        </div>

        {/* 快速连接区域 */}
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl p-6 text-white flex flex-col md:flex-row items-center justify-between">
          <div className="mb-4 md:mb-0">
            <h3 className="text-xl font-bold mb-2">快速连接</h3>
            <p className="opacity-90">
              确保手机蓝牙已打开，设备处于配对模式
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-green-400 animate-pulse"></div>
              <span className="text-sm">蓝牙状态：已开启</span>
            </div>
            <Button 
              type="primary" 
              size="small"
              onClick={() => setIsBindingModalVisible(true)}
            >
              添加设备
            </Button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs 
        activeKey={activeTab} 
        onChange={setActiveTab}
        items={[
          {
            key: 'devices',
            label: '设备管理',
            children: <DeviceList />,
            icon: <BluetoothOutlined className="w-4 h-4" />,
          },
          {
            key: 'sync',
            label: '同步历史',
            children: <SyncHistory />,
            icon: <ClockCircleOutlined className="w-4 h-4" />,
          },
        ]}
      />

      {/* 支持的设备 */}
      <div className="mt-8">
        <Card title="支持的设备品牌" className="hover:shadow-lg transition-shadow">
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {['Apple', 'Huawei', 'Xiaomi', 'Samsung', 'Garmin', 'Fitbit', 'OPPO', 'Vivo', 'Realme', 'Nothing', 'OnePlus', 'Google'].map((brand, index) => (
              <div 
                key={index} 
                className="flex items-center justify-center p-4 bg-gray-50 rounded-xl hover:bg-blue-50 hover:shadow-md transition-all cursor-pointer"
              >
                <span className="font-bold text-gray-700 text-lg">
                  {BRAND_ICONS[brand as keyof typeof BRAND_ICONS] || brand}
                </span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* 绑定模态框 */}
      <BindingModal />
    </div>
  );
};

export default SmartHardwareIntegration;
