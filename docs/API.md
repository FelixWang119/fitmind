# API 文档

**版本**: 1.0  
**基础URL**: `http://localhost:8000/api/v1`  
**认证方式**: Bearer Token (JWT)

---

## 目录

1. [认证相关](#认证相关)
2. [用户相关](#用户相关)
3. [对话相关](#对话相关)
4. [营养管理](#营养管理)
5. [习惯追踪](#习惯追踪)
6. [健康数据](#健康数据)
7. [仪表盘](#仪表盘)
8. [游戏化](#游戏化)
9. [记忆系统](#记忆系统-api)

---

## 通用说明

### 请求格式

所有 POST/PUT 请求体应为 JSON 格式，Content-Type: `application/json`

### 响应格式

**成功响应** (2xx):
```json
{
  "data": { ... },
  "message": "操作成功"
}
```

**错误响应** (4xx/5xx):
```json
{
  "detail": "错误描述信息"
}
```

### 认证头

所有需要认证的接口，请求头需包含：
```
Authorization: Bearer <your_jwt_token>
```

---

## 认证相关

### 1. 用户注册

**POST** `/auth/register`

创建新用户账户。

**请求体**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "nickname": "用户名"
}
```

**字段说明**:
- `email`: 邮箱地址，必填，唯一
- `password`: 密码，必填，最少8位，需包含字母和数字
- `nickname`: 昵称，选填，默认为邮箱前缀

**成功响应** (201):
```json
{
  "data": {
    "id": 1,
    "email": "user@example.com",
    "nickname": "用户名",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00"
  },
  "message": "用户注册成功"
}
```

**错误响应**:
- 400: 邮箱已存在
- 422: 参数验证失败

---

### 2. 用户登录

**POST** `/auth/login`

用户登录，获取 JWT Token。

**请求体**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**成功响应** (200):
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": {
      "id": 1,
      "email": "user@example.com",
      "nickname": "用户名"
    }
  },
  "message": "登录成功"
}
```

**错误响应**:
- 401: 邮箱或密码错误

---

### 3. 获取当前用户信息

**GET** `/auth/me`

获取当前登录用户的详细信息。

**请求头**:
```
Authorization: Bearer <token>
```

**成功响应** (200):
```json
{
  "data": {
    "id": 1,
    "email": "user@example.com",
    "nickname": "用户名",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00",
    "profile": {
      "gender": "male",
      "age": 30,
      "height": 175,
      "current_weight": 85.5,
      "target_weight": 75.0,
      "bmi": 27.9
    }
  }
}
```

---

### 4. 修改密码

**PUT** `/auth/password`

修改当前用户密码。

**请求体**:
```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword456"
}
```

**成功响应** (200):
```json
{
  "message": "密码修改成功"
}
```

---

## 用户相关

### 5. 获取用户档案

**GET** `/users/profile`

获取当前用户的健康档案信息。

**成功响应** (200):
```json
{
  "data": {
    "id": 1,
    "user_id": 1,
    "gender": "male",
    "birth_date": "1994-05-20",
    "age": 30,
    "height": 175.0,
    "current_weight": 85.5,
    "target_weight": 75.0,
    "activity_level": "moderate",
    "dietary_preferences": ["halal"],
    "allergies": "花生、海鲜",
    "health_conditions": ["diabetes"],
    "bmr": 1800,
    "tdee": 2500,
    "daily_calorie_target": 2000,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-20T08:15:00"
  }
}
```

---

### 6. 创建/更新用户档案

**POST** `/users/profile`

创建或更新用户健康档案。

**请求体**:
```json
{
  "gender": "male",
  "birth_date": "1994-05-20",
  "height": 175.0,
  "current_weight": 85.5,
  "target_weight": 75.0,
  "activity_level": "moderate",
  "dietary_preferences": ["halal"],
  "allergies": "花生、海鲜",
  "health_conditions": ["diabetes"]
}
```

**字段说明**:
- `gender`: 性别，枚举值：`male`, `female`, `other`
- `birth_date`: 出生日期，格式：`YYYY-MM-DD`
- `height`: 身高，单位：厘米
- `current_weight`: 当前体重，单位：公斤
- `target_weight`: 目标体重，单位：公斤
- `activity_level`: 活动水平，枚举值：`sedentary`, `light`, `moderate`, `heavy`
- `dietary_preferences`: 饮食偏好，数组，可选值：`vegetarian`, `vegan`, `halal`, `kosher`, `gluten_free`
- `allergies`: 过敏食物，文本
- `health_conditions`: 健康状况，数组，可选值：`diabetes`, `hypertension`, `heart_disease`, `kidney_disease`, `none`

**成功响应** (200):
```json
{
  "data": {
    "id": 1,
    "user_id": 1,
    "gender": "male",
    "bmr": 1800,
    "tdee": 2500,
    "daily_calorie_target": 2000
  },
  "message": "档案更新成功"
}
```

**自动计算字段**:
- `bmr`: 基础代谢率（根据公式自动计算）
- `tdee`: 每日总能量消耗
- `daily_calorie_target`: 每日目标热量（TDEE - 500）

---

## 对话相关

### 7. 发送消息

**POST** `/chat`

向 AI 助手发送消息。

**请求体**:
```json
{
  "message": "我今天该吃什么？",
  "conversation_id": 1
}
```

**字段说明**:
- `message`: 用户消息内容，必填，最多2000字符
- `conversation_id`: 对话ID，选填。不填则创建新对话

**成功响应** (200):
```json
{
  "data": {
    "conversation_id": 1,
    "user_message": {
      "id": 101,
      "role": "user",
      "content": "我今天该吃什么？",
      "created_at": "2024-01-20T10:00:00"
    },
    "ai_message": {
      "id": 102,
      "role": "assistant",
      "content": "根据你的营养计划，今天建议...",
      "created_at": "2024-01-20T10:00:05"
    },
    "title": "饮食咨询"
  }
}
```

**流式响应** (SSE):
如果请求头包含 `Accept: text/event-stream`，将返回 SSE 流：
```
data: {"type": "start", "conversation_id": 1}

data: {"type": "token", "content": "根据"}

data: {"type": "token", "content": "你的"}

data: {"type": "token", "content": "计划..."}

data: {"type": "end", "message_id": 102}
```

---

### 8. 获取对话历史

**GET** `/chat/history`

获取当前用户的所有对话列表。

**查询参数**:
- `limit`: 返回数量，默认20，最大100
- `offset`: 偏移量，默认0

**成功响应** (200):
```json
{
  "data": {
    "conversations": [
      {
        "id": 1,
        "title": "饮食咨询",
        "last_message": "谢谢你的建议！",
        "last_message_time": "2024-01-20T10:30:00",
        "message_count": 15,
        "created_at": "2024-01-20T10:00:00"
      },
      {
        "id": 2,
        "title": "运动计划",
        "last_message": "明天开始执行",
        "last_message_time": "2024-01-19T18:00:00",
        "message_count": 8,
        "created_at": "2024-01-19T17:30:00"
      }
    ],
    "total": 2,
    "limit": 20,
    "offset": 0
  }
}
```

---

### 9. 获取单条对话详情

**GET** `/chat/{conversation_id}`

获取特定对话的所有消息。

**成功响应** (200):
```json
{
  "data": {
    "id": 1,
    "title": "饮食咨询",
    "messages": [
      {
        "id": 101,
        "role": "user",
        "content": "我今天该吃什么？",
        "created_at": "2024-01-20T10:00:00"
      },
      {
        "id": 102,
        "role": "assistant",
        "content": "根据你的营养计划...",
        "created_at": "2024-01-20T10:00:05"
      }
    ],
    "created_at": "2024-01-20T10:00:00"
  }
}
```

---

### 10. 删除对话

**DELETE** `/chat/{conversation_id}`

删除特定对话及其所有消息。

**成功响应** (200):
```json
{
  "message": "对话已删除"
}
```

---

## 营养管理

### 11. 获取营养计划

**GET** `/nutrition/plan`

获取当前用户的营养计划。

**成功响应** (200):
```json
{
  "data": {
    "id": 1,
    "user_id": 1,
    "daily_calories": 2000,
    "protein_grams": 150,
    "fat_grams": 67,
    "carbs_grams": 200,
    "meals_per_day": 3,
    "meal_distribution": {
      "breakfast": 0.3,
      "lunch": 0.4,
      "dinner": 0.3
    },
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-20T08:15:00"
  }
}
```

---

### 12. 生成营养计划

**POST** `/nutrition/plan/generate`

基于用户档案自动生成营养计划。

**成功响应** (201):
```json
{
  "data": {
    "id": 1,
    "daily_calories": 2000,
    "protein_grams": 150,
    "fat_grams": 67,
    "carbs_grams": 200,
    "created_at": "2024-01-20T08:15:00"
  },
  "message": "营养计划已生成"
}
```

---

### 13. 获取饮食记录

**GET** `/nutrition/food-log`

获取指定日期的饮食记录。

**查询参数**:
- `date`: 日期，格式 `YYYY-MM-DD`，默认为今天

**成功响应** (200):
```json
{
  "data": {
    "date": "2024-01-20",
    "entries": [
      {
        "id": 1,
        "meal_type": "breakfast",
        "food_name": "燕麦粥",
        "calories": 300,
        "protein": 10,
        "fat": 5,
        "carbs": 55,
        "logged_at": "2024-01-20T08:00:00"
      },
      {
        "id": 2,
        "meal_type": "lunch",
        "food_name": "鸡胸肉沙拉",
        "calories": 450,
        "protein": 35,
        "fat": 15,
        "carbs": 20,
        "logged_at": "2024-01-20T12:30:00"
      }
    ],
    "summary": {
      "total_calories": 750,
      "total_protein": 45,
      "total_fat": 20,
      "total_carbs": 75,
      "remaining_calories": 1250
    }
  }
}
```

---

### 14. 添加饮食记录

**POST** `/nutrition/food-log`

添加一条饮食记录。

**请求体**:
```json
{
  "meal_type": "dinner",
  "food_name": "蒸鱼",
  "calories": 200,
  "protein": 25,
  "fat": 8,
  "carbs": 2,
  "date": "2024-01-20"
}
```

**字段说明**:
- `meal_type`: 餐次，枚举值：`breakfast`, `lunch`, `dinner`, `snack`
- `food_name`: 食物名称
- `calories`: 热量，单位：千卡
- `protein`: 蛋白质，单位：克
- `fat`: 脂肪，单位：克
- `carbs`: 碳水化合物，单位：克
- `date`: 日期，格式 `YYYY-MM-DD`，默认为今天

**成功响应** (201):
```json
{
  "data": {
    "id": 3,
    "user_id": 1,
    "meal_type": "dinner",
    "food_name": "蒸鱼",
    "calories": 200,
    "logged_at": "2024-01-20T18:30:00"
  },
  "message": "饮食记录已添加"
}
```

---

### 15. 删除饮食记录

**DELETE** `/nutrition/food-log/{entry_id}`

删除特定的饮食记录。

**成功响应** (200):
```json
{
  "message": "记录已删除"
}
```

---

## 习惯追踪

### 16. 获取习惯列表

**GET** `/habits`

获取当前用户的所有习惯。

**查询参数**:
- `include_archived`: 是否包含已归档的习惯，默认 `false`

**成功响应** (200):
```json
{
  "data": {
    "habits": [
      {
        "id": 1,
        "name": "每天喝8杯水",
        "description": "保持水分充足",
        "frequency": "daily",
        "frequency_count": 8,
        "streak": 12,
        "best_streak": 15,
        "total_completions": 45,
        "completion_rate": 0.85,
        "reminder_time": "09:00",
        "is_active": true,
        "created_at": "2024-01-01T08:00:00"
      },
      {
        "id": 2,
        "name": "步行8000步",
        "description": "每日步数目标",
        "frequency": "daily",
        "frequency_count": 1,
        "streak": 5,
        "best_streak": 10,
        "total_completions": 30,
        "completion_rate": 0.75,
        "reminder_time": "20:00",
        "is_active": true,
        "created_at": "2024-01-05T10:00:00"
      }
    ]
  }
}
```

---

### 17. 创建习惯

**POST** `/habits`

创建一个新习惯。

**请求体**:
```json
{
  "name": "早睡",
  "description": "晚上11点前睡觉",
  "frequency": "daily",
  "frequency_count": 1,
  "reminder_time": "22:30"
}
```

**字段说明**:
- `name`: 习惯名称，必填，最多50字符
- `description`: 习惯描述，选填
- `frequency`: 频率，枚举值：`daily`, `weekly`
- `frequency_count`: 频率次数（如每周3次则填3）
- `reminder_time`: 提醒时间，格式 `HH:MM`

**成功响应** (201):
```json
{
  "data": {
    "id": 3,
    "name": "早睡",
    "description": "晚上11点前睡觉",
    "frequency": "daily",
    "frequency_count": 1,
    "streak": 0,
    "reminder_time": "22:30",
    "is_active": true,
    "created_at": "2024-01-20T09:00:00"
  },
  "message": "习惯创建成功"
}
```

---

### 18. 习惯打卡

**POST** `/habits/{habit_id}/checkin`

为特定习惯打卡。

**请求体**:
```json
{
  "date": "2024-01-20",
  "note": "今天喝水很足！"
}
```

**字段说明**:
- `date`: 打卡日期，格式 `YYYY-MM-DD`，默认为今天
- `note`: 备注，选填

**成功响应** (200):
```json
{
  "data": {
    "id": 50,
    "habit_id": 1,
    "user_id": 1,
    "date": "2024-01-20",
    "note": "今天喝水很足！",
    "streak_after": 13,
    "checked_at": "2024-01-20T21:00:00"
  },
  "message": "打卡成功！连续13天！"
}
```

---

### 19. 取消打卡

**DELETE** `/habits/checkin/{checkin_id}`

取消特定日期的习惯打卡。

**成功响应** (200):
```json
{
  "message": "打卡已取消"
}
```

---

### 20. 更新习惯

**PUT** `/habits/{habit_id}`

更新习惯信息。

**请求体**:
```json
{
  "name": "每天喝2000ml水",
  "reminder_time": "08:00"
}
```

**成功响应** (200):
```json
{
  "data": {
    "id": 1,
    "name": "每天喝2000ml水",
    "reminder_time": "08:00",
    "updated_at": "2024-01-20T10:00:00"
  },
  "message": "习惯已更新"
}
```

---

### 21. 归档习惯

**POST** `/habits/{habit_id}/archive`

归档习惯（不再追踪但保留历史数据）。

**成功响应** (200):
```json
{
  "message": "习惯已归档"
}
```

---

## 健康数据

### 22. 获取健康数据

**GET** `/health/data`

获取指定类型的健康数据记录。

**查询参数**:
- `type`: 数据类型，枚举值：`weight`, `body_fat`, `waist`, `blood_pressure`, `blood_sugar`, `steps`, `sleep`, `exercise`
- `start_date`: 开始日期 `YYYY-MM-DD`
- `end_date`: 结束日期 `YYYY-MM-DD`
- `limit`: 返回数量，默认30

**成功响应** (200):
```json
{
  "data": {
    "type": "weight",
    "unit": "kg",
    "records": [
      {
        "id": 1,
        "value": 85.5,
        "recorded_at": "2024-01-20T08:00:00",
        "note": "早上空腹测量"
      },
      {
        "id": 2,
        "value": 85.2,
        "recorded_at": "2024-01-19T08:00:00"
      }
    ],
    "statistics": {
      "current": 85.5,
      "start": 90.0,
      "change": -4.5,
      "change_percent": -5.0,
      "average": 87.2,
      "min": 85.2,
      "max": 90.0
    }
  }
}
```

---

### 23. 添加健康数据

**POST** `/health/data`

添加一条健康数据记录。

**请求体**:
```json
{
  "type": "weight",
  "value": 85.5,
  "recorded_at": "2024-01-20T08:00:00",
  "note": "早上空腹测量"
}
```

**字段说明**:
- `type`: 数据类型，必填
- `value`: 数值，必填
- `recorded_at`: 记录时间，默认当前时间
- `note`: 备注，选填

**成功响应** (201):
```json
{
  "data": {
    "id": 10,
    "type": "weight",
    "value": 85.5,
    "recorded_at": "2024-01-20T08:00:00",
    "note": "早上空腹测量",
    "created_at": "2024-01-20T08:05:00"
  },
  "message": "记录已添加"
}
```

---

### 24. 获取最新数据

**GET** `/health/data/latest`

获取所有健康类型的最新数据。

**成功响应** (200):
```json
{
  "data": {
    "weight": {
      "value": 85.5,
      "unit": "kg",
      "recorded_at": "2024-01-20T08:00:00"
    },
    "body_fat": {
      "value": 28.5,
      "unit": "%",
      "recorded_at": "2024-01-18T20:00:00"
    },
    "steps": {
      "value": 8500,
      "unit": "步",
      "recorded_at": "2024-01-20T23:59:00"
    },
    "sleep": {
      "value": 7.5,
      "unit": "小时",
      "recorded_at": "2024-01-20T07:00:00"
    }
  }
}
```

---

### 25. 删除健康数据

**DELETE** `/health/data/{record_id}`

删除特定的健康数据记录。

**成功响应** (200):
```json
{
  "message": "记录已删除"
}
```

---

## 仪表盘

### 26. 获取仪表盘数据

**GET** `/dashboard`

获取仪表盘汇总数据。

**成功响应** (200):
```json
{
  "data": {
    "user_summary": {
      "nickname": "用户名",
      "days_active": 30,
      "current_weight": 85.5,
      "target_weight": 75.0,
      "weight_change": -4.5,
      "bmi": 27.9,
      "bmi_status": "overweight"
    },
    "today_summary": {
      "calories_consumed": 1500,
      "calories_target": 2000,
      "calories_remaining": 500,
      "habits_completed": 3,
      "habits_total": 5,
      "steps": 8500,
      "sleep_hours": 7.5
    },
    "progress": {
      "weight_progress": 45.0,
      "habit_completion_rate": 0.75,
      "days_to_goal": 90
    },
    "recent_achievements": [
      {
        "id": 1,
        "name": "坚持一周",
        "icon": "🏆",
        "earned_at": "2024-01-15"
      }
    ],
    "ai_suggestions": [
      "你已经连续记录了7天体重，很棒！",
      "今天的蛋白质摄入略低，晚餐可以增加一些瘦肉。"
    ]
  }
}
```

---

### 27. 获取趋势数据

**GET** `/dashboard/trends`

获取趋势分析数据。

**查询参数**:
- `period`: 周期，枚举值：`week`, `month`, `quarter`，默认 `month`

**成功响应** (200):
```json
{
  "data": {
    "period": "month",
    "weight_trend": {
      "labels": ["01-01", "01-08", "01-15", "01-22", "01-29"],
      "data": [90.0, 88.5, 87.0, 86.0, 85.5],
      "trend": "down",
      "average_change_per_week": -1.1
    },
    "calories_trend": {
      "labels": ["01-01", "01-08", "01-15", "01-22", "01-29"],
      "data": [2100, 2050, 2000, 1950, 1900],
      "average": 2000
    },
    "habits_trend": {
      "labels": ["第1周", "第2周", "第3周", "第4周"],
      "completion_rates": [0.65, 0.70, 0.75, 0.80]
    },
    "insights": [
      {
        "type": "positive",
        "message": "本周体重下降了0.5kg，继续保持！"
      },
      {
        "type": "suggestion",
        "message": "发现你周末热量摄入较高，可以尝试提前规划周末饮食。"
      }
    ]
  }
}
```

---

## 游戏化

### 28. 获取游戏化档案

**GET** `/gamification/profile`

获取用户的游戏化数据（积分、等级、徽章）。

**成功响应** (200):
```json
{
  "data": {
    "points": 2500,
    "level": {
      "current": 4,
      "name": "实践者",
      "points_to_next": 1000,
      "progress_percent": 60
    },
    "streaks": {
      "current_login_streak": 5,
      "best_login_streak": 15,
      "current_checkin_streak": 3
    },
    "stats": {
      "total_logins": 45,
      "total_messages": 120,
      "total_habit_checkins": 150,
      "total_data_entries": 80
    }
  }
}
```

---

### 29. 获取徽章列表

**GET** `/gamification/badges`

获取用户已获得和未获得的徽章。

**成功响应** (200):
```json
{
  "data": {
    "earned": [
      {
        "id": 1,
        "name": "初尝胜果",
        "description": "第一次减重5斤",
        "icon": "🎯",
        "category": "achievement",
        "earned_at": "2024-01-15T10:00:00",
        "points": 100
      },
      {
        "id": 2,
        "name": "水牛",
        "description": "连续7天饮水达标",
        "icon": "💧",
        "category": "habit",
        "earned_at": "2024-01-18T20:00:00",
        "points": 50
      }
    ],
    "available": [
      {
        "id": 3,
        "name": "半程英雄",
        "description": "达成50%减重目标",
        "icon": "🏆",
        "category": "achievement",
        "points": 200,
        "progress": 0.45
      }
    ]
  }
}
```

---

### 30. 获取积分历史

**GET** `/gamification/points-history`

获取积分获取历史。

**查询参数**:
- `limit`: 返回数量，默认20
- `offset`: 偏移量，默认0

**成功响应** (200):
```json
{
  "data": {
    "history": [
      {
        "id": 1,
        "action": "习惯打卡",
        "points": 10,
        "description": "完成'每天喝8杯水'",
        "created_at": "2024-01-20T21:00:00"
      },
      {
        "id": 2,
        "action": "记录体重",
        "points": 10,
        "description": "记录今日体重",
        "created_at": "2024-01-20T08:00:00"
      },
      {
        "id": 3,
        "action": "AI对话",
        "points": 5,
        "description": "与AI助手互动",
        "created_at": "2024-01-19T20:00:00"
      }
    ],
    "total": 150,
    "limit": 20,
    "offset": 0
  }
}
```

---

## 错误代码

### HTTP 状态码

| 状态码 | 含义 | 说明 |
|-------|------|------|
| 200 | OK | 请求成功 |
| 201 | Created | 创建成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证或Token无效 |
| 403 | Forbidden | 无权限访问 |
| 404 | Not Found | 资源不存在 |
| 422 | Unprocessable Entity | 参数验证失败 |
| 500 | Internal Server Error | 服务器内部错误 |

### 业务错误码

部分接口会返回详细的业务错误码：

```json
{
  "detail": {
    "code": "INSUFFICIENT_DATA",
    "message": "数据不足以生成分析",
    "suggestion": "请至少记录7天的数据"
  }
}
```

常见业务错误码：

| 错误码 | 说明 | 解决建议 |
|-------|------|---------|
| `USER_NOT_FOUND` | 用户不存在 | 检查用户ID |
| `CONVERSATION_NOT_FOUND` | 对话不存在 | 检查对话ID |
| `HABIT_NOT_FOUND` | 习惯不存在 | 检查习惯ID |
| `INVALID_DATE_FORMAT` | 日期格式错误 | 使用 `YYYY-MM-DD` 格式 |
| `FUTURE_DATE` | 不能记录未来日期 | 使用今天或过去的日期 |
| `ALREADY_CHECKED_IN` | 今天已打卡 | 无需重复打卡 |
| `NO_PROFILE` | 未设置用户档案 | 先创建用户档案 |
| `INSUFFICIENT_DATA` | 数据不足 | 多记录一些数据 |

---

## 分页说明

支持分页的接口（如历史记录列表）使用以下参数：

**请求参数**:
- `limit`: 每页数量，默认20，最大100
- `offset`: 偏移量，从0开始

**响应格式**:
```json
{
  "data": {
    "items": [...],
    "total": 150,
    "limit": 20,
    "offset": 0,
    "has_more": true
  }
}
```

**计算页码**:
```
当前页 = offset / limit + 1
总页数 = ceil(total / limit)
```

---

## 限流说明

API 有限流保护：

- 认证接口：5次/分钟
- 普通接口：100次/分钟
- AI对话接口：10次/分钟

超过限流将返回 429 Too Many Requests。

---

## SDK 示例

### Python 示例

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

def login(email, password):
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    return response.json()["data"]["access_token"]

def send_message(token, message, conversation_id=None):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"message": message}
    if conversation_id:
        data["conversation_id"] = conversation_id
    
    response = requests.post(
        f"{BASE_URL}/chat",
        headers=headers,
        json=data
    )
    return response.json()

# 使用示例
token = login("user@example.com", "password123")
result = send_message(token, "你好，今天该吃什么？")
print(result["data"]["ai_message"]["content"])
```

### JavaScript/TypeScript 示例

```typescript
const BASE_URL = "http://localhost:8000/api/v1";

async function login(email: string, password: string): Promise<string> {
  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  return data.data.access_token;
}

async function sendMessage(
  token: string,
  message: string,
  conversationId?: number
) {
  const response = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({
      message,
      conversation_id: conversationId
    })
  });
  return response.json();
}

// 使用示例
const token = await login("user@example.com", "password123");
const result = await sendMessage(token, "你好，今天该吃什么？");
console.log(result.data.ai_message.content);
```

---
# 记忆系统 API

## 概述
记忆系统API提供完整的用户行为数据分析和智能上下文构建功能。

**基础URL**: `/api/v1/memory`

---

## 目录

1. [记忆管理](#记忆管理)
2. [趋势分析](#趋势分析)
3. [里程碑检测](#里程碑检测)
4. [上下文构建](#上下文构建)
5. [数据关联](#数据关联)
6. [个性化推荐](#个性化推荐)
7. [数据处理](#数据处理)

---

## 记忆管理

### 创建记忆
**POST** `/memories`

创建用户长期记忆。

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | int | 是 | 用户ID |
| memory_type | string | 是 | 记忆类型 (health_trend, habit_pattern, milestone, preference) |
| memory_key | string | 是 | 记忆键 |
| memory_value | object | 是 | 记忆值 |
| importance_score | float | 否 | 重要性评分 (0-10) |

**成功响应**:
```json
{
  "success": true,
  "memory_id": 1
}
```

### 获取记忆列表
**GET** `/memories`

获取用户记忆列表。

**查询参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| user_id | int | 用户ID |
| memory_type | string | 可选：按记忆类型筛选 |
| min_importance | float | 可选：最小重要性评分 |

**成功响应**:
```json
{
  "success": true,
  "count": 5,
  "memories": [...]
}
```

### 获取记忆统计
**GET** `/memories/stats`

获取用户记忆统计信息。

**查询参数**: `user_id`

---

## 趋势分析

### 体重趋势
**GET** `/trends/weight`

分析用户体重趋势。

**查询参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|---------|------|
| user_id | int | - | 用户ID |
| days | int | 30 | 分析天数 (7-90) |

### 运动趋势
**GET** `/trends/exercise`

分析用户运动趋势。

### 饮食趋势
**GET** `/trends/diet`

分析用户饮食趋势。

### 综合趋势
**GET** `/trends/all`

获取所有趋势的综合分析。

### 习惯一致性
**GET** `/habits/consistency`

分析用户习惯完成一致性。

---

## 里程碑检测

### 获取所有里程碑
**GET** `/milestones`

获取用户的所有里程碑和预警。

### 体重目标进度
**GET** `/milestones/weight-goal`

获取体重目标达成进度。

### 连续记录里程碑
**GET** `/milestones/streaks`

获取连续打卡里程碑。

### 预警信号
**GET** `/milestones/warnings`

获取负面趋势预警。

---

## 上下文构建

### 完整上下文
**GET** `/context`

获取用户完整上下文（包括画像、趋势、模式、里程碑）。

### 快速上下文
**GET** `/context/quick`

获取快速上下文（轻量级）。

### AI提示生成
**GET** `/ai-prompt`

生成AI所需的提示信息。

**查询参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| user_id | int | 用户ID |
| user_message | string | 用户消息 |

---

## 数据关联

### 获取关联
**GET** `/associations`

获取数据之间的关联关系。

**查询参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| user_id | int | 用户ID |
| min_strength | float | 最小关联强度 (0-1) |

### 检测关联
**POST** `/associations/detect`

自动检测并创建新的数据关联。

---

## 个性化推荐

### 综合推荐
**GET** `/recommendations`

获取饮食、运动、习惯的综合推荐。

### 饮食推荐
**GET** `/recommendations/diet`

获取个性化饮食建议。

### 运动推荐
**GET** `/recommendations/exercise`

获取个性化运动建议。

### 习惯推荐
**GET** `/recommendations/habits`

获取习惯养成建议。

### 即时建议
**GET** `/quick-tip`

获取基于时间和上下文的快速建议。

---

## 数据处理

### 处理每日数据
**POST** `/process-daily`

处理用户每日数据，生成摘要。

**查询参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| user_id | int | 用户ID |
| process_date | date | 可选：处理日期 |
| force | bool | 是否强制重新处理 |

### 获取摘要
**GET** `/summaries`

获取近期数据摘要。

---

## 使用示例

```javascript
// 获取用户记忆统计
const stats = await fetch('/api/v1/memory/memories/stats?user_id=1');
const statsData = await stats.json();
console.log(statsData.stats);

// 获取体重趋势
const weightTrend = await fetch('/api/v1/memory/trends/weight?user_id=1&days=30');
const trendData = await weightTrend.json();
console.log(trendData.trend);

// 获取综合推荐
const recommendations = await fetch('/api/v1/memory/recommendations?user_id=1');
const recData = await recommendations.json();
console.log(recData.recommendations);

// 获取完整上下文
const context = await fetch('/api/v1/memory/context?user_id=1');
const contextData = await context.json();
console.log(contextData.context_text);
```

---

**文档结束**

*本文档由系统自动生成，最后更新：2026-02-21*
