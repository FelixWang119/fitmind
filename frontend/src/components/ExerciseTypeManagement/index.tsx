/**
 * 运动类型后台管理组件
 * 包含列表、添加/编辑/删除、MET值配置、排序搜索、批量操作
 */

import React, { useState, useEffect, useMemo } from 'react';
import { 
  Table, 
  Button, 
  Modal, 
  Form, 
  Input, 
  InputNumber, 
  Switch, 
  Space, 
  Tag, 
  message, 
  Tabs, 
  Card, 
  Radio,
  Upload,
  Progress,
  Dropdown,
  Menu
} from 'antd';
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  ImportOutlined, 
  ExportOutlined,
  SearchOutlined,
  SortAscending,
  SortDescending,
  MoreOutlined,
  FireOutlined,
  MoveUp,
  MoveDown
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/lib/table';
import { useAuthStore } from '../../../store/authStore';

// 类型定义
interface ExerciseType {
  id: string;
  name: string;
  description: string;
  category: 'cardio' | 'strength' | 'flexibility' | 'balance' | 'mindfulness';
  metValue: number;
  isPublic: boolean;
  icon: string;
  createdAt: string;
  usageCount: number;
}

interface MovementStatistics {
  totalMinutes: number;
  totalCalories: number;
  sessionCount: number;
  averageDuration: number;
}

// 初始数据
const INITIAL_EXERCISE_TYPES: ExerciseType[] = [
  { id: '1', name: '慢跑', description: '中等强度的有氧运动', category: 'cardio', metValue: 7.0, isPublic: true, icon: '🏃', createdAt: '2024-01-01', usageCount: 150 },
  { id: '2', name: '力量训练', description: '全身力量训练课程', category: 'strength', metValue: 6.0, isPublic: true, icon: '🏋️', createdAt: '2024-01-01', usageCount: 120 },
  { id: '3', name: '瑜伽', description: '柔韧性和平衡性训练', category: 'flexibility', metValue: 3.5, isPublic: true, icon: '🧘', createdAt: '2024-01-02', usageCount: 80 },
  { id: '4', name: 'HIIT高强度间歇', description: '高强度间歇训练', category: 'cardio', metValue: 10.0, isPublic: true, icon: '⚡', createdAt: '2024-01-03', usageCount: 95 },
  { id: '5', name: '普拉提', description: '核心力量训练', category: 'strength', metValue: 4.0, isPublic: true, icon: '🪐', createdAt: '2024-01-04', usageCount: 70 },
  { id: '6', name: '太极', description: '传统身心锻炼', category: 'mindfulness', metValue: 2.5, isPublic: true, icon: '☯️', createdAt: '2024-01-05', usageCount: 40 },
  { id: '7', name: '游泳', description: '全身有氧运动', category: 'cardio', metValue: 8.0, isPublic: true, icon: '🏊', createdAt: '2024-01-06', usageCount: 60 },
  { id: '8', name: '骑行', description: '户外或室内骑行', category: 'cardio', metValue: 6.5, isPublic: true, icon: '🚴', createdAt: '2024-01-07', usageCount: 55 },
];

// 模拟统计数据
const MOCK_STATISTICS: MovementStatistics[] = [
  { totalMinutes: 4500, totalCalories: 28500, sessionCount: 150, averageDuration: 30 },
  { totalMinutes: 3200, totalCalories: 19200, sessionCount: 120, averageDuration: 27 },
  { totalMinutes: 2800, totalCalories: 9800, sessionCount: 80, averageDuration: 35 },
  { totalMinutes: 3600, totalCalories: 36000, sessionCount: 95, averageDuration: 38 },
  { totalMinutes: 2100, totalCalories: 8400, sessionCount: 70, averageDuration: 30 },
  { totalMinutes: 1400, totalCalories: 3500, sessionCount: 40, averageDuration: 35 },
  { totalMinutes: 2100, totalCalories: 16800, sessionCount: 60, averageDuration: 35 },
  { totalMinutes: 1950, totalCalories: 12675, sessionCount: 55, averageDuration: 35 },
];

const CATEGORIES = {
  cardio: { label: '有氧运动', color: 'blue', icon: '🔥' },
  strength: { label: '力量训练', color: 'orange', icon: '💪' },
  flexibility: { label: '柔韧性', color: 'green', icon: '/stretch' },
  balance: { label: '平衡性', color: 'purple', icon: '⚖️' },
  mindfulness: { label: '身心', color: 'cyan', icon: '🧘' },
};

