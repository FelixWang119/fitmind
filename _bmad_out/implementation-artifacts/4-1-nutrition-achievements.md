# Story 4-1: 营养成就系统

**Epic**: 4 - 成就系统扩展  
**Story ID**: 4.1  
**Story Key**: `4-1-nutrition-achievements`  
**优先级**: P1  
**故事点数**: 8 pts  
**状态**: ready-for-dev  

---

## 📖 Story 描述

**作为** 用户  
**我想要** 完成营养相关的成就任务  
**以便** 获得积分奖励和徽章，激励健康饮食习惯  

---

## ✅ 验收标准 (BDD 格式)

### AC 4.1.1: 营养成就列表

**Given** 用户打开成就页面  
**When** 查看营养成就  
**Then** 显示营养相关成就:
- 连续记录饮食天数
- 达成热量目标次数
- 营养均衡达标天数
- 尝试新食物种类数

### AC 4.1.2: 成就进度追踪

**Given** 用户开始营养成就  
**When** 记录饮食  
**Then** 自动更新成就进度  
**And** 显示进度条和百分比

### AC 4.1.3: 成就奖励

**Given** 用户完成营养成就  
**When** 成就达成  
**Then** 发放积分奖励  
**And** 授予相应徽章

### AC 4.1.4: 营养成就类型

**Given** 系统配置  
**When** 查看成就类型  
**Then** 支持以下成就:
- `nutrition_streak_7` - 连续7天记录饮食
- `nutrition_streak_30` - 连续30天记录饮食
- `calorie_goal_met` - 达成热量目标
- `macro_balance` - 营养均衡
- `variety_explorer` - 尝试新食物

---

## 🏗️ 技术需求

### 后端 API

```python
# 扩展现有成就系统，添加营养成就相关端点
@router.get("/achievements/nutrition")
def get_nutrition_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取营养成就列表"""
    # 返回用户的营养成就及进度
```

### 前端

- 扩展现有的 Gamification 页面
- 添加营养成就标签页
- 显示成就进度和奖励

---

## 🔄 依赖关系

- **前置**: Epic 1 (Profile) - 已完成 ✅
- **后续**: Story 4.2 (运动成就扩展)

---

## 🧪 测试用例

1. `test_nutrition_achievements_list` - 营养成就列表
2. `test_achievement_progress_tracking` - 成就进度追踪
3. `test_achievement_reward_distribution` - 奖励发放
