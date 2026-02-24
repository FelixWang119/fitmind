# 数据模型文档 - 后端部分

## 概述

本文档详细描述了后端数据库的数据模型、表结构、关系和迁移策略。项目使用SQLAlchemy ORM和Alembic迁移工具。

## 核心数据模型

### 1. 用户模型 (User)

**表名**: `users`

**字段**:
| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | Integer | Primary Key, Index | 用户ID |
| email | String(255) | Unique, Index, Not Null | 邮箱地址 |
| username | String(100) | Unique, Index, Nullable | 用户名（可选） |
| full_name | String(200) | - | 全名 |
| hashed_password | String(255) | Not Null | 哈希后的密码 |
| is_active | Boolean | Default: True | 是否活跃 |
| is_superuser | Boolean | Default: False | 是否超级用户 |
| age | Integer | - | 年龄 |
| gender | String(10) | - | 性别（male/female/other） |
| height | Integer | - | 身高（厘米） |
| initial_weight | Integer | - | 初始体重（克） |
| target_weight | Integer | - | 目标体重（克） |
| activity_level | String(50) | - | 活动水平（sedentary/light/moderate/active/very_active） |
| dietary_preferences | Text | - | 饮食偏好（JSON字符串） |
| created_at | DateTime | Server Default: func.now() | 创建时间 |
| updated_at | DateTime | onupdate: func.now() | 更新时间 |
| last_login | DateTime | - | 最后登录时间 |

**关系**:
- `health_records`: 一对多，关联HealthRecord
- `conversations`: 一对多，关联Conversation
- `habits`: 一对多，关联Habit
- `habit_goals`: 一对多，关联HabitGoal
- `meals`: 一对多，关联Meal
- `water_intakes`: 一对多，关联WaterIntake
- `health_assessments`: 一对多，关联HealthAssessment
- `long_term_memories`: 一对多，关联UserLongTermMemory
- `context_summaries`: 一对多，关联ContextSummary
- `habit_patterns`: 一对多，关联HabitPattern
- `data_associations`: 一对多，关联DataAssociation
- `password_reset_tokens`: 一对多，关联PasswordResetToken
- `reward_redemptions`: 一对多，关联RewardRedemption
- `calorie_goals`: 一对多，关联CalorieGoal

### 2. 餐食模型 (Meal)

**表名**: `meals`

**字段**:
| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | Integer | Primary Key, Index | 餐食ID |
| user_id | Integer | Foreign Key (users.id), Not Null | 用户ID |
| meal_type | String(50) | - | 餐食类型（breakfast/lunch/dinner/snack） |
| name | String(200) | - | 餐食名称 |
| calories | Integer | - | 总热量（千卡） |
| protein | Float | - | 蛋白质（克） |
| carbs | Float | - | 碳水化合物（克） |
| fat | Float | - | 脂肪（克） |
| meal_datetime | DateTime | - | 用餐时间 |
| notes | Text | - | 备注 |
| created_at | DateTime | Server Default: func.now() | 创建时间 |

**关系**:
- `user`: 多对一，关联User
- `food_items`: 一对多，关联FoodItem

### 3. 食物项模型 (FoodItem)

**表名**: `food_items`

**字段**:
| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | Integer | Primary Key, Index | 食物项ID |
| meal_id | Integer | Foreign Key (meals.id), Not Null | 餐食ID |
| name | String(200) | - | 食物名称 |
| grams | Float | - | 重量（克） |
| calories | Integer | - | 热量（千卡） |
| protein | Float | - | 蛋白质（克） |
| carbs | Float | - | 碳水化合物（克） |
| fat | Float | - | 脂肪（克） |

**关系**:
- `meal`: 多对一，关联Meal

### 4. 习惯模型 (Habit)

**表名**: `habits`

**字段**:
| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | Integer | Primary Key, Index | 习惯ID |
| user_id | Integer | Foreign Key (users.id), Not Null | 用户ID |
| name | String(200) | - | 习惯名称 |
| description | Text | - | 描述 |
| frequency | String(50) | - | 频率（daily/weekly） |
| target_count | Integer | - | 目标次数 |
| is_active | Boolean | Default: True | 是否活跃 |
| category | String(100) | - | 类别 |
| difficulty | String(50) | - | 难度（easy/medium/hard） |
| created_at | DateTime | Server Default: func.now() | 创建时间 |

