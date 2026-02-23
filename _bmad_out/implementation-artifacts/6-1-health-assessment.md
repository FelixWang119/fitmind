# Story 6.1: 健康评估系统 (Health Assessment System)

## Story Overview

**Epic:** 6 - 智能健康评估与建议系统 (Intelligent Health Assessment and Recommendation System)

**Story ID:** 6.1

**Story Title:** 健康评估系统 (Health Assessment System)

**Story Type:** Functional Feature

**Priority:** High

**Estimated Effort:** Large

---

## User Story

作为关注全面健康的用户，
我想要获得综合的健康评估，
以便我可以了解我在营养、行为、情感三个维度的整体健康状况，并获得针对性的改进建议。

---

## Description

健康评估系统是智能健康评估与建议系统的核心功能模块。该系统通过整合用户在营养管理、行为习惯、情感支持三个维度的数据，进行综合分析并生成健康评分（0-100分）。

系统支持：
- 三维度健康评估（营养、行为、情感）
- 综合健康评分计算
- 各维度详细分析
- 历史评估对比

---

## Technical Context

### Dependencies
- **Data Models Required:**
  - user_profiles (用户档案表)
  - food_logs (饮食记录表)
  - habit_logs (习惯打卡表)
  - health_data (健康数据表)
  - conversations (对话表，用于情感分析)
  - sleep_logs (睡眠记录表)
  - exercise_logs (运动记录表)

- **Backend Services Required:**
  - Assessment Calculation Service (评估计算服务)
  - Historical Data Service (历史数据服务)
  - AI Analysis Service (AI分析服务)

- **Frontend Components Required:**
  - Assessment Dashboard (评估仪表盘)
  - Score Visualization (评分可视化)
  - Dimension Detail Cards (维度详情卡片)
  - Historical Comparison Chart (历史对比图表)

---

## Acceptance Criteria

### AC 6.1.1: 三维度健康评估

**Given** 用户已登录系统并拥有健康数据
**When** 用户进入健康评估页面并点击"开始评估"按钮
**Then** 系统执行三维度健康评估：
- 营养维度评估：分析用户饮食记录、热量摄入、营养均衡情况
- 行为维度评估：分析用户习惯打卡数据、运动频率、睡眠质量
- 情感维度评估：分析用户情绪记录、对话情感趋势、心理状态

**And** 系统为每个维度生成评分（0-100分）

---

### AC 6.1.2: 综合健康评分计算

**Given** 系统完成三维度评估
**When** 系统计算综合健康评分
**Then** 系统按照以下权重计算综合评分：
- 营养维度权重：35%
- 行为维度权重：35%
- 情感维度权重：30%

**And** 综合评分显示为0-100分的数值
**And** 评分附带等级标签：
- 0-39: 需改善
- 40-59: 一般
- 60-79: 良好
- 80-100: 优秀

---

### AC 6.1.3: 维度详细分析

**Given** 用户查看评估结果
**When** 用户点击具体维度查看详情
**Then** 系统显示该维度的详细分析：
- **营养维度详情：**
  - 热量摄入情况（与TDEE对比）
  - 宏量营养素比例（蛋白质、碳水、脂肪）
  - 饮食规律性分析
  - 建议摄入量对比

- **行为维度详情：**
  - 习惯完成率统计
  - 运动频率分析
  - 睡眠质量评估
  - 作息规律性分析

- **情感维度详情：**
  - 情绪稳定性分析
  - 压力水平评估
  - 积极情绪占比
  - 需要关注的情绪模式

**And** 每个维度提供3-5条具体改进建议

---

### AC 6.1.4: 历史评估对比

**Given** 用户有历史评估记录
**When** 用户在评估详情页查看历史对比
**Then** 系统显示：
- 最近5次评估的综合评分趋势图
- 各维度评分变化趋势
- 评估时间线对比

**And** 系统标注：
- 进步的维度（绿色箭头）
- 退步的维度（红色箭头）
- 保持稳定的维度（灰色横线）

**And** 显示与上次评估相比的变化百分比

---

### AC 6.1.5: 评估数据完整性检查

**Given** 用户健康数据不完整
**When** 系统执行健康评估
**Then** 系统检查数据完整性：
- 过去7天的饮食记录
- 过去14天的习惯打卡记录
- 过去7天的睡眠记录

**And** 如果某类数据缺失：
- 显示"数据不足"提示
- 基于可用数据计算评分
- 在评估报告中标注数据缺失的影响

---

### AC 6.1.6: 评估触发机制

**Given** 用户在系统中有足够数据
**When** 以下任一条件满足：
- 用户手动点击"开始评估"
- 用户首次完成所有档案设置7天后
- 用户已有14天未进行评估

**Then** 系统允许执行健康评估

---

### AC 6.1.7: 评估结果持久化

**Given** 健康评估完成
**When** 系统生成评估结果
**Then** 系统保存评估记录到数据库：
- 评估时间戳
- 综合评分及等级
- 各维度评分
- 评估建议摘要
- 数据完整状态

