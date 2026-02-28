/**
 * 通知模板管理组件
 * 包含模板列表、创建/编辑、预览、变量管理、发送测试
 */

import React, { useState, useEffect, useMemo } from 'react';
import { 
  Table, 
  Button, 
  Modal, 
  Form, 
  Input, 
  Tag, 
  Space, 
  message,
  Tabs,
  Card,
  Upload,
  recipient,
  Switch,
  Typography,
  Divider,
  Dropdown,
  Menu,
  Select
} from 'antd';
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  EyeOutlined,
  SendOutlined,
  TemplateOutlined,
  VariableOutlined,
  HistoryOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/lib/table';
import { useAuthStore } from '../../../store/authStore';

// 类型定义
interface NotificationTemplate {
  id: string;
  name: string;
  description: string;
  category: 'exercise' | 'nutrition' | 'weight' | 'community' | 'system';
  type: 'daily' | 'weekly' | 'reminder' | 'achievement' | 'alert';
  subject: string;
  content: string;
  variables: string[];
  isDefault: boolean;
  isActive: boolean;
  usageCount: number;
  lastModified: string;
}

interface NotificationHistory {
  id: string;
  templateId: string;
  templateName: string;
  sentAt: string;
  recipients: number;
  successRate: number;
  status: 'success' | 'partial' | 'failed';
}

const CATEGORIES = {
  exercise: { label: '运动提醒', icon: '🏃', color: 'blue' },
  nutrition: { label: '饮食提醒', icon: '🥗', color: 'green' },
  weight: { label: '体重目标', icon: '⚖️', color: 'purple' },
  community: { label: '社区动态', icon: '💬', color: 'orange' },
  system: { label: '系统通知', icon: '⚙️', color: 'gray' },
};

const TYPES = {
  daily: { label: '每日摘要', color: 'blue' },
  weekly: { label: '每周总结', color: 'purple' },
  reminder: { label: '提醒通知', color: 'orange' },
  achievement: { label: '成就奖励', color: 'gold' },
  alert: { label: '紧急提醒', color: 'red' },
};

// 初始数据
const INITIAL_TEMPLATES: NotificationTemplate[] = [
  {
    id: '1',
    name: '每日运动打卡提醒',
    description: '每日下午6点提醒用户进行运动打卡',
    category: 'exercise',
    type: 'daily',
    subject: '🏆 今日运动打卡提醒',
    content: '你好，{{userName}}！今天是{{date}}。\n\n你已经完成了{{exerciseMinutes}}分钟的运动，消耗了{{caloriesBurned}}千卡！\n\n距离今日目标还差{{remainingMinutes}}分钟，坚持就是胜利！🔥',
    variables: ['userName', 'date', 'exerciseMinutes', 'caloriesBurned', 'remainingMinutes'],
    isDefault: true,
    isActive: true,
    usageCount: 1250,
    lastModified: '2024-01-15 10:30',
  },
  {
    id: '2',
    name: '饮食记录完成奖励',
    description: '用户完成饮食记录后发放的奖励通知',
    category: 'nutrition',
    type: 'achievement',
    subject: '🎉 饮食记录奖励',
    content: '恭喜你，{{userName}}！\n\n你已经完成了今天的饮食记录，获得了{{points}}积分！\n\n连续{{streakDays}}天完成饮食记录，表现卓越！🌟',
    variables: ['userName', 'points', 'streakDays'],
    isDefault: false,
    isActive: true,
    usageCount: 890,
    lastModified: '2024-01-10 14:20',
  },
  {
    id: '3',
    name: '体重目标达成祝贺',
    description: '用户达成月度体重目标时发送',
    category: 'weight',
    type: 'achievement',
    subject: '🏆 恭喜！达成月度体重目标',
    content: '祝贺你，{{userName}}！\n\n你已经成功减重{{weightLost}}公斤，达到了{{targetWeight}}公斤的目标！\n\n你的毅力值得称赞，继续保持！💪',
    variables: ['userName', 'weightLost', 'targetWeight'],
    isDefault: true,
    isActive: true,
    usageCount: 320,
    lastModified: '2024-01-08 09:15',
  },
  {
    id: '4',
    name: '连续打卡庆祝',
    description: '用户连续7天打卡后的庆祝通知',
    category: 'exercise',
    type: 'achievement',
    subject: '🎊 连续打卡7天庆祝！',
    content: '🎉 太棒了！{{userName}}\n\n你已经连续{{consecutiveDays}}天完成打卡，获得徽章解锁！\n\n坚持就是胜利，你的毅力令人佩服！✨',
    variables: ['userName', 'consecutiveDays'],
    isDefault: false,
    isActive: true,
    usageCount: 150,
    lastModified: '2024-01-05 16:45',
  },
  {
    id: '5',
    name: '系统维护通知',
    description: '系统计划维护的提前通知',
    category: 'system',
    type: 'alert',
    subject: '⚠️ 系统维护通知',
    content: '亲爱的用户，\n\n我们计划在{{maintenanceTime}}进行系统维护，预计持续{{duration}}小时。期间服务可能会短暂中断，敬请谅解。\n\n维护结束后会有特别奖励发放！🎁',
    variables: ['maintenanceTime', 'duration'],
    isDefault: true,
    isActive: true,
    usageCount: 15,
    lastModified: '2024-01-01 08:00',
  },
];

