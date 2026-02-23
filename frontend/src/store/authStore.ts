import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { api } from '../api/client';
import type { User } from '../types';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: any) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: true,
      error: null,

      login: async (email: string, password: string) => {
        try {
          set({ error: null });
          const response = await api.login(email, password);
          const { access_token } = response;
          
          localStorage.setItem('token', access_token);
          
          // Get user info
          const user = await api.getCurrentUser();
          
          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          console.error('Login failed:', error);
          // Extract error message from API response
          let errorMessage = '登录失败';
          if (error.response?.data?.detail) {
            const detail = error.response.data.detail;
            if (typeof detail === 'object' && detail.message) {
              errorMessage = detail.message;
            } else if (typeof detail === 'string') {
              errorMessage = detail;
            }
          }
          set({ error: errorMessage });
          throw error;
        }
      },

      register: async (userData: any) => {
        try {
          set({ error: null });
          await api.register(userData);
          // Auto login after registration
          await get().login(userData.email, userData.password);
        } catch (error: any) {
          console.error('Registration failed:', error);
          // Extract error message from API response
          let errorMessage = '注册失败';
          if (error.response?.data?.detail) {
            const detail = error.response.data.detail;
            if (typeof detail === 'object' && detail.message) {
              errorMessage = detail.message;
            } else if (typeof detail === 'string') {
              errorMessage = detail;
            }
          }
          set({ error: errorMessage });
          throw error;
        }
      },

      logout: () => {
        localStorage.removeItem('token');
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        });
      },

      clearError: () => {
        set({ error: null });
      },

      checkAuth: async () => {
        const token = localStorage.getItem('token');
        
        if (!token) {
          set({ isLoading: false, error: null });
          return;
        }

        try {
          const user = await api.getCurrentUser();
          set({
            user,
            token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error) {
          console.error('Auth check failed:', error);
          localStorage.removeItem('token');
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);