**关系**:
- `user`: 多对一，关联User
- `completions`: 一对多，关联HabitCompletion
- `goals`: 一对多，关联HabitGoal

### 5. 习惯完成记录模型 (HabitCompletion)

**表名**: `habit_completions`

**字段**:
| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | Integer | Primary Key, Index | 完成记录ID |
| habit_id | Integer | Foreign Key (habits.id), Not Null | 习惯ID |
| completion_date | Date | - | 完成日期 |
| notes | Text | - | 备注 |
| created_at | DateTime | Server Default: func.now() | 创建时间 |

**关系**:
- `habit`: 多对一，关联Habit

### 6. 对话模型 (Conversation)

**表名**: `conversations`

**字段**:
| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | Integer | Primary Key, Index | 对话ID |
| user_id | Integer | Foreign Key (users.id), Not Null | 用户ID |
| title | String(200) | - | 对话标题 |
| current_role | String(50) | - | 当前AI角色 |
| created_at | DateTime | Server Default: func.now() | 创建时间 |
| updated_at | DateTime | onupdate: func.now() | 更新时间 |

**关系**:
- `user`: 多对一，关联User
- `messages`: 一对多，关联Message
- `role_history`: 一对多，关联RoleHistory

### 7. 消息模型 (Message)

**表名**: `messages`

**字段**:
| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | Integer | Primary Key, Index | 消息ID |
| conversation_id | Integer | Foreign Key (conversations.id), Not Null | 对话ID |
| role | String(20) | - | 角色（user/assistant） |
| content | Text | - | 消息内容 |
| tokens_used | Integer | - | 使用的token数 |
| model | String(100) | - | 使用的模型 |
| created_at | DateTime | Server Default: func.now() | 创建时间 |

**关系**:
- `conversation`: 多对一，关联Conversation

### 8. 健康记录模型 (HealthRecord)

**表名**: `health_records`

**字段**:
| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | Integer | Primary Key, Index | 健康记录ID |
| user_id | Integer | Foreign Key (users.id), Not Null | 用户ID |
| record_date | Date | - | 记录日期 |
| weight | Integer | - | 体重（克） |
| blood_pressure_systolic | Integer | - | 收缩压 |
| blood_pressure_diastolic | Integer | - | 舒张压 |
| heart_rate | Integer | - | 心率 |
| sleep_hours | Float | - | 睡眠时长（小时） |
| stress_level | Integer | - | 压力水平（1-10） |
| notes | Text | - | 备注 |
| created_at | DateTime | Server Default: func.now() | 创建时间 |

**关系**:
- `user`: 多对一，关联User

### 9. 游戏化模型

#### 9.1 用户积分模型 (UserPoints)
**表名**: `user_points`

**字段**:
| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | Integer | Primary Key, Index | 积分记录ID |
| user_id | Integer | Foreign Key (users.id), Not Null | 用户ID |
| total_points | Integer | Default: 0 | 总积分 |
| available_points | Integer | Default: 0 | 可用积分 |
| level_points | Integer | Default: 0 | 等级积分 |
| created_at | DateTime | Server Default: func.now() | 创建时间 |
| updated_at | DateTime | onupdate: func.now() | 更新时间 |

#### 9.2 徽章模型 (Badge)
**表名**: `badges`

**字段**:
| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | String(50) | Primary Key | 徽章ID |
| name | String(200) | - | 徽章名称 |
| description | Text | - | 描述 |
| category | String(100) | - | 类别 |
| icon | String(100) | - | 图标 |
| points_required | Integer | - | 所需积分 |
| criteria | Text | - | 获取条件（JSON） |

#### 9.3 用户徽章模型 (UserBadge)
**表名**: `user_badges`

**字段**:
| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | Integer | Primary Key, Index | 用户徽章ID |
| user_id | Integer | Foreign Key (users.id), Not Null | 用户ID |
| badge_id | String(50) | Foreign Key (badges.id), Not Null | 徽章ID |
| earned_at | DateTime | Server Default: func.now() | 获取时间 |
| showcased | Boolean | Default: False | 是否展示 |

### 10. 记忆系统模型

#### 10.1 用户长期记忆模型 (UserLongTermMemory)
**表名**: `user_long_term_memories`

**字段**:
| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | Integer | Primary Key, Index | 记忆ID |
| user_id | Integer | Foreign Key (users.id), Not Null | 用户ID |
| memory_type | String(50) | - | 记忆类型 |
| content | Text | - | 内容 |
| importance_score | Integer | - | 重要性评分 |
| last_accessed | DateTime | - | 最后访问时间 |
| created_at | DateTime | Server Default: func.now() | 创建时间 |

