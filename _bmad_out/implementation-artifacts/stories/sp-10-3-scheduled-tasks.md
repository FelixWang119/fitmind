---
sprint: 5
story_id: SP-10.3
title: "定时任务调度 (Scheduled Tasks for Report Generation)"
priority: P0
story_points: 5
status: ready-for-dev
created_date: "2026-03-02"
assignee: "Developer"
epic: 10
epic_title: "健康报告"
---

# Story SP-10.3: 定时任务调度 (Scheduled Tasks for Report Generation)

## 📋 用户故事

**作为** 系统  
**我想要** 按照设定的时间自动生成健康报告  
**以便** 用户无需主动触达，可以获得持续的健康状态跟踪

---

## 🎯 验收标准

### 自动报告生成
- [ ] **每日自动生成**: 每天凌晨 2:00 自动为所有用户生成日报 (默认包含AI解读)  
- [ ] **每周自动生成**: 每周日凌晨 2:00 自动为所有用户生成周报
- [ ] **每月自动生成**: 每月1号凌晨 2:00 自动为所有用户生成月报  
- [ ] **批量处理**: 当有大量用户时能够批量高效处理

### 定时任务机制
- [ ] **任务调度系统**: 使用 APScheduler 或类似机制来管理工作
- [ ] **错误处理**: 当处理某个用户失败时不会影响其他用户的生成过程
- [ ] **日志记录**: 详细的任务执行日志方便调试
- [ ] **手动触发**: 支持管理人员手动触发报告生成

### 任务执行优化  
- [ ] **性能考量**: 为不同规模的用户群体制定处理策略（并发控制、批次处理）
- [ ] **资源管理**: 确保定期任务不会对系统整体性能产生负面影响
- [ ] **失败重试**: 处定的失败重试机制（例如3次重试机会）

### 报告存储
- [ ] **报告归档**: 生成的报告会存储到数据库中以供访问
- [ ] **历史保留**: 实现合理的数据清理策略（保留最近x个月的数据）
- [ ] **关联用户**: 正确地将生成的报告与相应用户关联

---

## 📐 技术规格

### 文件位置

**新建文件:**
- `backend/app/schedulers/tasks/report_generation_tasks.py` - 报告生成定时任务
- `backend/app/schedulers/scheduler.py` - (若不存在) 向APScheduler配置入口

### 任务定义

```python
class ReportGenerationScheduler:
    @staticmethod
    async def generate_daily_reports():
        """定时生成所有用户的日报，含AI解读"""
        pass
        
    @staticmethod
    async def generate_weekly_reports():
        """定时生成所有用户的周报，含AI解读"""
        pass
        
    @staticmethod
    async def generate_monthly_reports():
        """定时生成所有用户的月报，含AI解读"""
        pass
```

### 数据表结构
- 更新或创建 `ReportHistory` 表来存储历史报告
- 包含字段：user_id, report_type, report_data, ai_interpretation, generated_at

---

## 🛠️ 实施建议

### 任务调度框架
1. 使用APScheduler的CronTrigger实现定时任务
2. 考虑使用后台任务队列(如Celery)处理大批量用户情况
3. 添加健康检查端点来验证定时任务是否在运行

### 错误恢复
1. 实现每个用户独立的任务包装函数
2. 任务失败时记录日志并发送告警
3. 对重复性失败实施指数退避策略

---

## 🚀 开发优先级

1. **基础调度**: 实现基本的定时任务框架
2. **报告生成**: 添加各类报告的生成逻辑
3. **批量处理**: 完善针对不同用户规模的处理逻辑  
4. **错误处理**: 完善异常处理和日志记录机制