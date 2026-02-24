# API合约文档 - 后端部分

## 概述

本文档详细描述了后端API的端点、请求/响应格式、认证机制和错误处理。后端使用FastAPI框架，提供RESTful API接口。

## 认证API

### 1. 用户注册
**端点**: `POST /api/v1/auth/register`

**请求体**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "username": "optional_username",
  "full_name": "User Full Name",
  "age": 30,
  "gender": "male",
  "height": 175,
  "initial_weight": 70000,
  "target_weight": 65000,
  "activity_level": "moderate",
  "dietary_preferences": "{\"preferences\": [\"low_carb\", \"high_protein\"]}"
}
```

**响应** (201 Created):
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "optional_username",
  "full_name": "User Full Name",
  "is_active": true,
  "is_superuser": false,
  "age": 30,
  "gender": "male",
  "height": 175,
  "initial_weight": 70000,
  "target_weight": 65000,
  "activity_level": "moderate",
  "dietary_preferences": "{\"preferences\": [\"low_carb\", \"high_protein\"]}",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**错误响应**:
- `400 Bad Request`: 邮箱已注册或验证失败
- `429 Too Many Requests`: 超过注册速率限制
- `500 Internal Server Error`: 服务器内部错误

### 2. 用户登录
**端点**: `POST /api/v1/auth/login`

**请求体** (表单数据):
```
username: user@example.com
password: securepassword123
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**错误响应**:
- `401 Unauthorized`: 用户名或密码错误
- `400 Bad Request`: 无效的请求格式

### 3. 获取当前用户
**端点**: `GET /api/v1/users/profile`

**认证**: Bearer Token

