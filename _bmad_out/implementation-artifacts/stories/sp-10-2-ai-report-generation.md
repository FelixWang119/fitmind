---
sprint: 5
story_id: SP-10.2
title: "AI 报告生成服务 (AI Report Generation Service)"
priority: P0
story_points: 8
status: ready-for-dev
created_date: "2026-03-02"
assignee: "Developer"
epic: 10
epic_title: "健康报告"
---

# Story SP-10.2: AI 报告生成服务 (AI Report Generation Service)

## 📋 用户故事

**作为** 系统  
**我想要** 自动生成 AI 解读的健康报告  
**以便** 用户获得自然语言的理解和行动指引

---

## 🎯 验收标准

### AI 解读内容  
- [ ] **日报内容**: 简洁总结当天健康状态（100-200字）
  - [ ] 饮食情况摘要
  - [ ] 运动/习惯完成状况
  - [ ] 提供第二天建议  

- [ ] **周报内容**: 包含趋势和模式，比日报更深入（200-300字）
  - [ ] 本周成就和进展
  - [ ] 需要关注的方面
  - [ ] 下周行动计划  

- [ ] **月报内容**: 宏观回顾和长期趋势（300-500字）
  - [ ] 月度变化趋势
  - [ ] 里程碑成就
  - [ ] 长期目标建议

### AI 生成逻辑
- [ ] **自然语言**: 输出温暖、专业、易懂的自然语言，避免数字和分数
- [ ] **个性化**: 基于用户的年龄、性别、目标、习惯等个人信息
- [ ] **积极鼓励**: 提供正向激励，识别用户的进步
- [ ] **可操作性**: 提供建设性的、具体的下一步行动建议

### 与数据服务集成
- [ ] **复用数据服务**: 使用已创建的 ReportDataService 提供的数据
- [ ] **API 接口**: 生成的报告可以通过接口访问
- [ ] **结构化输出**: 同时提供解读文本和关键指标

### 性能与质量
- [ ] **响应时间**: AI 生成时间不超过 5 秒
- [ ] **内容质量**: 输出自然流畅，无重复或矛盾内容
- [ ] **错误处理**: 优雅处理 AI 服务失效情况（提供默认回复）

---

## 📐 技术规格

### 文件位置

**新建文件:**
- `backend/app/services/ai_report_service.py` - AI 生成服务

**修改文件:**
- `backend/app/api/v1/endpoints/reports.py` - 在现有API基础上添加AI生成

### 服务要求

**模型接口:** 
```python
class AIReportGenerator:
    def generate_daily_summary(self, report_data: ReportData, user_profile: dict) -> str:
        """生成日报解读文本"""
        pass
        
    def generate_weekly_summary(self, report_data: ReportData, user_profile: dict) -> str:
        """生成周报解读文本"""  
        pass
        
    def generate_monthly_summary(self, report_data: ReportData, user_profile: dict) -> str:
        """生成月报解读文本"""
        pass
```

**API 集成示例:**
- 现有 `/reports/today` 端点将返回添加了解读字段的响应
- 返回结构中将包括 `.interpretation` 字段，包含AI生成的解读文本

---

## 🛠️ 实施建议

### AI 生成策略

1. **上下文构建**:
   - 基于 ReportData 提供的结构化数据
   - 添加用户个人信息 (年龄、性别、体重目标等)
   - 提供生成提示（prompt）模版，确保输出风格一致

2. **内容分层**:
   - 第一层：数据摘要（用户做了什么）
   - 第二层：模式分析（趋势和改进空间）
   - 第三层：激励与建议（积极强化 + 行动建议）

### 错误处理方案
- 如果 AI 服务失败，使用模板化回复兜底
- 记录错误日志以便优化
- 返回优雅错误而不中断应用流程

---

## 🚀 开发优先级

1. **基础实现**: 实现 `generate_daily_summary` 和基础API连接
2. **内容深化**: 添加周报和月报解读
3. **质量优化**: 改进提示设计，确保输出一致性
4. **容错机制**: 完善失败处理方案