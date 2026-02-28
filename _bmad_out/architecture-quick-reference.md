# 体重管理 AI 助手 - 快速参考 (Quick Reference)

**文档**: 架构设计摘要  
**日期**: 2026-02-27  
**版本**: 1.0

---

## 🎯 P0 核心架构决策

### 1. 数据模型扩展

**新增表 (3 个):**
- `user_goals` - 用户目标主表
- `goal_progress` - 目标进度记录
- `goal_history` - 目标变更历史

**扩展表 (1 个):**
- `users` - 扩展到 17 个档案字段

**现有表复用:**
- `exercise_checkins` - 运动打卡 (已有)
- `meals` - 餐饮记录 (已有)
- `unified_memory` - 统一记忆 (已有,需扩展)

### 2. API 端点设计

**新增 v2.0 端点 (10 个):**
```
GET    /api/v2/users/me/profile              # 获取档案
PUT    /api/v2/users/me/profile              # 更新档案
GET    /api/v2/goals                         # 获取所有目标
POST   /api/v2/goals                         # 创建目标
POST   /api/v2/goals/{id}/progress           # 记录进度
GET    /api/v2/calorie-balance/today         # 热量平衡
GET    /api/v2/exercise/checkins             # 运动记录
POST   /api/v2/exercise/checkins             # 打卡运动
GET    /api/v2/achievements                  # 成就列表
POST   /api/v2/exercise/checkins             # 运动打卡
```

**向后兼容 v1.0:**
- GET/PUT `/api/v1/users/me` → 扩展到 17 字段
- GET `/api/v1/health` → 新增扩展字段

### 3. AI 记忆集成

**触发机制:**
```
UserProfile → UnifiedMemory (同步)
          ↓
    pgvector (嵌入)
          ↓
    语义搜索 (向量相似度)
          ↓
  AI 对话引用
```

**记忆维度:**
- 基准信息 (benchmark)
- 偏好记忆 (preference)
- 行为模式 (behavior)
- 上下文信息 (context)

**技术栈:**
- 向量数据库: pgvector (PostgreSQL)
- 向量维度: 768
- 嵌入模型: BGE-Small-ZH-V1.5

### 4. 热量平衡计算架构

**公式:**
```
热量盈余 = 摄入热量 - 基础代谢 - 运动消耗
```

**计算策略:**
- 实时: 运动打卡后立即更新
- 缓存: BMR/TDEE (30分钟), 热量平衡 (2分钟)
- 聚合: 三栏对比 (摄入 vs 基础代谢 vs 运动消耗)

**运动打卡集成:**
```
运动打卡 → calories_burned
      ↓
   热量平衡计算
      ↓
   前端实时显示
```

---

## 📊 P1 技术选型

### 前端组件

| 需求 | 选型 | 理由 |
|------|------|------|
| UI 框架 | Ant Design | 已有技术栈,零学习成本 |
| 图表 | Chart.js | 轻量级,已集成 |
| 状态 | Zustand | 已有技术栈 |
| 输入 | Ant Design Forms | 表单验证成熟 |

### 后端服务

| 服务 | 技术 | 选择理由 |
|------|------|----------|
| Web 框架 | FastAPI | 性能优异,异步支持 |
| ORM | SQLAlchemy | 成熟稳定 |
| 向量搜索 | pgvector | 简化基础设施,成本低 |
| 缓存 | Redis | 现有部署 |
| 调度 | APScheduler | 已有经验 |

---

## 🗂️ 数据迁移策略

### 迁移步骤

```
1. 备份数据库 (pg_dump)
2. 添加新字段 (Alembic)
3. 创建新表 (Alembic)
4. 填充现有数据 (backfill)
5. 数据验证 (checksums)
6. 生产部署
```

### 关键脚本

**添加扩展字段:**
```python
op.add_column("users", Column("current_weight", Integer))
op.add_column("users", Column("waist_circumference", Integer))
op.add_column("users", Column("health_conditions", Text))  # JSON
```

