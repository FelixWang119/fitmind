# Story 4-2: 运动成就系统扩展

**Epic**: 4 - 成就系统扩展  
**Story ID**: 4.2  
**Story Key**: `4-2-exercise-achievements-extension`  
**优先级**: P1  
**故事点数**: 13 pts  
**状态**: ready-for-dev  

---

## 📖 Story 描述

**作为** 用户  
**我想要** 完成运动相关的成就任务  
**以便** 获得积分奖励和徽章，激励坚持运动  

---

## ✅ 验收标准 (BDD 格式)

### AC 4.2.1: 运动成就列表

**Given** 用户打开成就页面  
**When** 查看运动成就  
**Then** 显示运动相关成就:
- 连续运动天数
- 完成运动目标次数
- 累计运动时长
- 尝试不同运动类型

### AC 4.2.2: 运动类型成就

**Given** 用户完成不同类型运动  
**When** 达成成就条件  
**Then** 解锁对应成就:
- 有氧运动成就
- 力量训练成就
- 柔韧性训练成就

### AC 4.2.3: 运动里程碑成就

**Given** 用户累计运动数据  
**When** 达到里程碑  
**Then** 授予里程碑徽章:
- 累计100公里跑步
- 累计1000分钟运动
- 连续运动30天

### AC 4.2.4: 成就排行榜

**Given** 用户查看成就  
**When** 查看排行榜  
**Then** 显示:
- 用户排名
- 全球/好友排行榜
- 成就解锁百分比

---

## 🏗️ 技术需求

### 后端 API

```python
@router.get("/achievements/exercise")
def get_exercise_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取运动成就列表"""
    # 返回用户的运动成就及进度

@router.get("/achievements/leaderboard")
def get_achievement_leaderboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取成就排行榜"""
    # 返回排行榜数据
```

### 前端

- 扩展 Gamification 页面
- 添加运动成就标签页
- 添加排行榜组件

---

## 🔄 依赖关系

- **前置**: Story 4.1 (营养成就) - 本 Epic 内
- **后续**: 无

---

## 🧪 测试用例

1. `test_exercise_achievements_list` - 运动成就列表
2. `test_exercise_type_achievements` - 运动类型成就
3. `test_milestone_achievements` - 里程碑成就
4. `test_leaderboard_ranking` - 排行榜排名
