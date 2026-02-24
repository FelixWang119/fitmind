# 状态管理文档 - 前端部分

## 概述

本文档详细描述了前端应用的状态管理架构、数据流和组件交互模式。前端使用React + TypeScript + Zustand构建，采用现代状态管理最佳实践。

## 状态管理架构

### 1. 状态分层

```
┌─────────────────────────────────────┐
│       全局状态 (Global State)       │
│  - 用户认证状态                     │
│  - 应用配置                         │
│  - 主题设置                         │
│  - 通知系统                         │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│       页面状态 (Page State)         │
│  - 当前页面数据                     │
│  - 表单状态                         │
│  - 加载状态                         │
│  - 错误状态                         │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│       组件状态 (Component State)    │
│  - UI交互状态                       │
│  - 本地数据                         │
│  - 动画状态                         │
└─────────────────────────────────────┘
```

### 2. 状态管理库选择

**Zustand** 作为主要状态管理库，原因：
- **轻量级**: 最小化包大小影响
- **类型安全**: 完整的TypeScript支持
- **简单API**: 易于学习和使用
- **持久化支持**: 内置状态持久化
- **中间件支持**: 灵活的中间件系统

## 认证状态管理

### 1. 认证存储 (authStore.ts)

**位置**: `/frontend/src/store/authStore.ts`

**状态接口**:
```typescript
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
```

**持久化配置**:
```typescript
persist(
  (set, get) => ({ ... }),
  {
    name: 'auth-storage',
    partialize: (state) => ({
      token: state.token,
      isAuthenticated: state.isAuthenticated,
    }),
  }
)
```

### 2. 认证流程

#### 登录流程
```typescript
// 1. 用户输入邮箱和密码
// 2. 调用 authStore.login(email, password)
// 3. 发送登录请求到后端
// 4. 接收访问令牌
// 5. 存储令牌到localStorage
// 6. 获取用户信息
// 7. 更新认证状态
```

#### 注册流程
```typescript
// 1. 用户填写注册信息
// 2. 调用 authStore.register(userData)
// 3. 发送注册请求
// 4. 注册成功后自动登录
```

#### 认证检查
```typescript
// 应用启动时执行
// 1. 检查localStorage中的令牌
// 2. 如果存在令牌，验证令牌有效性
// 3. 获取当前用户信息
// 4. 更新认证状态
```

### 3. 错误处理
```typescript
try {
  await authStore.login(email, password);
} catch (error: any) {
  // 提取错误信息
  let errorMessage = '登录失败';
  if (error.response?.data?.detail) {
    const detail = error.response.data.detail;
    if (typeof detail === 'object' && detail.message) {
      errorMessage = detail.message;
    } else if (typeof detail === 'string') {
      errorMessage = detail;
    }
  }
  // 更新错误状态
  authStore.setState({ error: errorMessage });
}
```

## API客户端集成

### 1. API客户端配置

**位置**: `/frontend/src/api/client.ts`

**基础配置**:
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### 2. 请求拦截器
```typescript
// 请求拦截器 - 添加认证令牌
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);
```

### 3. 响应拦截器
```typescript
// 响应拦截器 - 处理认证错误
client.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // 处理未授权错误
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### 4. API方法组织
```typescript
class ApiClient {
  // 认证相关
  async login(email: string, password: string) { ... }
  async register(userData: any) { ... }
  async getCurrentUser() { ... }
  
  // 仪表板相关
  async getDashboardOverview() { ... }
  async getQuickStats() { ... }
  
  // 习惯管理
  async getHabits(activeOnly: boolean = true) { ... }
  async createHabit(data: any) { ... }
  
  // 餐食管理
  async getDailyMeals(date?: string) { ... }
  async createMeal(mealData: any) { ... }
  
  // AI聊天
  async sendMessage(message: string, conversationId?: number) { ... }
  
  // 营养分析
  async analyzeFoodImage(imageData: string, date?: string) { ... }
  