**And** 用户可以查看历史所有评估记录

---

### AC 6.1.8: 评估性能要求

**Given** 评估请求发起
**When** 系统执行健康评估
**Then** 评估计算时间 < 3秒
**And** 数据库查询时间 < 1秒
**And** 评估结果缓存时间30分钟

---

### AC 6.1.9: 评估结果展示

**Given** 评估完成
**When** 系统返回评估结果
**Then** 前端展示：
- 综合健康评分圆形进度条
- 三维度评分条形图
- 各维度"查看详情"展开按钮
- 历史对比趋势图入口
- "获取详细建议"按钮

**And** 动画效果：评分数字从0递增到实际值

---

### AC 6.1.10: AI增强评估建议

**Given** 用户查看评估结果
**When** 用户点击"获取详细建议"按钮
**Then** 系统调用AI服务：
- 分析用户当前健康状态
- 结合用户个人档案（目标、体重、偏好）
- 生成个性化深度建议

**And** 建议内容包含：
- 针对薄弱维度的优先改进建议
- 与用户目标对齐的行动计划
- 预期改进效果的时间估算

---

## Implementation Notes

### Database Schema (New Tables)

```sql
-- 健康评估记录表
CREATE TABLE health_assessments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 综合评分
    overall_score INTEGER NOT NULL,
    overall_grade VARCHAR(20) NOT NULL,
    
    -- 营养维度
    nutrition_score INTEGER NOT NULL,
    nutrition_details JSONB,
    
    -- 行为维度
    behavior_score INTEGER NOT NULL,
    behavior_details JSONB,
    
    -- 情感维度
    emotion_score INTEGER NOT NULL,
    emotion_details JSONB,
    
    -- 评估建议
    suggestions JSONB,
    
    -- 数据完整性状态
    data_completeness JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### API Endpoints

- `POST /api/assessments` - 执行健康评估
- `GET /api/assessments/latest` - 获取最新评估结果
- `GET /api/assessments/history` - 获取历史评估列表
- `GET /api/assessments/{id}` - 获取具体评估详情

### Scoring Algorithm

```python
def calculate_nutrition_score(food_logs, user_profile):
    """
    营养评分计算逻辑：
    - 热量均衡度：与TDEE对比 (30分)
    - 宏量营养素比例：蛋白质、碳水、脂肪平衡 (25分)
    - 饮食规律：三餐规律性 (20分)
    - 营养多样性：食物种类丰富度 (15分)
    - 健康饮食习惯：少油少盐少糖 (10分)
    """
    pass

def calculate_behavior_score(habit_logs, exercise_logs, sleep_logs):
    """
    行为评分计算逻辑：
    - 习惯完成率：打卡完成比例 (30分)
    - 运动频率：每周运动次数 (25分)
    - 睡眠质量：睡眠时长和质量 (25分)
    - 作息规律：作息时间一致性 (20分)
    """
    pass

def calculate_emotion_score(emotion_logs, conversations):
    """
    情感评分计算逻辑：
    - 情绪稳定性：情绪波动程度 (30分)
    - 积极情绪占比：正面情绪比例 (25分)
    - 压力水平：压力指标 (25分)
    - 心理韧性：应对能力评估 (20分)
    """
    pass

def calculate_overall_score(nutrition, behavior, emotion):
    """
    综合评分计算：
    - 营养权重：35%
    - 行为权重：35%
    - 情感权重：30%
    """
    return nutrition * 0.35 + behavior * 0.35 + emotion * 0.30
```

---

## Out of Scope (For Future Stories)

- Story 6.2: 健康趋势分析（预测模型、长期趋势）
- Story 6.3: 个性化建议系统（AI驱动的深度建议）
- Story 6.4: 数据可视化增强（高级图表、自定义报表）

---

## Definition of Done

- [ ] 后端API实现完成并通过单元测试
- [ ] 数据库表创建并迁移成功
- [ ] 前端评估页面实现
- [ ] 评分计算逻辑正确实现
- [ ] 历史对比功能实现
- [ ] 代码审查通过
- [ ] 集成测试通过
- [ ] 文档更新完成

---

## Dependencies on Other Stories

- **依赖：** Epic 1 (用户档案) - 需要用户基础数据
- **依赖：** Epic 3 (健康数据记录) - 需要饮食、运动、睡眠数据
- **依赖：** Epic 4 (行为习惯) - 需要习惯打卡数据

---

## Story Metadata

| Field | Value |
|-------|-------|
| Story ID | 6.1 |
| Epic ID | 6 |
| Status | Ready for Development |
| Created | 2026-02-23 |
| Estimated Points | 8 |
| Actual Points | TBD |
| Assignee | TBD |
| Reviewer | TBD |

---

## Related Documents

- [Epic 6 规划文档](./epics.md)
- [技术规格文档](./tech-spec-weight-management-ai-agent-docker-mvp.md)
- [PRD需求文档](../planning-artifacts/PRD.md)
