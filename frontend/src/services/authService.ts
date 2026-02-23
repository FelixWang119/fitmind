import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

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
    const response = await axios.post(`${API_BASE_URL}/auth/register`, data);
    return response.data;
  },

  /**
   * 用户登录
   */
  login: async (data: LoginData): Promise<AuthResponse> => {
    const formData = new FormData();
    formData.append('username', data.username);
    formData.append('password', data.password);

    const response = await axios.post(`${API_BASE_URL}/auth/login`, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  /**
   * 获取当前用户信息
   */
  getCurrentUser: async (token: string) => {
    const response = await axios.get(`${API_BASE_URL}/auth/me`, {
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
    const response = await axios.post(
      `${API_BASE_URL}/auth/change-password`,
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