// 示例历史记录
const MOCK_HISTORY: NotificationHistory[] = [
  { id: '1', templateId: '1', templateName: '每日运动打卡提醒', sentAt: '2024-01-15 18:00', recipients: 1250, successRate: 98.5, status: 'success' },
  { id: '2', templateId: '2', templateName: '饮食记录完成奖励', sentAt: '2024-01-15 12:30', recipients: 890, successRate: 99.2, status: 'success' },
  { id: '3', templateId: '3', templateName: '体重目标达成祝贺', sentAt: '2024-01-14 10:00', recipients: 45, successRate: 100.0, status: 'success' },
];

// 主组件
export const NotificationTemplateManagement: React.FC = () => {
  const [templates, setTemplates] = useState<NotificationTemplate[]>(INITIAL_TEMPLATES);
  const [searchText, setSearchText] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [currentTemplate, setCurrentTemplate] = useState<NotificationTemplate | null>(null);
  const [editingTemplate, setEditingTemplate] = useState<NotificationTemplate | null>(null);
  const [form] = Form.useForm();
  const [activeTab, setActiveTab] = useState('list');

  // 过滤后数据
  const filteredData = useMemo(() => {
    return templates.filter(template => {
      const matchesSearch = template.name.includes(searchText) || template.subject.includes(searchText);
      const matchesCategory = categoryFilter ? template.category === categoryFilter : true;
      return matchesSearch && matchesCategory;
    });
  }, [templates, searchText, categoryFilter]);

  // 表格列定义
  const columns: ColumnsType<NotificationTemplate> = [
    {
      title: '模板名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      render: (text, record) => (
        <div className="flex items-center space-x-3">
          <Tag color={CATEGORIES[record.category].color}>
            {CATEGORIES[record.category].icon}
          </Tag>
          <span className="font-semibold">{text}</span>
          {record.isDefault && <Tag color="blue" className="text-xs">默认模板</Tag>}
        </div>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      width: 200,
    },
    {
      title: '通知类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (type) => {
        const typeInfo = TYPES[type];
        return <Tag color={typeInfo.color}>{typeInfo.label}</Tag>;
      },
    },
    {
      title: '变量',
      key: 'variables',
      width: 150,
      render: (_, record) => (
        <Space size="small" wrap>
          {record.variables.map((variable, idx) => (
            <Tag key={idx} color="processing" className="text-xs">
              {variable}
            </Tag>
          ))}
        </Space>
      ),
    },
    {
      title: '使用次数',
      dataIndex: 'usageCount',
      key: 'usageCount',
      width: 100,
    },
    {
      title: '最近修改',
      dataIndex: 'lastModified',
      key: 'lastModified',
      width: 150,
      sorter: (a, b) => new Date(a.lastModified).getTime() - new Date(b.lastModified).getTime(),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_, record) => (
        <Space size="small">
          <Button 
            type="link" 
            icon={<EyeOutlined />} 
            onClick={() => handlePreview(record)} 
            title="预览"
          />
          <Button 
            type="link" 
            icon={<EditOutlined />} 
            onClick={() => handleEdit(record)} 
            title="编辑"
          />
          <Button 
            type="link" 
            danger 
            icon={<DeleteOutlined />} 
            onClick={() => handleDelete(record.id)} 
            title="删除"
          />
          <Button 
            type="link" 
            icon={<SendOutlined />} 
            onClick={() => handleSendTest(record)} 
            title="发送测试"
          />
        </Space>
      ),
    },
  ];

  // 处理操作
  const handleEdit = (template: NotificationTemplate) => {
    setEditingTemplate(template);
    form.setFieldsValue({
      ...template,
      variables: template.variables.join(', '),
    });
    setIsModalVisible(true);
  };

  const handleDelete = (id: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个通知模板吗？',
      onOk: () => {
        setTemplates(prev => prev.filter(t => t.id !== id));
        message.success('删除成功');
      },
    });
  };

  const handlePreview = (template: NotificationTemplate) => {
    setCurrentTemplate(template);
    setPreviewVisible(true);
  };

  const handleSendTest = (template: NotificationTemplate) => {
    message.success(`测试通知已发送到您的设备`);
    // 实际应该调用后端API
  };

  const handleCancel = () => {
    setIsModalVisible(false);
    setPreviewVisible(false);
    setEditingTemplate(null);
    form.resetFields();
    setCurrentTemplate(null);
  };

  const handleFinish = (values: any) => {
    // 处理变量输入
    const variables = values.variables
      ? values.variables.split(',').map((v: string) => v.trim()).filter((v: string) => v)
      : [];

    if (editingTemplate) {
      setTemplates(prev => 
        prev.map(t => 
          t.id === editingTemplate.id 
            ? { ...t, ...values, variables } 
            : t
        )
      );
      message.success('更新成功');
    } else {
      const newTemplate: NotificationTemplate = {
        ...values,
        id: String(Date.now()),
        variables,
        isDefault: false,
        isActive: true,
        usageCount: 0,
        lastModified: new Date().toISOString().replace('T', ' ').substring(0, 16),
      };
      setTemplates(prev => [...prev, newTemplate]);
      message.success('添加成功');
    }
    setIsModalVisible(false);
    form.resetFields();
    setEditingTemplate(null);
  };

  // 变量说明
  const VARIABLE_DESCRIPTIONS = [
    { variable: '{{userName}}', description: '用户姓名' },
    { variable: '{{date}}', description: '当前日期' },
    { variable: '{{exerciseMinutes}}', description: '今日运动时长（分钟）' },
    { variable: '{{caloriesBurned}}', description: '今日消耗热量（千卡）' },
    { variable: '{{weightLost}}', description: '减重重量（公斤）' },
    { variable: '{{streakDays}}', description: '连续打卡天数' },
    { variable: '{{points}}', description: '今日获得积分' },
    { variable: '{{consecutiveDays}}', description: '连续天数' },
    { variable: '{{targetWeight}}', description: '目标体重' },
    { variable: '{{maintenanceTime}}', description: '维护开始时间' },
    { variable: '{{duration}}', description: '持续时间（小时）' },
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">通知模板管理</h1>
            <p className="text-gray-600 mt-2">创建和管理系统通知模板，设置变量实现个性化</p>
          </div>
          <Button 
            type="primary" 
            icon={<PlusOutlined />} 
            onClick={() => {
              setEditingTemplate(null);
              form.resetFields();
              setIsModalVisible(true);
            }}
          >
            创建模板
          </Button>
        </div>

        {/* 统计卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            { label: '模板总数', value: templates.length, color: 'blue' },
            { label: '启用中', value: templates.filter(t => t.isActive).length, color: 'green' },
            { label: '使用次数', value: templates.reduce((sum, t) => sum + t.usageCount, 0).toLocaleString(), color: 'orange' },
            { label: '平均使用率', value: '87%', color: 'purple' },
          ].map((stat, index) => (
            <Card key={index}>
              <div className="flex items-center space-x-4">
                <div className={`p-4 rounded-xl bg-${stat.color}-100`}>
                  <TemplateOutlined className={`w-8 h-8 text-${stat.color}-600`} />
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

      {/* Tabs */}
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <Tabs.TabPane tab="模板列表" key="list">
          <Card 
            title={
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <span>通知模板列表 ({filteredData.length})</span>
                <div className="flex flex-wrap gap-2">
                  <div className="relative">
                    <input 
                      type="text"
                      placeholder="搜索模板..." 
                      className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      value={searchText}
                      onChange={(e) => setSearchText(e.target.value)}
                    />
                    <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                  
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
                </div>
              </div>
            }
            className="mt-6"
          >
            <Table 
              rowKey="id"
              columns={columns}
              dataSource={filteredData}
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
              }}
            />
          </Card>
        </Tabs.TabPane>

        <Tabs.TabPane tab="变量管理" key="variables">
          <Card title="通知变量说明">
            <div className="space-y-6">
              <div className="bg-blue-50 p-6 rounded-xl border border-blue-100">
                <h3 className="font-bold text-lg mb-2 text-blue-800">变量使用说明</h3>
                <p className="text-gray-700 mb-3">
                  在通知模板中，你可以使用变量来实现个性化内容。用户收到通知时，变量会被实际数据替换。
                  使用格式：<code className="bg-gray-200 px-2 py-1 rounded">{{'{{variableName}}'}}</code>
                </p>
                <div className="bg-white p-4 rounded-lg border border-gray-200 mb-3">
                  <p className="text-sm text-gray-600 mb-2">示例模板：</p>
                  <pre className="font-mono text-sm text-gray-800">
                    {`你好，{{userName}}！\n\n你今天已经运动了{{exerciseMinutes}}分钟，消耗了{{caloriesBurned}}千卡！\n\n继续加油！`}
                  </pre>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full border-collapse border border-gray-200">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="border border-gray-200 p-3 text-left">变量名</th>
                      <th className="border border-gray-200 p-3 text-left">说明</th>
                      <th className="border border-gray-200 p-3 text-left">适用场景</th>
                    </tr>
                  </thead>
                  <tbody>
                    {VARIABLE_DESCRIPTIONS.map((item, idx) => (
                      <tr key={idx}>
                        <td className="border border-gray-200 p-3 font-mono bg-gray-50">{item.variable}</td>
                        <td className="border border-gray-200 p-3">{item.description}</td>
                        <td className="border border-gray-200 p-3 text-sm text-gray-600">
                          {item.variable.includes('userName') || item.variable.includes('date') 
                            ? '几乎所有场景' 
                            : item.variable.includes('exercise') ? '运动相关' 
                            : item.variable.includes('weight') ? '体重相关' 
                            : '系统相关'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* 快捷添加区域 */}
              <div className="bg-gray-50 p-6 rounded-xl">
                <h4 className="font-bold text-gray-800 mb-4">快速添加变量</h4>
                <div className="flex flex-wrap gap-2">
                  {VARIABLE_DESCRIPTIONS.map((item) => (
                    <span 
                      key={item.variable}
                      className="px-3 py-1.5 bg-white border border-gray-300 rounded-lg text-sm font-mono hover:border-blue-400 hover:bg-blue-50 cursor-pointer transition-colors"
                      onClick={() => {
                        navigator.clipboard.writeText(item.variable);
                        message.success(`变量 ${item.variable} 已复制`);
                      }}
                      title="点击复制"
                    >
                      {item.variable}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </Card>
        </Tabs.TabPane>

        <Tabs.TabPane tab="发送测试" key="send-test">
          <Card title="发送测试通知">
            <div className="space-y-6">
              <div className="bg-gray-50 p-6 rounded-xl border border-gray-200">
                <h4 className="font-bold text-gray-800 mb-4">选择测试模板</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {templates.slice(0, 6).map(template => (
                    <div 
                      key={template.id}
                      className="p-4 bg-white rounded-xl border border-gray-300 hover:border-blue-400 cursor-pointer transition-all hover:shadow-md"
                      onClick={() => {
                        handleSendTest(template);
                        // 模拟发送
                      }}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h5 className="font-semibold text-gray-800">{template.name}</h5>
                        <Tag color={CATEGORIES[template.category].color}>{CATEGORIES[template.category].icon}</Tag>
                      </div>
                      <p className="text-sm text-gray-500 line-clamp-2">{template.description}</p>
                      <div className="mt-3 text-xs text-gray-400">
                        修改于: {template.lastModified}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-green-50 p-6 rounded-xl border border-green-100">
                <h4 className="font-bold text-green-800 mb-2">测试说明</h4>
                <ul className="space-y-2 text-gray-700 text-sm">
                  <li className="flex items-start">
                    <CheckCircleOutlined className="text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                    <span>测试通知会发送到当前登录用户的设备上</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircleOutlined className="text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                    <span>测试通知会替换所有变量为示例数据</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircleOutlined className="text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                    <span>发送成功后会显示实际效果预览</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircleOutlined className="text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                    <span>测试不会计入统计使用次数</span>
                  </li>
                </ul>
              </div>

              <div className="bg-blue-50 p-6 rounded-xl">
                <h4 className="font-bold text-blue-800 mb-4">最近测试记录</h4>
                <div className="space-y-2">
                  {[
                    { template: '每日运动打卡提醒', sentAt: '2024-01-15 14:30', status: '已送达', duration: '0.5s' },
                    { template: '饮食记录完成奖励', sentAt: '2024-01-15 11:20', status: '已送达', duration: '0.3s' },
                    { template: '连续打卡庆祝', sentAt: '2024-01-14 09:45', status: '已送达', duration: '0.4s' },
                  ].map((record, idx) => (
                    <div key={idx} className="flex justify-between items-center p-3 bg-white rounded-lg border border-gray-200">
                      <div>
                        <p className="font-medium">{record.template}</p>
                        <p className="text-sm text-gray-500">{record.sentAt}</p>
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className={`px-3 py-1 rounded-lg text-sm font-medium ${
                          record.status === '已送达' 
                            ? 'bg-green-100 text-green-700' 
                            : 'bg-red-100 text-red-700'
                        }`}>
                          {record.status}
                        </span>
                        <span className="text-sm text-gray-500">{record.duration}</span>
                      </div>
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
        title={editingTemplate ? '编辑通知模板' : '创建通知模板'}
        open={isModalVisible}
        onCancel={handleCancel}
        footer={null}
        width={700}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleFinish}
          initialValues={{
            category: 'exercise',
            type: 'daily',
            isActive: true,
            variables: '',
          }}
        >
          <div className="grid grid-cols-2 gap-4">
            <Form.Item
              name="name"
              label="模板名称"
              rules={[{ required: true, message: '请输入模板名称' }]}
            >
              <Input placeholder="例如：每日运动打卡提醒" />
            </Form.Item>

            <Form.Item
              name="category"
              label="分类"
              rules={[{ required: true, message: '请选择分类' }]}
            >
              <Select>
                {Object.entries(CATEGORIES).map(([key, cat]) => (
                  <Select.Option key={key} value={key}>
                    {cat.icon} {cat.label}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>
          </div>

          <Form.Item
            name="type"
            label="通知类型"
            rules={[{ required: true, message: '请选择通知类型' }]}
          >
            <Select>
              {Object.entries(TYPES).map(([key, type]) => (
                <Select.Option key={key} value={key}>
                  <Tag color={type.color}>{type.label}</Tag>
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="subject"
            label="通知主题"
            rules={[{ required: true, message: '请输入通知主题' }]}
          >
            <Input placeholder="例如：🏆 今日运动打卡提醒" />
            <p className="text-xs text-gray-500 mt-1">主题会显示在通知的标题位置</p>
          </Form.Item>

          <Form.Item
            name="description"
            label="描述"
            rules={[{ required: true, message: '请输入描述' }]}
          >
            <Input.TextArea rows={2} placeholder="简要描述这个模板的用途" />
          </Form.Item>

          <Form.Item
            name="content"
            label="通知内容"
            rules={[{ required: true, message: '请输入通知内容' }]}
            extra={
              <div className="bg-yellow-50 p-3 rounded-lg text-sm">
                <strong className="text-yellow-800">提示：</strong> 使用 <code className="bg-yellow-200 px-1 rounded">{{'{{变量名}}'}}</code> 来插入变量
              </div>
            }
          >
            <Input.TextArea 
              rows={8} 
              placeholder="你好，{{userName}}！\n\n你今天已经运动了{{exerciseMinutes}}分钟..."
              showCount
            />
          </Form.Item>

          <Form.Item
            name="variables"
            label="使用的变量"
            extra="使用逗号分隔多个变量"
          >
            <Input placeholder="例如：userName, date, exerciseMinutes" />
          </Form.Item>

          <Form.Item
            name="isActive"
            label="启用状态"
            valuePropName="checked"
          >
            <Switch checkedChildren="启用" unCheckedChildren="停用" />
          </Form.Item>

          <Form.Item className="text-right">
            <Space>
              <Button onClick={handleCancel}>取消</Button>
              <Button type="primary" htmlType="submit">
                {editingTemplate ? '保存修改' : '创建'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 预览对话框 */}
      <Modal
        title="通知预览"
        open={previewVisible}
        onCancel={handleCancel}
        footer={[
          <Button key="close" onClick={handleCancel}>关闭</Button>,
          <Button key="send" type="primary" icon={<SendOutlined />} onClick={() => {
            if (currentTemplate) {
              handleSendTest(currentTemplate);
            }
          }}>
            发送测试
          </Button>
        ]}
        width={500}
      >
        {currentTemplate && (
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex items-center space-x-2 mb-2">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-lg">🔔</span>
                </div>
                <div>
                  <p className="text-sm font-semibold text-gray-800">WeightAI 助手</p>
                  <p className="text-xs text-gray-500">{currentTemplate.lastModified}</p>
                </div>
              </div>
              <h4 className="font-bold text-gray-800 mb-2">{currentTemplate.subject}</h4>
              <div className="bg-white p-4 rounded-lg border border-gray-200 text-sm text-gray-700 whitespace-pre-wrap font-mono">
                {currentTemplate.content.replace(/{{(.*?)}}/g, (match, variable) => {
                  const replacements: Record<string, string> = {
                    userName: 'Felix',
                    date: new Date().toLocaleDateString('zh-CN'),
                    exerciseMinutes: '45',
                    caloriesBurned: '320',
                    weightLost: '2.5',
                    streakDays: '7',
                    points: '150',
                    consecutiveDays: '7',
                    targetWeight: '60',
                    maintenanceTime: '2024-01-20 02:00',
                    duration: '1',
                  };
                  return replacements[variable] || `{${variable}}`;
                })}
              </div>
            </div>

            <div className="bg-blue-50 p-4 rounded-lg">
              <h5 className="font-semibold text-blue-800 mb-2">变量替换示例：</h5>
              <div className="grid grid-cols-2 gap-2 text-sm">
                {currentTemplate.variables.map((variable, idx) => (
                  <div key={idx} className="flex justify-between items-center">
                    <span className="font-mono text-gray-700">{{'{{' + variable + '}}'}}</span>
                    <span className="text-gray-500">→ 已替换</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default NotificationTemplateManagement;