#### 10.2 上下文摘要模型 (ContextSummary)
**表名**: `context_summaries`

**字段**:
| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | Integer | Primary Key, Index | 摘要ID |
| user_id | Integer | Foreign Key (users.id), Not Null | 用户ID |
| summary_type | String(50) | - | 摘要类型 |
| content | Text | - | 内容 |
| period_start | Date | - | 周期开始 |
| period_end | Date | - | 周期结束 |
| created_at | DateTime | Server Default: func.now() | 创建时间 |

## 数据库关系图

```
users
├── health_records (1:n)
├── conversations (1:n)
│   └── messages (1:n)
├── habits (1:n)
│   ├── habit_completions (1:n)
│   └── habit_goals (1:n)
├── meals (1:n)
│   └── food_items (1:n)
├── water_intakes (1:n)
├── health_assessments (1:n)
├── long_term_memories (1:n)
├── context_summaries (1:n)
├── habit_patterns (1:n)
├── data_associations (1:n)
├── password_reset_tokens (1:n)
├── reward_redemptions (1:n)
└── calorie_goals (1:n)

gamification
├── user_points (1:1 with users)
├── user_badges (n:n with users and badges)
└── badges (master table)
```

## 迁移管理

### Alembic配置
- **配置文件**: `alembic.ini`
- **迁移目录**: `alembic/`
- **版本目录**: `alembic/versions/`

### 常用迁移命令
```bash
# 创建新迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1

# 查看迁移历史
alembic history

# 查看当前版本
alembic current
```

### 迁移策略
1. **自动生成迁移**: 修改模型后使用 `--autogenerate` 创建迁移
2. **手动审核迁移**: 检查自动生成的迁移脚本，确保正确性
3. **测试环境验证**: 在测试环境应用迁移并验证
4. **生产环境部署**: 在生产环境应用已验证的迁移

## 数据库配置

### 生产环境
```python
# PostgreSQL配置
DATABASE_URL = "postgresql://username:password@host:port/database"
```

### 开发/测试环境
```python
# SQLite配置
SQLITE_DATABASE_URL = "sqlite:///./weight_management.db"
```

### 连接池配置
- **最大连接数**: 根据服务器配置调整
- **连接超时**: 30秒
- **连接回收**: 定期回收空闲连接

## 数据完整性约束

### 外键约束
- 所有关联表都使用外键约束
- 级联删除策略：`cascade="all, delete-orphan"`
- 引用完整性：确保关联数据的一致性

### 唯一性约束
- 用户邮箱唯一
- 用户名唯一（可选）
- 组合唯一约束：如用户习惯名称唯一

### 数据验证
- 字段长度限制
- 数据类型验证
- 业务规则验证（如体重范围）

## 性能优化

### 索引策略
1. **主键索引**: 所有表的主键自动创建索引
2. **外键索引**: 所有外键字段创建索引
3. **查询字段索引**: 频繁查询的字段创建索引
4. **组合索引**: 多字段查询创建组合索引

### 查询优化
1. **延迟加载**: 使用延迟加载避免N+1查询问题
2. **预加载**: 关联数据使用预加载
3. **分页查询**: 大数据集使用分页查询
4. **查询缓存**: 频繁查询结果缓存

## 备份和恢复

### 备份策略
1. **定期全量备份**: 每天全量备份
2. **增量备份**: 每小时增量备份
3. **备份验证**: 定期验证备份完整性
4. **异地备份**: 备份数据存储到异地

### 恢复流程
1. **评估损坏程度**: 确定需要恢复的数据范围
2. **选择备份点**: 选择最近的可用备份
3. **恢复数据**: 应用备份数据
4. **验证恢复**: 验证数据完整性和一致性

## 数据安全

### 敏感数据保护
1. **密码哈希**: 使用bcrypt算法哈希密码
2. **个人数据加密**: 敏感个人数据加密存储
3. **访问控制**: 基于角色的数据访问控制
4. **审计日志**: 记录数据访问和修改日志

### 合规性要求
1. **数据最小化**: 只收集必要的数据
2. **用户同意**: 获取用户明确同意
3. **数据保留**: 制定数据保留策略
4. **数据删除**: 支持用户数据删除请求