// 主组件
export const ExerciseTypeManagement: React.FC = () => {
  const [exerciseTypes, setExerciseTypes] = useState<ExerciseType[]>(INITIAL_EXERCISE_TYPES);
  const [searchText, setSearchText] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingItem, setEditingItem] = useState<ExerciseType | null>(null);
  const [form] = Form.useForm();
  const [activeTab, setActiveTab] = useState('list');
  const [bulkSelectedKeys, setBulkSelectedKeys] = useState<React.Key[]>([]);
  const [statistics, setStatistics] = useState<MovementStatistics[]>(MOCK_STATISTICS);

  // 计算统计数据
  const calculatedStats = useMemo(() => {
    const totalMinutes = exerciseTypes.reduce((sum, item) => {
      return sum + (item.usageCount * (statistics.find(s => item.usageCount === s.sessionCount)?.totalMinutes || 30));
    }, 0);
    const totalCalories = exerciseTypes.reduce((sum, item) => {
      return sum + (item.usageCount * (item.metValue * 30 * 60 / 60)); // 简化计算
    }, 0);
    
    return {
      totalMinutes: totalMinutes.toLocaleString(),
      totalCalories: Math.round(totalCalories).toLocaleString(),
      sessionCount: exerciseTypes.reduce((sum, item) => sum + item.usageCount, 0).toLocaleString(),
      averageDuration: 30
    };
  }, [exerciseTypes, statistics]);

  // 过滤后数据
  const filteredData = useMemo(() => {
    return exerciseTypes.filter(item => {
      const matchesSearch = item.name.includes(searchText) || item.description.includes(searchText);
      const matchesCategory = categoryFilter ? item.category === categoryFilter : true;
      return matchesSearch && matchesCategory;
    });
  }, [exerciseTypes, searchText, categoryFilter]);

  // 表格列定义
  const columns: ColumnsType<ExerciseType> = [
    {
      title: '运动名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      render: (text, record) => (
        <div className="flex items-center space-x-3">
          <span className="text-2xl">{record.icon}</span>
          <span className="font-semibold">{text}</span>
          {record.isPublic && <Tag color="blue" className="text-xs">公开</Tag>}
        </div>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      width: 250,
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 120,
      render: (category) => {
        const catInfo = CATEGORIES[category];
        return (
          <Tag icon={<span>{catInfo.icon}</span>} color={catInfo.color}>
            {catInfo.label}
          </Tag>
        );
      },
    },
    {
      title: 'MET值',
      dataIndex: 'metValue',
      key: 'metValue',
      width: 100,
      render: (met) => (
        <div className="flex items-center">
          < FireOutlined className="text-red-500 mr-1" />
          {met.toFixed(1)}
        </div>
      ),
    },
    {
      title: '使用次数',
      dataIndex: 'usageCount',
      key: 'usageCount',
      width: 100,
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 120,
      sorter: (a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime(),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space size="small">
          <Button 
            type="link" 
            icon={<EditOutlined />} 
            onClick={() => handleEdit(record)} 
          />
          <Button 
            type="link" 
            danger 
            icon={<DeleteOutlined />} 
            onClick={() => handleDelete(record.id)} 
          />
        </Space>
      ),
    },
  ];

  // 处理添加/编辑
  const handleEdit = (item: ExerciseType) => {
    setEditingItem(item);
    form.setFieldsValue(item);
    setIsModalVisible(true);
  };

  const handleDelete = (id: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个运动类型吗？',
      onOk: () => {
        setExerciseTypes(prev => prev.filter(item => item.id !== id));
        message.success('删除成功');
      },
    });
  };

  const handleCancel = () => {
    setIsModalVisible(false);
    setEditingItem(null);
    form.resetFields();
  };

  const handleFinish = async (values: any) => {
    if (editingItem) {
      setExerciseTypes(prev => 
        prev.map(item => 
          item.id === editingItem.id 
            ? { ...item, ...values, metValue: parseFloat(values.metValue) } 
            : item
        )
      );
      message.success('更新成功');
    } else {
      const newItem: ExerciseType = {
        ...values,
        id: String(Date.now()),
        metValue: parseFloat(values.metValue),
        icon: values.category === 'cardio' ? '🏃' : values.category === 'strength' ? '🏋️' : '🧘',
        isPublic: true,
        createdAt: new Date().toISOString().split('T')[0],
        usageCount: 0,
      };
      setExerciseTypes(prev => [...prev, newItem]);
      message.success('添加成功');
    }
    setIsModalVisible(false);
    form.resetFields();
    setEditingItem(null);
  };

  // 全选处理
  const onSelectChange = (newSelectedRowKeys: React.Key[]) => {
    setBulkSelectedKeys(newSelectedRowKeys);
  };

  const rowSelection = {
    selectedKeys: bulkSelectedKeys,
    onChange: onSelectChange,
  };

  // 批量操作菜单
  const bulkActionsMenu = (
    <Menu>
      <Menu.Item key="export" icon={<ExportOutlined />}>
        导出所选
      </Menu.Item>
      <Menu.Item key="delete" icon={<DeleteOutlined />} danger>
        删除所选
      </Menu.Item>
    </Menu>
  );

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">运动类型管理</h1>
            <p className="text-gray-600 mt-2">配置运动类型和MET值，管理运动数据</p>
          </div>
          <Button 
            type="primary" 
            icon={<PlusOutlined />} 
            onClick={() => {
              setEditingItem(null);
              form.resetFields();
              setIsModalVisible(true);
            }}
          >
            添加运动类型
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        {[
          { label: '总运动时长', value: calculatedStats.totalMinutes, unit: '分钟', color: 'blue' },
          { label: '总消耗热量', value: calculatedStats.totalCalories, unit: '千卡', color: 'orange' },
          { label: '运动次数', value: calculatedStats.sessionCount, unit: '次', color: 'green' },
          { label: '平均单次时长', value: calculatedStats.averageDuration, unit: '分钟', color: 'purple' },
        ].map((stat, index) => (
          <Card key={index} className="hover:shadow-lg transition-shadow">
            <div className="flex items-center space-x-4">
              <div className={`p-4 rounded-xl bg-${stat.color}-100`}>
                <FireOutlined className={`w-8 h-8 text-${stat.color}-600`} />
              </div>
              <div>
                <p className="text-gray-500 text-sm">{stat.label}</p>
                <p className="text-2xl font-bold text-gray-800">
                  {stat.value} <span className="text-sm text-gray-500">{stat.unit}</span>
                </p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Tabs */}
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <Tabs.TabPane tab="运动列表" key="list">
          <Card 
            title={
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <span>运动类型列表 ({filteredData.length})</span>
                <div className="flex flex-wrap gap-2">
                  {/* 搜索 */}
                  <div className="relative">
                    <SearchOutlined className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                    <Input 
                      placeholder="搜索运动类型..." 
                      value={searchText}
                      onChange={(e) => setSearchText(e.target.value)}
                      className="pl-10 w-64"
                      suffix={<SearchOutlined className="text-gray-400" />}
                    />
                  </div>
                  
                  {/* 分类筛选 */}
                  <select 
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    value={categoryFilter || ''}
                    onChange={(e) => setCategoryFilter(e.target.value || null)}
                  >
                    <option value="">全部分类</option>
                    {Object.entries(CATEGORIES).map(([key, cat]) => (
                      <option key={key} value={key}>{cat.label}</option>
                    ))}
                  </select>
                  
                  {/* 排序 */}
                  <Dropdown 
                    menu={{
                      items: [
                        { key: 'name-asc', label: '名称 A-Z' },
                        { key: 'name-desc', label: '名称 Z-A' },
                        { key: 'met-asc', label: 'MET值 低到高' },
                        { key: 'met-desc', label: 'MET值 高到低' },
                        { key: 'usage-desc', label: '使用次数 多到少' },
                      ],
                      onClick: ({ key }) => console.log('排序:', key)
                    }}
                    trigger={['click']}
                  >
                    <Button icon={<SortAscending className="w-4 h-4" />}>
                      排序
                    </Button>
                  </Dropdown>
                  
                  {/* 批量操作 */}
                  {bulkSelectedKeys.length > 0 && (
                    <Dropdown menu={bulkActionsMenu} trigger={['click']}>
                      <Button danger disabled={bulkSelectedKeys.length === 0}>
                        批量操作 ({bulkSelectedKeys.length})
                      </Button>
                    </Dropdown>
                  )}
                </div>
              </div>
            }
            className="mt-6"
          >
            <Table 
              rowKey="id"
              rowSelection={rowSelection}
              columns={columns}
              dataSource={filteredData}
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
              }}
            />
          </Card>
        </Tabs.TabPane>

        <Tabs.TabPane tab="MET值参考" key="met-reference">
          <Card title="MET值参考与配置">
            <div className="space-y-6">
              <div className="bg-blue-50 p-6 rounded-xl border border-blue-100">
                <h3 className="font-bold text-lg mb-2 text-blue-800">什么是MET值？</h3>
                <p className="text-gray-700 mb-3">
                  MET（Metabolic Equivalent of Energy）即代谢当量，表示运动时的能量消耗相对于静息状态的倍数。
                  1 MET = 静息状态下的能量消耗（约3.5ml O2/kg/min）
                </p>
                <div className="grid grid-cols-3 gap-4 mt-4">
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <p className="text-sm text-gray-500 mb-1">低强度</p>
                    <p className="text-xl font-bold text-green-600">1.0-2.9 MET</p>
                    <p className="text-xs text-gray-400 mt-1">瑜伽、太极、慢走</p>
                  </div>
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <p className="text-sm text-gray-500 mb-1">中等强度</p>
                    <p className="text-xl font-bold text-blue-600">3.0-5.9 MET</p>
                    <p className="text-xs text-gray-400 mt-1">快走、瑜伽、骑车</p>
                  </div>
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <p className="text-sm text-gray-500 mb-1">高强度</p>
                    <p className="text-xl font-bold text-red-600">6.0+ MET</p>
                    <p className="text-xs text-gray-400 mt-1">跑步、游泳、HIIT</p>
                  </div>
                </div>
              </div>

              {/* MET值配置表 */}
              <div className="overflow-x-auto">
                <table className="w-full border-collapse border border-gray-200">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="border border-gray-200 p-3 text-left">运动类型</th>
                      <th className="border border-gray-200 p-3 text-left">MET值范围</th>
                      <th className="border border-gray-200 p-3 text-left">示例活动</th>
                      <th className="border border-gray-200 p-3 text-left">配置建议</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      { label: '日常生活', range: '1.0-2.0', example: '吃饭、穿衣、散步', advice: '保持低MET值' },
                      { label: '轻度活动', range: '2.1-3.9', example: '慢走、伸展、轻家务', advice: '适合 rehabilitation' },
                      { label: '中等强度', range: '4.0-5.9', example: '快走、骑车、瑜伽', advice: '有氧运动主流范围' },
                      { label: '高强度', range: '6.0-8.9', example: '跑步、游泳、球类', advice: '有效燃脂区间' },
                      { label: '极高强度', range: '9.0+', example: 'HIIT、 sprint、竞技', advice: '快速燃脂但难度高' },
                    ].map((item, idx) => (
                      <tr key={idx}>
                        <td className="border border-gray-200 p-3">{item.label}</td>
                        <td className="border border-gray-200 p-3 font-mono">{item.range}</td>
                        <td className="border border-gray-200 p-3 text-sm">{item.example}</td>
                        <td className="border border-gray-200 p-3 text-sm">{item.advice}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </Card>
        </Tabs.TabPane>

        <Tabs.TabPane tab="批量导入" key="batch-import">
          <Card title="批量导入运动类型">
            <div className="space-y-6">
              <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-blue-400 transition-colors cursor-pointer bg-gray-50">
                <ImportOutlined className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-lg font-medium text-gray-700 mb-2">点击或拖拽CSV文件到此处</p>
                <p className="text-sm text-gray-500 mb-4">支持 .csv 格式，文件大小不超过 5MB</p>
                
                <div className="bg-blue-50 p-4 rounded-lg text-left text-sm text-gray-700 mb-4">
                  <p className="font-bold mb-2">CSV 格式要求：</p>
                  <pre className="bg-white p-3 rounded overflow-x-auto">
                    {`name,description,category,metValue,icon
慢跑,中等强度有氧运动,cardio,7.0,🏃
力量训练,全身力量训练,strength,6.0,🏋️
瑜伽,柔韧性和平衡性训练,flexibility,3.5,🧘`}
                  </pre>
                </div>

                <Button type="primary" size="large" icon={<ImportOutlined />}>
                  上传文件
                </Button>
              </div>

              <div className="bg-yellow-50 p-6 rounded-xl border border-yellow-100">
                <h4 className="font-bold text-yellow-800 mb-2">批量导入说明</h4>
                <ul className="space-y-2 text-gray-700 text-sm">
                  <li className="flex items-start">
                    <span className="text-yellow-500 mr-2">•</span>
                    <span>导入的运动类型默认为公开状态</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-yellow-500 mr-2">•</span>
                    <span>MET值范围应为 1.0 - 20.0 之间的数字</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-yellow-500 mr-2">•</span>
                    <span>分类必须是: cardio, strength, flexibility, balance, mindfulness</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-yellow-500 mr-2">•</span>
                    <span>图标使用 Unicode emoji，如 🏃、🏋️、🧘</span>
                  </li>
                </ul>
              </div>

              <div className="bg-gray-50 p-6 rounded-xl">
                <h4 className="font-bold text-gray-800 mb-4">历史导入记录</h4>
                <div className="space-y-2">
                  {[
                    { date: '2024-01-15 14:30', filename: '运动类型_20240115.csv', count: 15, status: '成功' },
                    { date: '2024-01-10 09:15', filename: '运动类型_20240110.csv', count: 8, status: '成功' },
                    { date: '2024-01-05 16:45', filename: '运动类型_20240105.csv', count: 0, status: '失败' },
                  ].map((record, idx) => (
                    <div key={idx} className="flex justify-between items-center p-3 bg-white rounded-lg border border-gray-200">
                      <div>
                        <p className="font-medium">{record.filename}</p>
                        <p className="text-sm text-gray-500">{record.date} - {record.count} 条记录</p>
                      </div>
                      <Tag color={record.status === '成功' ? 'green' : 'red'}>
                        {record.status}
                      </Tag>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Card>
        </Tabs.TabPane>
      </Tabs>

      {/* 添加/编辑对话框 */}
      <Modal
        title={editingItem ? '编辑运动类型' : '添加运动类型'}
        open={isModalVisible}
        onCancel={handleCancel}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleFinish}
          initialValues={{
            category: 'cardio',
            isPublic: true,
            icon: '🏃',
            metValue: 5.0,
          }}
        >
          <Form.Item
            name="name"
            label="运动名称"
            rules={[{ required: true, message: '请输入运动名称' }]}
          >
            <Input placeholder="例如：慢跑" />
          </Form.Item>

          <Form.Item
            name="description"
            label="描述"
            rules={[{ required: true, message: '请输入描述' }]}
          >
            <Input.TextArea rows={3} placeholder="简要描述这项运动" />
          </Form.Item>

          <div className="grid grid-cols-2 gap-4">
            <Form.Item
              name="category"
              label="分类"
              rules={[{ required: true, message: '请选择分类' }]}
            >
              <Radio.Group>
                {Object.entries(CATEGORIES).map(([key, cat]) => (
                  <Radio.Button key={key} value={key} style={{ width: '50%', textAlign: 'center' }}>
                    {cat.label}
                  </Radio.Button>
                ))}
              </Radio.Group>
            </Form.Item>

            <Form.Item
              name="icon"
              label="图标"
              rules={[{ required: true, message: '请选择图标' }]}
            >
              <Input placeholder="输入 Emoji，如 🏃" />
            </Form.Item>
          </div>

          <Form.Item
            name="metValue"
            label="MET值"
            rules={[
              { required: true, message: '请输入MET值' },
              { type: 'number', min: 1.0, max: 20.0, message: 'MET值应在1.0-20.0之间' }
            ]}
          >
            <InputNumber 
              min={1.0} 
              max={20.0} 
              step={0.1} 
              style={{ width: '100%' }} 
              placeholder="例如：7.0" 
            />
          </Form.Item>

          <Form.Item
            name="isPublic"
            label="公开状态"
            valuePropName="checked"
          >
            <Switch checkedChildren="公开" unCheckedChildren="私有" />
          </Form.Item>

          <Form.Item className="text-right">
            <Space>
              <Button onClick={handleCancel}>取消</Button>
              <Button type="primary" htmlType="submit">
                {editingItem ? '保存修改' : '添加'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ExerciseTypeManagement;