**响应**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "optional_username",
  "full_name": "User Full Name",
  "is_active": true,
  "is_superuser": false,
  "age": 30,
  "gender": "male",
  "height": 175,
  "initial_weight": 70000,
  "target_weight": 65000,
  "activity_level": "moderate",
  "dietary_preferences": "{\"preferences\": [\"low_carb\", \"high_protein\"]}",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-01T12:00:00Z"
}
```

### 4. 密码重置请求
**端点**: `POST /api/v1/auth/password-reset-request`

**请求体**:
```json
{
  "email": "user@example.com"
}
```

### 5. 密码重置
**端点**: `POST /api/v1/auth/password-reset`

**请求体**:
```json
{
  "token": "reset_token_here",
  "new_password": "newsecurepassword123"
}
```

## 用户管理API

### 1. 更新用户资料
**端点**: `PUT /api/v1/users/profile`

**认证**: Bearer Token

**请求体**:
```json
{
  "full_name": "Updated Name",
  "age": 31,
  "height": 176,
  "target_weight": 64000,
  "activity_level": "active",
  "dietary_preferences": "{\"preferences\": [\"vegetarian\"]}"
}
```

## 餐食管理API

### 1. 获取每日餐食摘要
**端点**: `GET /api/v1/meals/daily-nutrition-summary`

**查询参数**:
- `target_date`: 目标日期 (格式: YYYY-MM-DD)

**响应**:
```json
{
  "date": "2024-01-01",
  "total_calories": 1800,
  "total_protein": 120,
  "total_carbs": 200,
  "total_fat": 60,
  "meals": [
    {
      "id": 1,
      "meal_type": "breakfast",
      "name": "早餐",
      "calories": 400,
      "protein": 20,
      "carbs": 50,
      "fat": 15,
      "meal_datetime": "2024-01-01T08:00:00Z"
    }
  ]
}
```

### 2. 创建餐食
**端点**: `POST /api/v1/meals`

**认证**: Bearer Token

**请求体**:
```json
{
  "meal_type": "lunch",
  "name": "AI分析午餐",
  "calories": 600,
  "protein": 40,
  "carbs": 60,
  "fat": 20,
  "meal_datetime": "2024-01-01T12:30:00Z",
  "items": [
    {
      "name": "米饭",
      "grams": 150,
      "calories": 174,
      "protein": 3,
      "carbs": 38,
      "fat": 0.5
    }
  ]
}
```

### 3. 更新餐食
**端点**: `PUT /api/v1/meals/{meal_id}`

### 4. 删除餐食
**端点**: `DELETE /api/v1/meals/{meal_id}`

## 营养分析API

### 1. 分析食物图片
**端点**: `POST /api/v1/nutrition/analyze-food-image`

**认证**: Bearer Token

**请求体**:
```json
{
  "image": "base64_encoded_image_string",
  "date": "2024-01-01"
}
```

**响应**:
```json
{
  "meal_type": "lunch",
  "items": [
    {
      "name": "米饭",
      "grams": 150,
      "calories": 174,
      "protein": 3,
      "carbs": 38,
      "fat": 0.5
    },
    {
      "name": "红烧肉",
      "grams": 100,
      "calories": 350,
      "protein": 12,
      "carbs": 8,
      "fat": 30
    }
  ],
  "total_calories": 524,
  "total_protein": 15,
  "total_carbs": 46,
  "total_fat": 30.5,
  "notes": "AI分析完成，包含米饭和红烧肉"
}
```

## AI聊天API

### 1. 发送AI消息
**端点**: `POST /api/v1/ai/chat`

**认证**: Bearer Token

**请求体**:
```json
{
  "message": "我今天体重下降了1公斤",
  "conversation_id": 1,
  "role": "nutritionist"
}
```

**响应**:
```json
{
  "response": "恭喜你！体重下降1公斤是个很好的进展。继续保持健康的饮食和运动习惯。",
  "model": "qwen-plus",
  "tokens_used": 45,
  "response_time": 1.2,
  "timestamp": "2024-01-01T12:00:00Z",
  "metadata": {
    "role": "nutritionist"
  }
}
```

### 2. 获取对话列表
**端点**: `GET /api/v1/chat/conversations`

### 3. 获取对话消息
**端点**: `GET /api/v1/chat/conversations/{conversation_id}/messages`

### 4. 创建新对话
**端点**: `POST /api/v1/chat/conversations`

## 习惯管理API

### 1. 获取习惯列表
**端点**: `GET /api/v1/habits/`

**查询参数**:
- `active_only`: 是否只返回活跃习惯 (默认: true)

### 2. 创建习惯
**端点**: `POST /api/v1/habits/`

### 3. 完成习惯
**端点**: `POST /api/v1/habits/{habit_id}/completions`

### 4. 获取习惯统计
**端点**: `GET /api/v1/habits/statistics`

## 仪表板API

### 1. 获取仪表板概览
**端点**: `GET /api/v1/dashboard/overview`

**响应**:
```json
{
  "user": {
    "name": "User Name",
    "current_weight": 68000,
    "target_weight": 65000,
    "progress_percentage": 60
  },
  "today_summary": {
    "calories_consumed": 1200,
    "calories_budget": 1800,
    "protein_consumed": 80,
    "habits_completed": 3,
    "total_habits": 5
  },
  "recent_achievements": [
    {
      "title": "连续打卡7天",
      "description": "保持良好习惯",
      "date": "2024-01-01"
    }
  ]
}
```

### 2. 获取快速统计
**端点**: `GET /api/v1/dashboard/quick-stats`

### 3. 获取AI建议
**端点**: `GET /api/v1/dashboard/ai-suggestions`

## 游戏化API

### 1. 获取游戏化概览
**端点**: `GET /api/v1/gamification/overview`

### 2. 获取用户积分
**端点**: `GET /api/v1/gamification/points`

### 3. 获取徽章
**端点**: `GET /api/v1/gamification/badges`

### 4. 领取每日奖励
**端点**: `POST /api/v1/gamification/claim-daily-reward`

## 健康评估API

### 1. 创建健康评估
**端点**: `POST /api/v1/health-assessment/assessments`

### 2. 获取最新评估
**端点**: `GET /api/v1/health-assessment/assessments/latest`

## 错误处理

### 错误响应格式
```json
{
  "detail": "错误描述",
  "status_code": 400,
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 常见错误码
- `VALIDATION_ERROR`: 请求数据验证失败
- `AUTHENTICATION_ERROR`: 认证失败
- `AUTHORIZATION_ERROR`: 权限不足
- `NOT_FOUND`: 资源未找到
- `RATE_LIMIT_EXCEEDED`: 请求频率超限
- `INTERNAL_SERVER_ERROR`: 服务器内部错误

## 认证机制

### JWT令牌认证
1. 用户通过登录端点获取访问令牌
2. 后续请求需要在Header中添加: `Authorization: Bearer <token>`
3. 令牌有效期: 30分钟（可在配置中调整）
4. 令牌刷新: 支持刷新令牌机制

### 速率限制
- 注册端点: 每个IP地址每小时最多5次
- 登录端点: 每个IP地址每小时最多10次
- API端点: 每个用户每分钟最多60次请求

## 千问API集成

### 配置参数
```python
# app/core/config.py
QWEN_API_KEY: Optional[str] = None  # API密钥
QWEN_API_BASE: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_API_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
QWEN_MODEL: str = "qwen-plus"  # 默认模型
```

### 模型使用策略
1. **普通对话**: 使用 `qwen-plus` 模型
2. **图片识别**: 使用 `qwen-vl-max` 或 `qwen-vl-chat` 模型
3. **环境感知**: 开发环境无API密钥时使用模拟数据
4. **错误恢复**: API调用失败时返回后备数据

### 图片分析流程
1. 前端上传base64编码的图片
2. 后端调用千问视觉API (`qwen-vl-max`模型)
3. 解析API返回的JSON格式结果
4. 返回标准化的营养分析数据

## 测试用户固化方案

### 测试用户管理
1. **测试用户创建**: 使用固定邮箱和密码创建测试用户
2. **用户持久化**: 测试用户信息存储在测试数据库中
3. **认证令牌缓存**: 测试用户的认证令牌可重复使用
4. **数据隔离**: 测试用户与生产用户数据隔离

### 测试资源位置
- **测试图片目录**: `/Users/felix/bmad/backend/tests/mealimg/`
- **包含文件**: lunch.jpg, meal3.png, meal4.jpg, meal5.jpg, meal6.jpg
- **用途**: 食品图像分析测试
- **管理**: 测试资源纳入版本控制，有意义的文件名

### 测试流程
1. 使用测试用户登录获取令牌
2. 使用测试图片进行食物分析
3. 验证AI分析结果
4. 创建餐食记录
5. 验证数据一致性