**创建目标表:**
```python
op.create_table("user_goals", ...)
op.create_table("goal_progress", ...)
op.create_table("goal_history", ...)
```

**单位转换:**
```
Database:  grams (70000)
Frontend:  kilograms (70.0)
Formula:   kg × 1000 = g
```

---

## ⚡ 性能优化

### 索引策略

```sql
-- 核心索引
CREATE INDEX idx_user_goals_user_type ON user_goals (user_id, goal_type);
CREATE INDEX idx_goal_progress_goal_date ON goal_progress (goal_id, recorded_date);
CREATE INDEX idx_exercise_user_date ON exercise_checkins (user_id, started_at DESC);
CREATE INDEX idx_meal_user_date ON meals (user_id, meal_datetime DESC);
CREATE INDEX idx_unified_memory_embedding ON unified_memory 
    USING ivfflat (embedding vector_cosine_ops);
```

### 缓存策略

| 数据 | TTL | 位置 |
|------|-----|------|
| User Profile | 300s | Redis |
| Calorie Balance | 120s | Redis |
| BMR/TDEE | 1800s | Redis |
| Exercise Types | 86400s | Redis |

### 计算策略

| 计算 | 策略 | 频率 |
|------|------|------|
| BMR/TDEE | 缓存 | 每日更新 |
| 热量平衡 | 缓存+实时 | 每餐/运动后 |
| 目标进度 | 实时计算 | 实时更新 |
| 运动消耗 | 实时计算 | 打卡时 |

---

## 🔒 安全措施

### 加密

```
静态加密: AES-256 (PG TDE)
传输加密: TLS 1.3
敏感字段: Fernet 加密 (health_conditions, medications)
```

### 访问控制

```
RBAC 实现:
- 用户: read:health, write:health
- 管理员: manage:config, manage:users

OAuth2 + JWT 认证
```

### 审计日志

```python
class AuditLog(Base):
    action = Column(String(100))  # 'profile.update'
    resource_type = Column(String(50))
    old_value = Column(Text)  # JSON
    new_value = Column(Text)  # JSON
    ip_address = Column(String(50))
```

### 合规性

- **数据最小化**: 仅收集必要健康数据
- **用户同意**: 显式同意机制
- **数据导出**: `/api/v2/users/me/data-export`
- **删除权利**: 软删除支持

---

## 📈 下一步行动

### 立即任务 (Week 1-2)

```
✅ 创建 Epic/Story 拆解
✅ 设置开发环境
✅ 编写迁移脚本
✅ 实现 User Profile Extension
```

### P0 完成 (Week 3-4)

```
✅ 数据库迁移完成
✅ v2.0 API 实现
✅ 新增模型创建
✅ 单元测试覆盖 >80%
```

### Q1 目标 (Month 2)

```
✅ 生产部署
✅ 用户测试
✅ 性能优化
✅ 安全审计
```

---

## 📚 参考文档

| 文档 | 位置 | 说明 |
|------|------|------|
| PRD | `/docs/PRD.md` | 产品需求文档 v1.2 |
| Epics | `_bmad_out/planning-artifacts/epics.md` | 19 个 Stories |
| UX | `_bmad_out/planning-artifacts/ux-design-specification.md` | 设计规范 |
| Context | `_bmad_out/project-context-weight-ai.md` | 项目上下文 |
| Architecture | **本文件** | 架构设计 |

---

## ✅ 验证清单

```
架构评审:
✅ 技术选型合理
✅ 向后兼容性保证
✅ 扩展性设计
✅ 性能优化策略
✅ 安全措施充分

实施准备:
✅ 数据库迁移脚本
✅ API 版本控制
✅ 测试策略
✅ 监控方案
```

---

**状态**: ✅ 完成  
**最后更新**: 2026-02-27  
**维护者**: BMAD Architect Agent
