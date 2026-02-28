# 多部分集成架构

本文档描述体重管理AI代理项目的多部分集成架构，包括前端、后端、数据库和AI服务的交互方式。

## 目录

1. [架构概述](#架构概述)
2. [组件交互](#组件交互)
3. [数据流](#数据流)
4. [API集成](#api集成)
5. [认证与授权](#认证与授权)
6. [错误处理](#错误处理)
7. [性能考虑](#性能考虑)
8. [扩展性设计](#扩展性设计)

## 架构概述

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                       用户界面层                             │
├─────────────────────────────────────────────────────────────┤
│  React前端 (TypeScript)                                      │
│  • 用户界面组件                                              │
│  • 状态管理 (Zustand)                                        │
│  • 路由 (React Router)                                       │
│  • API客户端 (Axios)                                         │
└──────────────┬──────────────────────────────────────────────┘
               │ HTTP/HTTPS (REST API + WebSocket)
               ▼
┌─────────────────────────────────────────────────────────────┐
│                       应用服务层                             │
├─────────────────────────────────────────────────────────────┤
│  FastAPI后端 (Python)                                        │
│  • REST API端点                                              │
│  • 业务逻辑服务                                              │
│  • 数据验证 (Pydantic)                                       │
│  • 认证授权 (JWT)                                            │
└──────────────┬──────────────────────────────────────────────┘
               │ 数据库操作 + AI服务调用
               ▼
┌─────────────────────────────────────────────────────────────┐
│                       数据与AI层                             │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL数据库  │  通义千问AI服务                         │
│  • 用户数据        │  • 对话模型 (qwen-plus)                 │
│  • 健康记录        │  • 图像识别 (qwen-vl-max)               │
│  • 习惯追踪        │  • 营养分析                             │
│  • 游戏化数据      │  • 营养分析                             │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈集成

| 组件 | 技术 | 版本 | 集成方式 |
|------|------|------|----------|
| **前端** | React + TypeScript | 18.2.0 | Vite构建，Axios HTTP客户端 |
| **后端** | FastAPI + Python | 3.11+ | REST API，WebSocket支持 |
| **数据库** | PostgreSQL | 15 | SQLAlchemy ORM，Alembic迁移 |
| **AI服务** | 通义千问 | - | HTTP API，兼容OpenAI格式 |
| **容器化** | Docker + Compose | 20.10+ | 多容器编排 |
| **监控** | Structlog + Prometheus | - | 结构化日志，指标收集 |

## 组件交互

### 前端-后端交互

**通信协议:**
- **主要**: HTTP/HTTPS (REST API)
- **辅助**: WebSocket (实时更新)
- **数据格式**: JSON

**API客户端配置:**
```typescript
// frontend/src/api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器（添加认证令牌）
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器（处理令牌刷新）
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      // 尝试刷新令牌
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post('/api/v1/auth/refresh', {
            refresh_token: refreshToken,
          });
          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        } catch (refreshError) {
          // 刷新失败，跳转到登录页
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);
```

### 后端-数据库交互

**ORM配置:**
```python
# backend/app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 依赖注入数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**数据模型示例:**
```python
# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 后端-AI服务交互

**AI服务客户端:**
```python
# backend/app/services/ai_service.py
import httpx
from app.core.config import settings

class AIService:
    def __init__(self):
        self.base_url = settings.QWEN_BASE_URL
        self.api_key = settings.QWEN_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    async def chat_completion(self, messages, model="qwen-plus"):
        """普通对话"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
    
    async def analyze_food_image(self, image_data, model="qwen-vl-max"):
        """食物图像分析"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "分析这张食物图片，识别食物种类、估算卡路里和营养成分。"},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}},
                            ],
                        }
                    ],
                    "max_tokens": 1000,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json()
```

## 数据流

### 用户注册流程

```
1. 用户填写注册表单
   ↓
2. 前端发送POST /api/v1/auth/register
   ↓
3. 后端验证数据，创建用户记录
   ↓
4. 数据库保存用户信息
   ↓
5. 后端生成JWT令牌
   ↓
6. 前端接收令牌并保存
   ↓
7. 用户自动登录
```

### 食物图像分析流程

```
1. 用户上传食物图片
   ↓
2. 前端将图片转换为Base64
   ↓
3. 发送POST /api/v1/nutrition/analyze-image
   ↓
4. 后端调用AI服务 (qwen-vl-max模型)
   ↓
5. AI服务返回分析结果
   ↓
6. 后端解析结果，保存到数据库
   ↓
7. 前端显示分析结果
```

### 实时对话流程

```
1. 用户发送消息
   ↓
2. 前端建立WebSocket连接
   ↓
3. 发送消息到 /ws/chat
   ↓
4. 后端接收消息，调用AI服务 (qwen-plus模型)
   ↓
5. AI服务流式返回响应
   ↓
6. 后端通过WebSocket实时推送
   ↓
7. 前端实时显示AI回复
```

## API集成

### REST API设计

**API版本:** `/api/v1/`
**认证方式:** Bearer Token (JWT)
**响应格式:** JSON

**主要API端点:**

| 模块 | 端点 | 方法 | 描述 |
|------|------|------|------|
| **认证** | `/auth/register` | POST | 用户注册 |
| | `/auth/login` | POST | 用户登录 |
| | `/auth/refresh` | POST | 刷新令牌 |
| | `/auth/me` | GET | 获取当前用户 |
| **健康** | `/health/records` | GET | 获取健康记录 |
| | `/health/records` | POST | 创建健康记录 |
| **习惯** | `/habits/` | GET | 获取习惯列表 |
| | `/habits/` | POST | 创建习惯 |
| | `/habits/{id}/complete` | POST | 完成习惯 |
| **营养** | `/nutrition/analyze-image` | POST | 分析食物图像 |
| | `/nutrition/recommendations` | GET | 获取营养建议 |
| **情感** | `/emotional-support/check-in` | POST | 情感签到 |
| **游戏化** | `/gamification/badges` | GET | 获取徽章 |
| | `/gamification/points` | GET | 获取积分 |

### WebSocket API

**连接端点:** `/ws/chat`
**协议:** WebSocket
**消息格式:** JSON

**消息类型:**
```json
{
  "type": "chat_message",
  "content": "用户消息内容",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

**响应类型:**
```json
{
  "type": "ai_response",
  "content": "AI回复内容",
  "timestamp": "2024-01-20T10:30:05Z",
  "is_complete": true
}
```

### 第三方服务集成

#### 通义千问AI服务

**配置:**
```python
# backend/app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    QWEN_API_KEY: str
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_CHAT_MODEL: str = "qwen-plus"
    QWEN_VISION_MODEL: str = "qwen-vl-max"
    
    class Config:
        env_file = ".env"
```

**使用模式:**
- **常规对话**: 使用 `qwen-plus` 模型
- **图像识别**: 使用 `qwen-vl-max` 模型
- **相同API密钥**: 两种模型使用相同的API密钥配置

#### 邮件服务 (可选)

**配置:**
```python
# 邮件服务配置
SMTP_HOST: str = "smtp.gmail.com"
SMTP_PORT: int = 587
SMTP_USER: str = ""
SMTP_PASSWORD: str = ""
EMAIL_FROM: str = "noreply@weightai.com"
```

## 认证与授权

### JWT认证流程

1. **用户登录**
   ```http
   POST /api/v1/auth/login
   Content-Type: application/json
   
   {
     "username": "user@example.com",
     "password": "password123"
   }
   ```

2. **令牌响应**
   ```json
   {
     "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
     "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
     "token_type": "bearer",
     "expires_in": 1800
   }
   ```

3. **API请求认证**
   ```http
   GET /api/v1/auth/me
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
   ```

### 权限控制

**基于角色的访问控制:**
```python
# backend/app/core/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def require_role(role: str):
    """角色要求装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user or current_user.role != role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### 令牌刷新机制

```python
# 令牌刷新端点
@app.post("/auth/refresh")
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            refresh_request.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # 生成新的访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
```

## 错误处理

### 统一错误响应格式

```json
{
  "detail": "错误描述",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-20T10:30:00Z",
  "path": "/api/v1/endpoint"
}
```

### 错误分类

| 错误类型 | HTTP状态码 | 错误代码 | 处理方式 |
|----------|------------|----------|----------|
| **验证错误** | 400 | `VALIDATION_ERROR` | 客户端检查输入 |
| **认证错误** | 401 | `AUTHENTICATION_ERROR` | 重新登录或刷新令牌 |
| **权限错误** | 403 | `PERMISSION_DENIED` | 检查用户权限 |
| **资源不存在** | 404 | `RESOURCE_NOT_FOUND` | 检查资源ID |
| **冲突错误** | 409 | `RESOURCE_CONFLICT` | 检查唯一性约束 |
| **服务器错误** | 500 | `INTERNAL_SERVER_ERROR` | 服务器端修复 |
| **服务不可用** | 503 | `SERVICE_UNAVAILABLE` | 重试或等待 |

### 全局异常处理器

```python
# backend/app/core/exception_handlers.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "error_code": "VALIDATION_ERROR",
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
        },
    )

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": "Resource conflict",
            "error_code": "RESOURCE_CONFLICT",
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
        },
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": getattr(exc, "error_code", "HTTP_ERROR"),
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
        },
    )
```

## 性能考虑

### 数据库优化

1. **索引策略**
   ```python
   # 为常用查询字段创建索引
   class User(Base):
       __tablename__ = "users"
       
       id = Column(Integer, primary_key=True, index=True)
       email = Column(String, unique=True, index=True)  # 登录查询
       username = Column(String, unique=True, index=True)  # 用户查找
       created_at = Column(DateTime, index=True)  # 时间范围查询
   ```

2. **查询优化**
   ```python
   # 使用selectinload避免N+1查询
   from sqlalchemy.orm import selectinload
   
   # 不好的做法
   users = db.query(User).all()
   for user in users:
       habits = user.habits  # 每次循环都执行查询
   
   # 好的做法
   users = db.query(User).options(selectinload(User.habits)).all()
   for user in users:
       habits = user.habits  # 已预加载
   ```

3. **分页处理**
   ```python
   from fastapi_pagination import Page, add_pagination, paginate
   
   @app.get("/users", response_model=Page[UserSchema])
   async def get_users(db: Session = Depends(get_db)):
       users = db.query(User).order_by(User.created_at.desc())
       return paginate(users)
   ```

### 缓存策略

1. **Redis缓存**
   ```python
   import redis
   from functools import wraps
   
   redis_client = redis.Redis.from_url(settings.REDIS_URL)
   
   def cache_response(ttl: int = 300):
       def decorator(func):
           @wraps(func)
           async def wrapper(*args, **kwargs):
               # 生成缓存键
               cache_key = f"{func.__module__}:{func.__name__}:{args}:{kwargs}"
               
               # 尝试从缓存获取
               cached = redis_client.get(cache_key)
               if cached:
                   return json.loads(cached)
               
               # 执行函数
               result = await func(*args, **kwargs)
               
               # 缓存结果
               redis_client.setex(cache_key, ttl, json.dumps(result))
               
               return result
           return wrapper
       return decorator
   ```

2. **缓存使用场景**
   - 用户配置信息 (TTL: 1小时)
   - 营养建议 (TTL: 24小时)
   - 游戏化徽章列表 (TTL: 1小时)
   - API速率限制计数

### API性能监控

1. **响应时间监控**
   ```python
   import time
   from fastapi import Request
   
   @app.middleware("http")
   async def add_process_time_header(request: Request, call_next):
       start_time = time.time()
       response = await call_next(request)
       process_time = time.time() - start_time
       response.headers["X-Process-Time"] = str(process_time)
       
       # 记录慢请求
       if process_time > 1.0:  # 超过1秒
           logger.warning(
               "Slow request",
               path=request.url.path,
               method=request.method,
               process_time=process_time,
           )
       
       return response
   ```

2. **Prometheus指标**
   ```python
   from prometheus_fastapi_instrumentator import Instrumentator
   
   instrumentator = Instrumentator().instrument(app)
   
   @app.on_event("startup")
   async def startup():
       instrumentator.expose(app)
   ```

## 扩展性设计

### 水平扩展

1. **无状态后端**
   - 所有状态存储在数据库或Redis中
   - 支持多个后端实例
   - 使用负载均衡器分发请求

2. **数据库读写分离**
   ```python
   # 配置主从数据库
   class DatabaseConfig:
       MASTER_URL = "postgresql://master_host/db"
       REPLICA_URL = "postgresql://replica_host/db"
       
       @staticmethod
       def get_read_session():
           return create_engine(REPLICA_URL)
       
       @staticmethod
       def get_write_session():
           return create_engine(MASTER_URL)
   ```

### 微服务架构准备

1. **服务拆分可能性**
   ```
   当前单体架构 → 未来微服务架构
   
   weight-management-ai-backend
   ├── auth-service (认证授权)
   ├── user-service (用户管理)
   ├── health-service (健康追踪)
   ├── nutrition-service (营养分析)
   ├── gamification-service (游戏化)
   └── ai-gateway (AI服务网关)
   ```

2. **API网关模式**
   ```python
   # 未来可实现的API网关
   from fastapi import FastAPI
   import httpx
   
   app = FastAPI()
   
   SERVICE_URLS = {
       "auth": "http://auth-service:8000",
       "user": "http://user-service:8001",
       "health": "http://health-service:8002",
   }
   
   @app.get("/api/{service}/{path:path}")
   async def proxy_request(service: str, path: str, request: Request):
       if service not in SERVICE_URLS:
           raise HTTPException(status_code=404, detail="Service not found")
       
       service_url = SERVICE_URLS[service]
       async with httpx.AsyncClient() as client:
           response = await client.request(
               method=request.method,
               url=f"{service_url}/{path}",
               headers=dict(request.headers),
               params=dict(request.query_params),
               content=await request.body(),
           )
           
           return Response(
               content=response.content,
               status_code=response.status_code,
               headers=dict(response.headers),
           )
   ```

### 消息队列集成准备

1. **异步任务处理**
   ```python
   # 使用Celery处理异步任务
   from celery import Celery
   
   celery_app = Celery(
       "weight_ai_tasks",
       broker=settings.REDIS_URL,
       backend=settings.REDIS_URL,
   )
   
   @celery_app.task
   def analyze_food_image_async(image_data: str, user_id: int):
       # 异步处理食物图像分析
       result = ai_service.analyze_food_image(image_data)
       save_analysis_result(user_id, result)
       return result
   
   # API端点触发异步任务
   @app.post("/nutrition/analyze-image")
   async def analyze_image(
       image: UploadFile,
       current_user: User = Depends(get_current_user)
   ):
       image_data = await image.read()
       task = analyze_food_image_async.delay(
           base64.b64encode(image_data).decode(),
           current_user.id
       )
       return {"task_id": task.id, "status": "processing"}
   ```

### 监控与告警扩展

1. **分布式追踪**
   ```python
   # 集成OpenTelemetry
   from opentelemetry import trace
   from opentelemetry.exporter.jaeger import JaegerExporter
   from opentelemetry.sdk.trace import TracerProvider
   from opentelemetry.sdk.trace.export import BatchSpanProcessor
   
   trace.set_tracer_provider(TracerProvider())
   tracer = trace.get_tracer(__name__)
   
   jaeger_exporter = JaegerExporter(
       agent_host_name="localhost",
       agent_port=6831,
   )
   
   span_processor = BatchSpanProcessor(jaeger_exporter)
   trace.get_tracer_provider().add_span_processor(span_processor)
   ```

2. **健康检查扩展**
   ```python
   # 扩展健康检查端点
   @app.get("/health")
   async def health_check():
       health_status = {
           "status": "healthy",
           "timestamp": datetime.utcnow().isoformat(),
           "services": {}
       }
       
       # 检查数据库
       try:
           db.execute("SELECT 1")
           health_status["services"]["database"] = "healthy"
       except Exception as e:
           health_status["services"]["database"] = "unhealthy"
           health_status["status"] = "degraded"
       
       # 检查Redis
       try:
           redis_client.ping()
           health_status["services"]["redis"] = "healthy"
       except Exception as e:
           health_status["services"]["redis"] = "unhealthy"
           health_status["status"] = "degraded"
       
       # 检查AI服务
       try:
           await ai_service.chat_completion([{"role": "user", "content": "ping"}])
           health_status["services"]["ai"] = "healthy"
       except Exception as e:
           health_status["services"]["ai"] = "unhealthy"
           health_status["status"] = "degraded"
       
       return health_status
   ```

---

## 总结

体重管理AI代理项目采用现代化的分层架构设计，具有良好的可扩展性和维护性：

### 架构优势

1. **清晰的关注点分离**: 前端、后端、数据库、AI服务各司其职
2. **松耦合设计**: 组件间通过定义良好的API接口通信
3. **可扩展性**: 支持水平扩展和微服务演进
4. **可维护性**: 统一的错误处理、日志记录和监控

### 关键技术决策

1. **FastAPI + React组合**: 提供优秀的开发体验和性能
2. **Docker容器化**: 确保环境一致性和简化部署
3. **通义千问AI集成**: 支持多模态AI能力（对话+视觉）
4. **JWT认证**: 无状态认证，适合分布式部署

### 未来演进方向

1. **微服务拆分**: 当业务复杂度增加时，可按领域拆分服务
2. **消息队列集成**: 引入Celery或Kafka处理异步任务
3. **CDN集成**: 静态资源和用户上传文件使用CDN加速
4. **多租户支持**: 为不同组织提供独立的数据隔离

---

**架构文档版本:** 1.0.0  
**最后更新:** 2024-01-20  
**维护者:** 架构团队