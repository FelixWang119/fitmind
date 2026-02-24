# 架构模式分析

## 概述

本项目采用分层架构模式，包含清晰的责任分离和模块化设计。以下是项目的主要架构模式和设计决策。

## 后端架构模式

### 1. 分层架构 (Layered Architecture)

```
┌─────────────────────────────────────┐
│          API层 (Endpoints)          │
│  - 请求处理                         │
│  - 参数验证                         │
│  - 响应格式化                       │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│         服务层 (Services)           │
│  - 业务逻辑                         │
│  - 事务管理                         │
│  - 外部服务集成                     │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│         数据访问层 (Models)         │
│  - 数据模型定义                     │
│  - 数据库操作                       │
│  - 关系映射                         │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│         数据库层 (Database)         │
│  - PostgreSQL / SQLite              │
│  - 数据存储                         │
│  - 事务处理                         │
└─────────────────────────────────────┘
```

### 2. 依赖注入模式
- **配置管理**: 通过 `app/core/config.py` 集中管理配置
- **服务实例化**: 在需要时创建服务实例，支持依赖注入
- **数据库会话**: 通过FastAPI依赖注入系统管理数据库会话

### 3. 仓储模式 (Repository Pattern)
- **数据访问抽象**: 通过SQLAlchemy模型提供数据访问抽象
- **业务逻辑分离**: 服务层不直接操作数据库，通过模型层访问
- **测试友好**: 便于模拟数据访问层进行单元测试

### 4. 策略模式 (Strategy Pattern)
- **AI服务选择**: 根据内容自动选择AI角色（行为教练、营养师、情感支持）
- **图像分析策略**: 根据环境配置选择真实API或模拟模式
- **认证策略**: 支持多种认证方式（JWT、OAuth等）

## 前端架构模式

### 1. 组件化架构 (Component-Based Architecture)

```
┌─────────────────────────────────────┐
│         页面组件 (Pages)            │
│  - 路由级组件                       │
│  - 页面布局                         │
│  - 数据获取                         │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│         功能组件 (Features)         │
│  - 业务功能模块                     │
│  - 复杂交互逻辑                     │
│  - 状态管理                         │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│         基础组件 (UI Components)    │
│  - 可复用UI组件                     │
│  - 样式和交互                       │
│  - 无状态/有状态组件                │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│         工具组件 (Utilities)        │
│  - Hooks                            │
│  - 工具函数                         │
│  - 类型定义                         │
└─────────────────────────────────────┘
```

### 2. 状态管理模式
- **Zustand轻量级状态管理**: 全局状态管理
- **React Context**: 局部状态共享
- **组件状态**: 使用React Hooks管理组件内部状态
- **状态持久化**: 支持状态持久化到localStorage

### 3. 容器/展示模式 (Container/Presentational Pattern)
- **容器组件**: 处理业务逻辑、数据获取和状态管理
- **展示组件**: 专注于UI渲染和用户交互
- **关注点分离**: 逻辑和展示分离，提高可测试性

### 4. 自定义Hooks模式
- **逻辑复用**: 通过自定义Hooks复用业务逻辑
- **关注点分离**: 将副作用和状态逻辑从组件中提取
- **测试友好**: 便于单独测试业务逻辑

## 集成架构模式

### 1. 客户端-服务器模式 (Client-Server Pattern)
- **前后端分离**: 前端作为客户端，后端作为服务器
- **RESTful API**: 通过HTTP RESTful API进行通信
- **无状态通信**: 服务器不保存客户端状态，通过令牌认证

### 2. API网关模式 (API Gateway Pattern)
- **统一入口**: 所有API请求通过统一入口点
- **路由分发**: 根据路径将请求分发到相应端点
- **中间件处理**: 统一处理认证、日志、错误等

### 3. 认证授权模式
- **JWT令牌认证**: 无状态认证机制
- **令牌刷新**: 支持访问令牌和刷新令牌
- **角色权限**: 基于角色的访问控制（RBAC）

## 关键设计决策

