/**
 * Admin API Service
 * Story 7.1: 管理后台基础框架
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Admin Types
export interface AdminUser {
  id: number;
  email: string;
  username: string | null;
  full_name: string | null;
  is_superuser: boolean;
  is_active: boolean;
}

export interface AdminToken {
  access_token: string;
  token_type: string;
  user: AdminUser;
}

export interface AdminMenuItem {
  id: string;
  name: string;
  path: string;
  icon?: string;
  children?: AdminMenuItem[];
}

export interface AdminMenusResponse {
  menus: AdminMenuItem[];
}

// 获取 token
const getToken = (): string | null => {
  return localStorage.getItem('admin_token');
};

// 设置 token
export const setAdminToken = (token: string): void => {
  localStorage.setItem('admin_token', token);
};

// 移除 token
export const removeAdminToken = (): void => {
  localStorage.removeItem('admin_token');
};

// 获取 auth header
const getAuthHeader = () => {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// 创建 axios 实例
const adminApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 添加请求拦截器
adminApi.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 添加响应拦截器
adminApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      removeAdminToken();
      window.location.href = '/admin/login';
    }
    return Promise.reject(error);
  }
);

/**
 * 管理员登录
 * @param email 邮箱
 * @param password 密码
 * @returns 登录结果
 */
export const adminLogin = async (email: string, password: string): Promise<AdminToken> => {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  
  const response = await adminApi.post<AdminToken>(
    '/admin/auth/login',
    formData,
    {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    }
  );
  
  if (response.data.access_token) {
    setAdminToken(response.data.access_token);
  }
  
  return response.data;
};

/**
 * 获取当前管理员信息
 * @returns 管理员信息
 */
export const getAdminMe = async (): Promise<AdminUser> => {
  const response = await adminApi.get<AdminUser>('/admin/auth/me');
  return response.data;
};

/**
 * 获取管理员可访问的菜单
 * @returns 菜单列表
 */
export const getAdminMenus = async (): Promise<AdminMenusResponse> => {
  const response = await adminApi.get<AdminMenusResponse>('/admin/auth/menus');
  return response.data;
};

/**
 * 检查是否已登录
 * @returns 是否已登录
 */
export const isAdminLoggedIn = (): boolean => {
  return !!getToken();
};

/**
 * 管理员登出
 */
export const adminLogout = (): void => {
  removeAdminToken();
};

/**
 * Feature Flag Types
 */
export interface FeatureFlag {
  id: string;
  config_key: string;
  config_value: {
    enabled: boolean;
    description?: string;
    [key: string]: any;
  };
  config_type: string;
  config_category: string;
  environment: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * 获取所有功能开关
 * @param environment 环境 (all/development/staging/production)
 * @returns 功能开关列表
 */
export const getFeatureFlags = async (environment?: string): Promise<FeatureFlag[]> => {
  const params = environment ? { config_type: 'feature_flag', environment } : { config_type: 'feature_flag' };
  const response = await adminApi.get('/admin/configs', { params });
  return response.data.items;
};

/**
 * 获取单个功能开关
 * @param configKey 配置 key
 * @param environment 环境
 * @returns 功能开关
 */
export const getFeatureFlag = async (configKey: string, environment: string = 'all'): Promise<FeatureFlag> => {
  const response = await adminApi.get(`/admin/configs/${configKey}`, { params: { environment } });
  return response.data;
};

/**
 * 更新功能开关
 * @param configKey 配置 key
 * @param enabled 是否启用
 * @param reason 变更原因
 * @returns 更新后的功能开关
 */
export const updateFeatureFlag = async (
  configKey: string, 
  enabled: boolean,
  reason?: string
): Promise<FeatureFlag> => {
  const response = await adminApi.put(
    `/admin/configs/${configKey}`,
    { enabled },
    { params: { reason } }
  );
  return response.data;
};

/**
 * System Config Types
 */
export interface SystemConfig {
  id: string;
  config_key: string;
  config_value: any;
  config_type: string;
  config_category: string;
  environment: string;
  is_active: boolean;
  description?: string;
  created_at: string;
  updated_at: string;
}

/**
 * 获取所有系统配置
 * @param configType 配置类型
 * @param environment 环境
 * @returns 系统配置列表
 */
export const getSystemConfigs = async (
  configType?: string,
  environment?: string
): Promise<SystemConfig[]> => {
  const params: any = {};
  if (configType) params.config_type = configType;
  if (environment) params.environment = environment;
  
  const response = await adminApi.get('/admin/configs', { params });
  return response.data.items;
};

/**
 * 更新系统配置
 * @param configKey 配置 key
 * @param configValue 新的配置值
 * @param reason 变更原因
 * @returns 更新后的配置
 */
export const updateSystemConfig = async (
  configKey: string,
  configValue: any,
  reason?: string
): Promise<SystemConfig> => {
  const response = await adminApi.put(
    `/admin/configs/${configKey}`,
    configValue,
    { params: { reason } }
  );
  return response.data;
};

/**
 * Audit Log Types
 */
export interface AuditLog {
  id: string;
  config_id: string;
  old_value: any;
  new_value: any;
  changed_by: string;
  reason?: string;
  created_at: string;
}

/**
 * 获取配置变更日志
 * @param configKey 配置 key
 * @param limit 限制数量
 * @returns 变更日志列表
 */
export const getAuditLogs = async (
  configKey?: string,
  limit: number = 50
): Promise<AuditLog[]> => {
  const params: any = { limit };
  if (configKey) params.config_key = configKey;
  
  const response = await adminApi.get('/admin/configs/logs', { params });
  return response.data.items;
};
