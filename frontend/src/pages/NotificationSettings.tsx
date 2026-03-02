import { useEffect, useState } from 'react';
import { Switch, TimePicker, Slider, message } from 'antd';
import { Bell, BellOff, Clock, Mail, MessageCircle, Shield, Sun, Target, Trophy, Zap } from 'lucide-react';
import dayjs from 'dayjs';
import notificationApi, { NotificationSettings } from '../services/notificationApi';

const NotificationSettingsPage = () => {
  const [settings, setSettings] = useState<NotificationSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const data = await notificationApi.getSettings();
      setSettings(data);
    } catch (error) {
      console.error('Failed to load notification settings:', error);
      message.error('加载通知设置失败');
    } finally {
      setLoading(false);
    }
  };

  const updateSetting = async (key: keyof NotificationSettings, value: any) => {
    if (!settings) return;
    
    const updatedSettings = { ...settings, [key]: value };
    setSettings(updatedSettings);
    
    // 保存到后端
    setSaving(true);
    try {
      await notificationApi.updateSettings({ [key]: value });
      message.success('设置已保存');
    } catch (error) {
      console.error('Failed to update setting:', error);
      message.error('保存设置失败');
      // 恢复原值
      setSettings(settings);
    } finally {
      setSaving(false);
    }
  };

  if (loading || !settings) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">通知设置</h1>

      {/* 通知总开关 */}
      <section className="bg-white rounded-xl shadow p-6 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            {settings.enabled ? (
              <Bell className="w-6 h-6 text-blue-600 mr-3" />
            ) : (
              <BellOff className="w-6 h-6 text-gray-400 mr-3" />
            )}
            <div>
              <h2 className="text-lg font-semibold text-gray-800">接收通知</h2>
              <p className="text-sm text-gray-500">关闭后将不再接收任何通知</p>
            </div>
          </div>
          <Switch
            checked={settings.enabled}
            onChange={(checked) => updateSetting('enabled', checked)}
            loading={saving}
            checkedChildren="开启"
            unCheckedChildren="关闭"
          />
        </div>
      </section>

      {/* 通知类型设置 */}
      <section className="bg-white rounded-xl shadow p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
          <Zap className="w-5 h-5 mr-2 text-blue-600" />
          通知类型
        </h2>
        
        <div className="space-y-4">
          {/* 习惯打卡提醒 */}
          <div className="flex items-center justify-between py-3 border-b border-gray-100">
            <div className="flex items-center">
              <Target className="w-5 h-5 text-green-600 mr-3" />
              <div>
                <p className="font-medium text-gray-800">习惯打卡提醒</p>
                <p className="text-sm text-gray-500">提醒您完成每日习惯打卡</p>
              </div>
            </div>
            <Switch
              checked={settings.notify_habit_reminder}
              onChange={(checked) => updateSetting('notify_habit_reminder', checked)}
              disabled={!settings.enabled}
            />
          </div>

          {/* 里程碑成就通知 */}
          <div className="flex items-center justify-between py-3 border-b border-gray-100">
            <div className="flex items-center">
              <Trophy className="w-5 h-5 text-yellow-600 mr-3" />
              <div>
                <p className="font-medium text-gray-800">里程碑成就通知</p>
                <p className="text-sm text-gray-500">达成目标或获得成就时通知</p>
              </div>
            </div>
            <Switch
              checked={settings.notify_milestone}
              onChange={(checked) => updateSetting('notify_milestone', checked)}
              disabled={!settings.enabled}
            />
          </div>

          {/* 早安关怀 */}
          <div className="flex items-center justify-between py-3 border-b border-gray-100">
            <div className="flex items-center">
              <Sun className="w-5 h-5 text-orange-500 mr-3" />
              <div>
                <p className="font-medium text-gray-800">早安关怀</p>
                <p className="text-sm text-gray-500">每日的早安问候和激励</p>
              </div>
            </div>
            <Switch
              checked={settings.notify_care}
              onChange={(checked) => updateSetting('notify_care', checked)}
              disabled={!settings.enabled}
            />
          </div>

          {/* 系统通知 */}
          <div className="flex items-center justify-between py-3">
            <div className="flex items-center">
              <Shield className="w-5 h-5 text-red-600 mr-3" />
              <div>
                <p className="font-medium text-gray-800">系统通知</p>
                <p className="text-sm text-gray-500">重要系统更新和维护通知</p>
              </div>
            </div>
            <Switch
              checked={settings.notify_system}
              onChange={(checked) => updateSetting('notify_system', checked)}
              disabled={!settings.enabled}
            />
          </div>
        </div>
      </section>

      {/* 通知渠道 */}
      <section className="bg-white rounded-xl shadow p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
          <MessageCircle className="w-5 h-5 mr-2 text-blue-600" />
          通知渠道
        </h2>
        
        <div className="space-y-4">
          {/* 站内通知 */}
          <div className="flex items-center justify-between py-3 border-b border-gray-100">
            <div className="flex items-center">
              <MessageCircle className="w-5 h-5 text-blue-600 mr-3" />
              <div>
                <p className="font-medium text-gray-800">站内通知</p>
                <p className="text-sm text-gray-500">在应用内显示通知</p>
              </div>
            </div>
            <Switch
              checked={settings.in_app_enabled}
              onChange={(checked) => updateSetting('in_app_enabled', checked)}
              disabled={!settings.enabled}
            />
          </div>

          {/* 邮件通知 */}
          <div className="flex items-center justify-between py-3">
            <div className="flex items-center">
              <Mail className="w-5 h-5 text-gray-600 mr-3" />
              <div>
                <p className="font-medium text-gray-800">邮件通知</p>
                <p className="text-sm text-gray-500">通过电子邮件接收通知</p>
              </div>
            </div>
            <Switch
              checked={settings.email_enabled}
              onChange={(checked) => updateSetting('email_enabled', checked)}
              disabled={!settings.enabled}
            />
          </div>
        </div>
      </section>

      {/* 勿扰时段 */}
      <section className="bg-white rounded-xl shadow p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
          <Clock className="w-5 h-5 mr-2 text-blue-600" />
          勿扰时段
        </h2>
        
        <div className="flex items-center justify-between py-3 border-b border-gray-100 mb-4">
          <div>
            <p className="font-medium text-gray-800">启用勿扰时段</p>
            <p className="text-sm text-gray-500">在指定时间内不发送通知</p>
          </div>
          <Switch
            checked={settings.do_not_disturb_enabled}
            onChange={(checked) => updateSetting('do_not_disturb_enabled', checked)}
            disabled={!settings.enabled}
          />
        </div>

        {settings.do_not_disturb_enabled && (
          <div className="flex items-center space-x-4 py-3">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">开始时间</label>
              <TimePicker
                value={settings.do_not_disturb_start ? dayjs(settings.do_not_disturb_start, 'HH:mm') : null}
                onChange={(time) => updateSetting('do_not_disturb_start', time ? time.format('HH:mm') : '22:00')}
                format="HH:mm"
                minuteStep={15}
                className="w-full"
                disabled={!settings.enabled}
              />
            </div>
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">结束时间</label>
              <TimePicker
                value={settings.do_not_disturb_end ? dayjs(settings.do_not_disturb_end, 'HH:mm') : null}
                onChange={(time) => updateSetting('do_not_disturb_end', time ? time.format('HH:mm') : '08:00')}
                format="HH:mm"
                minuteStep={15}
                className="w-full"
                disabled={!settings.enabled}
              />
            </div>
          </div>
        )}
      </section>

      {/* 通知频率设置 */}
      <section className="bg-white rounded-xl shadow p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
          <Zap className="w-5 h-5 mr-2 text-blue-600" />
          通知频率
        </h2>
        
        {/* 每日通知上限 */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-medium text-gray-700">每日通知上限</label>
            <span className="text-sm font-semibold text-blue-600">{settings.max_notifications_per_day} 条/天</span>
          </div>
          <Slider
            min={0}
            max={50}
            value={settings.max_notifications_per_day}
            onChange={(value) => updateSetting('max_notifications_per_day', value)}
            disabled={!settings.enabled}
            marks={{
              0: '0',
              10: '10',
              20: '20',
              30: '30',
              40: '40',
              50: '50'
            }}
          />
          <p className="text-xs text-gray-500 mt-1">设置为0表示不限制</p>
        </div>

        {/* 通知间隔时间 */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-medium text-gray-700">通知间隔时间</label>
            <span className="text-sm font-semibold text-blue-600">{settings.min_notification_interval} 分钟</span>
          </div>
          <Slider
            min={0}
            max={120}
            step={5}
            value={settings.min_notification_interval}
            onChange={(value) => updateSetting('min_notification_interval', value)}
            disabled={!settings.enabled}
            marks={{
              0: '0',
              30: '30',
              60: '60',
              90: '90',
              120: '120'
            }}
          />
          <p className="text-xs text-gray-500 mt-1">同类型通知的最小间隔时间，设置为0表示不限制</p>
        </div>
      </section>
    </div>
  );
};

export default NotificationSettingsPage;