### 1. 千问API集成设计
```python
# 配置集中管理
class Settings(BaseSettings):
    QWEN_API_KEY: Optional[str] = None
    QWEN_API_BASE: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_API_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    QWEN_MODEL: str = "qwen-plus"

# 服务抽象层
class AIService:
    def __init__(self):
        self.mock_mode = settings.ENVIRONMENT == "development" and not settings.QWEN_API_KEY
    
    async def get_response(self, message: str, context: Optional[Dict] = None):
        if self.mock_mode:
            return await self._get_mock_response(message, context)
        else:
            return await self._get_qwen_response(message, context)
```

**设计优势**:
- **环境感知**: 根据环境自动选择真实API或模拟模式
- **配置驱动**: 通过环境变量控制API密钥和端点
- **错误恢复**: 提供后备数据机制，确保服务可用性
- **抽象隔离**: 业务逻辑与具体AI服务实现分离

### 2. 测试用户固化设计
```python
# 测试用户管理策略
class TestUserManager:
    def __init__(self):
        self.test_users = self._load_test_users()
    
    def get_or_create_test_user(self, email: str):
        # 1. 检查是否存在测试用户
        # 2. 如果不存在则创建
        # 3. 返回用户ID和认证令牌
        # 4. 持久化用户信息避免重复创建
        pass
```

**设计原则**:
- **幂等性**: 多次调用返回相同结果
- **持久化**: 测试用户信息持久化存储
- **隔离性**: 测试用户与生产用户隔离
- **可配置**: 支持自定义测试用户配置

### 3. 测试资源管理设计
```
backend/tests/mealimg/
├── lunch.jpg      # 测试图片1
├── meal3.png      # 测试图片2
├── meal4.jpg      # 测试图片3
├── meal5.jpg      # 测试图片4
└── meal6.jpg      # 测试图片5
```

**管理策略**:
- **目录组织**: 按功能分类组织测试资源
- **版本控制**: 测试资源纳入版本控制
- **大小控制**: 控制测试资源文件大小
- **命名规范**: 使用有意义的文件名

### 4. 错误处理设计
```python
# 统一错误响应格式
{
    "detail": "错误描述",
    "status_code": 400,
    "error_code": "VALIDATION_ERROR",
    "timestamp": "2024-01-01T00:00:00Z"
}

# 结构化错误处理
try:
    result = await service.process(request)
except ValidationError as e:
    raise HTTPException(status_code=400, detail=str(e))
except AuthenticationError as e:
    raise HTTPException(status_code=401, detail="认证失败")
except Exception as e:
    logger.error("处理请求时发生错误", error=str(e))
    raise HTTPException(status_code=500, detail="服务器内部错误")
```

## 扩展性考虑

### 1. 水平扩展
- **无状态服务**: 后端服务无状态，支持水平扩展
- **数据库连接池**: 支持数据库连接池，提高并发能力
- **缓存层**: Redis缓存支持，减轻数据库压力

### 2. 垂直扩展
- **模块化设计**: 各模块独立，便于功能扩展
- **插件架构**: 支持插件式扩展新功能
- **配置驱动**: 通过配置启用/禁用功能

### 3. 技术债务管理
- **类型安全**: TypeScript和mypy提供类型安全
- **代码规范**: 统一的代码规范和检查工具
- **测试覆盖**: 全面的测试覆盖确保代码质量
- **文档完整**: 完整的API文档和架构文档

## 性能考虑

### 1. 前端性能优化
- **代码分割**: Vite支持自动代码分割
- **懒加载**: 路由和组件懒加载
- **缓存策略**: 合理的HTTP缓存策略
- **图片优化**: 图片压缩和懒加载

### 2. 后端性能优化
- **异步处理**: FastAPI原生异步支持
- **数据库优化**: 查询优化和索引
- **缓存策略**: Redis缓存常用数据
- **连接池**: 数据库连接池管理

### 3. 网络性能优化
- **CDN部署**: 前端静态资源CDN部署
- **API压缩**: Gzip/Brotli压缩
- **连接复用**: HTTP/2连接复用
- **请求合并**: 批量请求减少网络往返