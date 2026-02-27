/**
 * 系统配置管理页面
 */

import React, { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  Select,
  message,
  Drawer,
  Typography,
  Card,
  Badge,
} from 'antd';
import {
  EditOutlined,
  HistoryOutlined,
  SaveOutlined,
  CloseOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { useRequest } from 'ahooks';
import { api } from '../../services/api';

const { Title } = Typography;
const { TextArea } = Input;

interface Config {
  id: string;
  config_key: string;
  config_value: any;
  config_type: string;
  config_category: string;
  description: string;
  environment: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface ConfigHistory {
  id: string;
  old_value: any;
  new_value: any;
  changed_by: string;
  reason: string;
  changed_at: string;
}

const ConfigTypeMap: Record<string, { color: string; label: string }> = {
  ai_prompt: { color: 'blue', label: 'AI 提示词' },
  feature_flag: { color: 'green', label: '功能开关' },
  system_config: { color: 'orange', label: '系统配置' },
  notification_template: { color: 'purple', label: '通知模板' },
  business_rule: { color: 'cyan', label: '业务规则' },
};

const AdminConfigs: React.FC = () => {
  const [editingConfig, setEditingConfig] = useState<Config | null>(null);
  const [historyVisible, setHistoryVisible] = useState(false);
  const [currentHistory, setCurrentHistory] = useState<ConfigHistory[]>([]);
  const [form] = Form.useForm();

  // 获取配置列表
  const { data: configsData, loading, refresh } = useRequest(() =>
    api.get('/api/v1/admin/configs').then(res => res.data)
  );

  // 获取配置历史
  const loadHistory = async (configKey: string) => {
    try {
      const res = await api.get(`/api/v1/admin/configs/${configKey}/history`);
      setCurrentHistory(res.data.items);
      setHistoryVisible(true);
    } catch (error) {
      message.error('加载历史记录失败');
    }
  };

  // 编辑配置
  const handleEdit = (config: Config) => {
    setEditingConfig(config);
    form.setFieldsValue({
      config_value: JSON.stringify(config.config_value, null, 2),
      reason: '',
    });
  };

  // 保存配置
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      const configValue = JSON.parse(values.config_value);

      await api.put(`/api/v1/admin/configs/${editingConfig!.config_key}`, null, {
        params: {
          config_value: JSON.stringify(configValue),
          reason: values.reason || undefined,
        },
      });

      message.success('配置更新成功');
      setEditingConfig(null);
      refresh();
    } catch (error: any) {
      if (error.message?.includes('JSON')) {
        message.error('JSON 格式错误，请检查');
      } else {
        message.error('更新失败');
      }
    }
  };

  // 清除缓存
  const handleClearCache = async () => {
    try {
      await api.post('/api/v1/admin/configs/cache/clear');
      message.success('缓存已清除');
    } catch (error) {
      message.error('清除缓存失败');
    }
  };

  const columns = [
    {
      title: '配置 Key',
      dataIndex: 'config_key',
      key: 'config_key',
      fixed: 'left',
      width: 250,
      render: (text: string) => <Typography.Text code>{text}</Typography.Text>,
    },
    {
      title: '类型',
      dataIndex: 'config_type',
      key: 'config_type',
      width: 120,
      render: (type: string) => {
        const config = ConfigTypeMap[type] || { color: 'default', label: type };
        return <Tag color={config.color}>{config.label}</Tag>;
      },
    },
    {
      title: '分类',
      dataIndex: 'config_category',
      key: 'config_category',
      width: 100,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '环境',
      dataIndex: 'environment',
      key: 'environment',
      width: 100,
      render: (env: string) => {
        const envColors: Record<string, string> = {
          all: 'blue',
          development: 'green',
          staging: 'orange',
          production: 'red',
        };
        return <Tag color={envColors[env] || 'default'}>{env}</Tag>;
      },
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 80,
      render: (active: boolean) => (
        <Badge status={active ? 'success' : 'error'} text={active ? '激活' : '禁用'} />
      ),
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 180,
      render: (time: string) => new Date(time).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right',
      render: (_: any, record: Config) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            size="small"
            icon={<HistoryOutlined />}
            onClick={() => loadHistory(record.config_key)}
          >
            历史
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
          <div>
            <Title level={2} style={{ margin: 0 }}>
              <SettingOutlined style={{ marginRight: 8 }} />
              系统配置管理
            </Title>
            <Typography.Text type="secondary">
              管理系统配置、AI 提示词、功能开关等
            </Typography.Text>
          </div>
          <Space>
            <Button onClick={handleClearCache}>清除缓存</Button>
            <Button type="primary" onClick={refresh} loading={loading}>
              刷新
            </Button>
          </Space>
        </div>

        <Table
          columns={columns}
          dataSource={configsData?.items || []}
          loading={loading}
          rowKey="id"
          scroll={{ x: 1500 }}
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </Card>

      {/* 编辑配置弹窗 */}
      <Modal
        title={`编辑配置：${editingConfig?.config_key}`}
        open={!!editingConfig}
        onOk={handleSave}
        onCancel={() => setEditingConfig(null)}
        width={800}
        okText="保存"
        cancelText="取消"
        okButtonProps={{ icon: <SaveOutlined /> }}
        cancelButtonProps={{ icon: <CloseOutlined /> }}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 20 }}>
          <Form.Item
            label="配置值（JSON 格式）"
            name="config_value"
            rules={[{ required: true, message: '请输入配置值' }]}
          >
            <TextArea rows={15} style={{ fontFamily: 'monospace', fontSize: 12 }} />
          </Form.Item>
          <Form.Item label="变更原因" name="reason">
            <TextArea rows={2} placeholder="可选：说明变更原因" />
          </Form.Item>
        </Form>

        <Card size="small" title="配置信息" style={{ marginTop: 16 }}>
          <div><strong>类型：</strong>{editingConfig?.config_type}</div>
          <div><strong>分类：</strong>{editingConfig?.config_category}</div>
          <div><strong>描述：</strong>{editingConfig?.description}</div>
          <div><strong>环境：</strong>{editingConfig?.environment}</div>
        </Card>
      </Modal>

      {/* 变更历史抽屉 */}
      <Drawer
        title="配置变更历史"
        placement="right"
        width={600}
        open={historyVisible}
        onClose={() => setHistoryVisible(false)}
      >
        {currentHistory.length === 0 ? (
          <Typography.Text type="secondary">暂无变更记录</Typography.Text>
        ) : (
          <Timeline>
            {currentHistory.map((log, index) => (
              <Timeline.Item key={log.id} color="blue">
                <div><strong>变更时间：</strong>{new Date(log.changed_at).toLocaleString()}</div>
                <div><strong>变更人：</strong>{log.changed_by || '系统'}</div>
                {log.reason && <div><strong>原因：</strong>{log.reason}</div>}
                <div style={{ marginTop: 8 }}>
                  <div><strong>旧值：</strong></div>
                  <pre style={{ background: '#f5f5f5', padding: 8, borderRadius: 4, fontSize: 11 }}>
                    {JSON.stringify(log.old_value, null, 2)}
                  </pre>
                </div>
                <div style={{ marginTop: 8 }}>
                  <div><strong>新值：</strong></div>
                  <pre style={{ background: '#e6f7ff', padding: 8, borderRadius: 4, fontSize: 11 }}>
                    {JSON.stringify(log.new_value, null, 2)}
                  </pre>
                </div>
              </Timeline.Item>
            ))}
          </Timeline>
        )}
      </Drawer>
    </div>
  );
};

export default AdminConfigs;
