import api from '@/api/client';

export interface RegisterData {
  email: string;
  username?: string;
  password: string;
  confirm_password: string;
  full_name?: string;
}

export interface LoginData {
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    email: string;
    username?: string;
    full_name?: string;
  };
}

export const authService = {
  /**
   * 用户注册
   */
  register: async (data: RegisterData): Promise<AuthResponse> => {
    const response = await api.client.post('/auth/register', data);
    return response.data;
  },

  /**
   * 用户登录 - 使用 api client 内置方法
   */
  login: async (data: LoginData): Promise<AuthResponse> => {
    return await api.login(data.username, data.password);
  },

  /**
   * 获取当前用户信息
   */
  getCurrentUser: async (token: string) => {
    const response = await api.client.get('/auth/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },

  /**
   * 更新密码
   */
  updatePassword: async (
    token: string,
    currentPassword: string,
    newPassword: string
  ) => {
    const response = await api.client.post(
      '/auth/change-password',
      null,
      {
        params: {
          old_password: currentPassword,
          new_password: newPassword,
        },
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  },
};