  // 游戏化
  async getGamificationOverview() { ... }
  async claimDailyReward() { ... }
}
```

## 组件状态管理

### 1. 页面组件状态模式

#### 数据获取模式
```typescript
function UserDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    fetchData();
  }, []);
  
  const fetchData = async () => {
    try {
      setLoading(true);
      const result = await api.getDashboardOverview();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay error={error} />;
  
  return <Dashboard data={data} />;
}
```

#### 表单状态模式
```typescript
function MealForm() {
  const [formData, setFormData] = useState({
    meal_type: 'lunch',
    name: '',
    calories: 0,
    protein: 0,
    carbs: 0,
    fat: 0,
  });
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.createMeal(formData);
      // 处理成功
    } catch (error) {
      // 处理错误
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {/* 表单字段 */}
    </form>
  );
}
```

### 2. 自定义Hooks模式

#### 数据获取Hook
```typescript
function useDashboardData() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const result = await api.getDashboardOverview();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);
  
  useEffect(() => {
    fetchData();
  }, [fetchData]);
  
  return { data, loading, error, refetch: fetchData };
}
```

#### 表单管理Hook
```typescript
function useForm(initialState) {
  const [formData, setFormData] = useState(initialState);
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
    // 清除字段错误
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: undefined,
      }));
    }
  }, [errors]);
  
  const validate = useCallback(() => {
    const newErrors = {};
    // 验证逻辑
    return newErrors;
  }, [formData]);
  
  const handleSubmit = useCallback(async (callback) => {
    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }
    
    setIsSubmitting(true);
    try {
      await callback(formData);
    } catch (error) {
      // 处理错误
    } finally {
      setIsSubmitting(false);
    }
  }, [formData, validate]);
  
  return {
    formData,
    errors,
    isSubmitting,
    handleChange,
    handleSubmit,
    setFormData,
  };
}
```

## 数据流模式

### 1. 单向数据流
```
用户操作 → 事件处理 → 状态更新 → UI渲染
```

### 2. 组件通信
- **父传子**: Props传递
- **子传父**: 回调函数
- **兄弟组件**: 通过共同父组件
- **跨组件**: Zustand全局状态

### 3. 状态更新策略
```typescript
// 乐观更新
const handleCompleteHabit = async (habitId) => {
  // 1. 立即更新UI
  setHabits(prev => prev.map(h => 
    h.id === habitId ? { ...h, completed: true } : h
  ));
  
  try {
    // 2. 发送API请求
    await api.completeHabit(habitId, {});
  } catch (error) {
    // 3. 失败时回滚
    setHabits(prev => prev.map(h => 
      h.id === habitId ? { ...h, completed: false } : h
    ));
    // 显示错误
  }
};
```

## 性能优化

### 1. 状态分割
- **按功能分割**: 认证状态、用户数据、UI状态分开管理
- **按页面分割**: 不同页面的状态独立管理
- **按生命周期分割**: 临时状态和持久状态分开

### 2. 状态选择器
```typescript
// 使用选择器避免不必要的重渲染
const user = useAuthStore(state => state.user);
const isAuthenticated = useAuthStore(state => state.isAuthenticated);

// 而不是
const { user, isAuthenticated } = useAuthStore();
```

### 3. 状态记忆化
```typescript
// 使用useMemo记忆化派生状态
const completedHabits = useMemo(() => {
  return habits.filter(h => h.completed);
}, [habits]);

// 使用useCallback记忆化回调函数
const handleDelete = useCallback((id) => {
  // 处理删除
}, []);
```

## 错误边界和恢复

### 1. 错误边界组件
```typescript
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  
  componentDidCatch(error, errorInfo) {
    // 记录错误到监控系统
    console.error('Error caught by boundary:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />;
    }
    return this.props.children;
  }
}
```

### 2. 网络错误处理
```typescript
// 重试机制
const fetchWithRetry = async (url, options, retries = 3) => {
  for (let i = 0; i < retries; i++) {
    try {
      return await fetch(url, options);
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, i)));
    }
  }
};
```

### 3. 离线支持
```typescript
// 检查网络状态
const [isOnline, setIsOnline] = useState(navigator.onLine);

useEffect(() => {
  const handleOnline = () => setIsOnline(true);
  const handleOffline = () => setIsOnline(false);
  
  window.addEventListener('online', handleOnline);
  window.addEventListener('offline', handleOffline);
  
  return () => {
    window.removeEventListener('online', handleOnline);
    window.removeEventListener('offline', handleOffline);
  };
}, []);
```

## 测试策略

### 1. 状态存储测试
```typescript
describe('authStore', () => {
  it('should handle login successfully', async () => {
    const { result } = renderHook(() => useAuthStore());
    
    await act(async () => {
      await result.current.login('test@example.com', 'password');
    });
    
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).not.toBeNull();
  });
  
  it('should handle login failure', async () => {
    const { result } = renderHook(() => useAuthStore());
    
    await act(async () => {
      try {
        await result.current.login('wrong@example.com', 'wrong');
      } catch (error) {
        // 预期错误
      }
    });
    
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.error).not.toBeNull();
  });
});
```

### 2. 组件状态测试
```typescript
describe('UserDashboard', () => {
  it('should display loading state initially', () => {
    render(<UserDashboard />);
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });
  
  it('should display data after loading', async () => {
    render(<UserDashboard />);
    await waitFor(() => {
      expect(screen.getByText('Dashboard Overview')).toBeInTheDocument();
    });
  });
});
```

## 最佳实践

### 1. 状态管理原则
- **单一数据源**: 相同数据只有一个来源
- **状态最小化**: 只存储必要状态
- **状态可预测**: 状态变化可追踪和调试
- **状态可测试**: 状态逻辑易于测试

### 2. 代码组织
- **按功能组织**: 相关状态和逻辑放在一起
- **关注点分离**: UI逻辑和业务逻辑分离
- **可复用性**: 提取可复用的状态逻辑
- **可维护性**: 清晰的命名和结构

### 3. 开发工作流
1. **设计状态结构**: 先设计状态结构，再实现组件
2. **实现状态逻辑**: 实现状态更新和业务逻辑
3. **连接组件**: 将组件连接到状态
4. **测试验证**: 测试状态逻辑和组件行为
5. **性能优化**: 优化状态更新和渲染性能