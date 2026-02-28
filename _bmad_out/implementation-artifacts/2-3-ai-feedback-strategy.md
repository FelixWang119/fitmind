# Story 2.3: AI 反馈策略

**Epic**: 2 - 目标系统实现  
**Story ID**: 2.3  
**Story Key**: `2-3-ai-feedback-strategy`  
**优先级**: P0 (MVP 核心)  
**故事点数**: 5 pts  
**状态**: ready-for-dev  

---

## 📖 Story 描述

**作为** 用户  
**我想要** 在偏离目标时收到智能的反馈和建议  
**以便** 我能及时调整行为并保持动力  

---

## ✅ 验收标准 (BDD 格式)

### AC 2.3.1: 轻微偏离提醒 (1-2天)

**Given** 用户 1-2 天未记录或未达成目标  
**When** 系统检测到偏离  
**Then** 发送温和提醒消息:
- 提示未完成的内容
- 使用鼓励语气
- 提供简单可执行的小建议

**示例消息:**
- "今天还没记录运动哦，10 分钟散步也算数～要一起完成今天的目标吗？"
- "记得喝水呀！一杯水只需要 30 秒 💧"

### AC 2.3.2: 中度偏离询问 (3-5天)

**Given** 用户 3-5 天未达成目标  
**When** 系统检测到中度偏离  
**Then** 发送关切询问消息:
- 表达理解和关心
- 询问是否遇到困难
- 提供调整建议

**示例消息:**
- "注意到这几天运动打卡少了，是遇到什么困难了吗？我们可以调整计划让它更容易坚持 🤗"
- "最近睡眠记录有点少哦，是太忙了吗？哪怕提前 30 分钟上床也是进步呢～"

### AC 2.3.3: 严重偏离建议 (7天+)

**Given** 用户 7 天以上严重偏离目标  
**When** 系统检测到严重偏离  
**Then** 发送建议重新评估消息:
- 建议调整目标
- 强调目标是灵活的
- 提供重新开始的支持

**示例消息:**
- "看起来当前的计划执行起来有些挑战。要不要我们一起重新调整目标？目标是活的，我们可以让它更适合你现在的节奏～"
- "健康是一辈子的马拉松，不急于一时。我们可以先从小目标开始你觉得怎么样？"

### AC 2.3.4: 超额完成鼓励

**Given** 用户连续 2 周以上超额完成目标  
**When** 系统检测到超额  
**Then** 发送庆祝鼓励消息:
- 肯定用户努力
- 询问是否要挑战更高目标

**示例消息:**
- "太棒了！你已经连续两周超额完成目标了 🎉 要挑战一下更高的目标吗？"
- "你是最棒的！看到你的进步我都忍不住要为你鼓掌了 👏 继续保持！"

### AC 2.3.5: 目标达成庆祝

**Given** 用户达成目标  
**When** 目标状态变为 completed  
**Then** 发送庆祝消息:
- 庆祝达成
- 肯定努力过程
- 建议下一步

**示例消息:**
- "🎉 恭喜你达成目标！这是你努力的成果！接下来有什么新目标吗？"
- "太为你骄傲了！这一路走来不容易，你坚持下来了！现在可以好好奖励自己一下～"

### AC 2.3.6: 反馈触发机制

**Given** 用户有活跃目标  
**When** 每日定时任务运行  
**Then** 检查:
- 连续未达成天数
- 连续超额完成天数
- 目标完成状态
- 发送相应的 AI 反馈消息

### AC 2.3.7: 反馈历史记录

**Given** AI 发送了反馈  
**When** 反馈已发送  
**Then** 记录到数据库:
- 反馈内容
- 触发原因
- 发送时间
- 用户响应 (可选)

---

## 🏗️ 技术需求

### AI 反馈服务

**文件位置**: `backend/app/services/goal_feedback.py`

```python
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.goal import UserGoal, GoalProgress, GoalStatus


class FeedbackLevel(str):
    """反馈级别"""
    MILD = "mild"      # 轻微偏离 (1-2天)
    MODERATE = "moderate"  # 中度偏离 (3-5天)
    SEVERE = "severe"  # 严重偏离 (7天+)
    EXCEEDING = "exceeding"  # 超额完成
    COMPLETED = "completed"  # 达成目标


class GoalFeedbackService:
    """AI 目标反馈服务"""
    
    # 消息模板配置
    MESSAGES = {
        "weight": {
            FeedbackLevel.MILD: [
                "今天还没记录体重哦，早起空腹称重最准确～",
                "记得记录今天的体重数据，这样才能更好地追踪进度呢！",
            ],
            FeedbackLevel.MODERATE: [
                "注意到这周体重记录少了，是有点忙吗？我们可以慢慢来～",
                "体重波动是正常的，关键是坚持记录。你遇到什么困难了吗？",
            ],
            FeedbackLevel.SEVERE: [
                "看起来体重记录暂停了一段时间。要不要我们一起重新制定计划？",
                "健康是一辈子的事情，我们可以调整目标让它更适合你现在的节奏。",
            ],
            FeedbackLevel.EXCEEDING: [
                "太棒了！体重下降趋势很稳定！你是怎么做到的？",
                "看到你的进步太开心了！继续保持这个节奏！",
            ],
        },
        "exercise": {
            FeedbackLevel.MILD: [
                "今天还没记录运动哦，10分钟散步也算数～要一起完成今天的目标吗？",
            ],
            FeedbackLevel.MODERATE: [
                "注意到这几天运动打卡少了，是遇到什么困难了吗？我们可以调整计划让它更容易坚持 🤗",
            ],
            FeedbackLevel.SEVERE: [
                "看起来当前的运动计划执行起来有些挑战。要不要我们一起重新调整目标？",
            ],
            FeedbackLevel.EXCEEDING: [
                "运动达人就是你！💪 连续超额完成，太厉害了！",
            ],
        },
        "diet": {
            FeedbackLevel.MILD: [
                "今天的三餐都记录了吗？哪怕少记一顿也能帮助我们了解饮食习惯～",
            ],
            FeedbackLevel.MODERATE: [
                "最近饮食记录有点不规律，是外出就餐多了还是太忙了？我们可以一起看看怎么调整～",
            ],
            FeedbackLevel.SEVERE: [
                "饮食记录暂停了一段时间。健康的饮食习惯需要慢慢培养，我们可以从小的改变开始！",
            ],
            FeedbackLevel.EXCEEDING: [
                "饮食控制得非常好！你的意志力真的太强了！",
            ],
        },
        "habit": {
            FeedbackLevel.MILD: [
                "今天的水喝够了吗？一杯水只需要 30 秒 💧",
                "记得休息哦！良好的睡眠也是健康的重要组成部分～",
            ],
            FeedbackLevel.MODERATE: [
                "最近睡眠记录有点少哦，是太忙了吗？哪怕提前 30 分钟上床也是进步呢～",
            ],
            FeedbackLevel.SEVERE: [
                "生活习惯的养成需要时间，我们可以一起制定一个更容易坚持的计划！",
            ],
            FeedbackLevel.EXCEEDING: [
                "你的生活习惯越来越健康了！为你骄傲！",
            ],
        },
    }
    
    # 庆祝消息 (所有类型通用)
    COMPLETION_MESSAGES = [
        "🎉 恭喜你达成目标！这是你努力的成果！接下来有什么新目标吗？",
        "太为你骄傲了！这一路走来不容易，你坚持下来了！现在可以好好奖励自己一下～",
        "你做到了！每一次进步都值得庆祝！接下来我们挑战更高的目标吧？",
    ]
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_and_send_feedback(self, user_id: int) -> Optional[dict]:
        """检查并发送反馈"""
        # 获取用户所有活跃目标
        goals = self.db.query(UserGoal).filter(
            UserGoal.user_id == user_id,
            UserGoal.status == GoalStatus.ACTIVE.value
        ).all()
        
        feedback_results = []
        
        for goal in goals:
            feedback = self._analyze_goal(goal)
            if feedback:
                feedback_results.append(feedback)
        
        return feedback_results if feedback_results else None
    
    def _analyze_goal(self, goal: UserGoal) -> Optional[dict]:
        """分析单个目标并生成反馈"""
        # 获取最近进度
        recent_progress = self.db.query(GoalProgress).filter(
            GoalProgress.goal_id == goal.goal_id
        ).order_by(GoalProgress.recorded_date.desc()).limit(14).all()
        
        if not recent_progress:
            # 没有进度记录，检查天数
            days_since_start = (datetime.now() - goal.start_date).days
            if days_since_start >= 1:
                return self._generate_feedback(goal, FeedbackLevel.MILD, "无进度记录")
            return None
        
        # 检查连续未达成天数
        consecutive_missed = 0
        consecutive_completed = 0
        
        for progress in recent_progress:
            if progress.daily_target_met:
                consecutive_completed += 1
                consecutive_missed = 0
            else:
                consecutive_missed += 1
                consecutive_completed = 0
        
        # 判断反馈级别
        if goal.status == GoalStatus.COMPLETED.value:
            level = FeedbackLevel.COMPLETED
            reason = "目标达成"
        elif consecutive_completed >= 14:
            level = FeedbackLevel.EXCEEDING
            reason = "连续14天超额完成"
        elif consecutive_missed >= 7:
            level = FeedbackLevel.SEVERE
            reason = f"连续{consecutive_missed}天未达成"
        elif consecutive_missed >= 3:
            level = FeedbackLevel.MODERATE
            reason = f"连续{consecutive_missed}天未达成"
        elif consecutive_missed >= 1:
            level = FeedbackLevel.MILD
            reason = f"{consecutive_missed}天未达成"
        else:
            return None  # 正常，无需反馈
        
        return self._generate_feedback(goal, level, reason)
    
    def _generate_feedback(self, goal: UserGoal, level: str, reason: str) -> dict:
        """生成反馈消息"""
        import random
        
        if level == FeedbackLevel.COMPLETED:
            message = random.choice(self.COMPLETION_MESSAGES)
        else:
            messages = self.MESSAGES.get(goal.goal_type, {}).get(level, [])
            message = random.choice(messages) if messages else "继续加油！"
        
        return {
            "goal_id": goal.goal_id,
            "goal_type": goal.goal_type,
            "level": level,
            "reason": reason,
            "message": message,
            "created_at": datetime.now(),
        }
```

### 定时任务

**文件位置**: `backend/app/tasks/goal_feedback_task.py`

```python
from datetime import datetime
from celery import Task
from app.core.celery import celery_app


@celery_app.task(name="goal_feedback_daily")
def send_daily_goal_feedback():
    """每日目标反馈任务"""
    from app.core.database import SessionLocal
    from app.services.goal_feedback import GoalFeedbackService
    
    db = SessionLocal()
    try:
        # 获取所有有活跃目标的用户
        from app.models.user import User
        from app.models.goal import UserGoal
        
        user_ids = db.query(UserGoal.user_id).filter(
            UserGoal.status == "active"
        ).distinct().all()
        
        feedback_service = GoalFeedbackService(db)
        
        results = []
        for (user_id,) in user_ids:
            feedback = feedback_service.check_and_send_feedback(user_id)
            if feedback:
                results.append({"user_id": user_id, "feedback": feedback})
        
        return {"sent": len(results), "details": results}
    
    finally:
        db.close()
```

### API 端点 (手动触发)

**文件位置**: `backend/app/api/v1/endpoints/goals.py`

```python
@router.get("/feedback/check")
def check_goal_feedback(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """手动检查目标反馈"""
    from app.services.goal_feedback import GoalFeedbackService
    
    service = GoalFeedbackService(db)
    feedback = service.check_and_send_feedback(current_user.id)
    
    if not feedback:
        return {"message": "一切正常！继续加油～", "feedback": []}
    
    return {"feedback": feedback}


@router.post("/feedback/{goal_id}/dismiss")
def dismiss_feedback(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记反馈为已处理"""
    # 记录用户选择 (忽略/调整目标/稍后提醒)
    return {"message": "已记录你的选择～"}
```

---

## 🔄 依赖关系

- **前置**: 
  - Story 1.6 (目标数据模型) - 已完成 ✅
  - Story 2.2 (目标创建与追踪) - 本 Epic 内
- **后续**: 无 (Epic 2 结束)

---

## 🧪 测试用例

1. `test_mild_feedback_1_2_days` - 1-2天未达成生成温和提醒
2. `test_moderate_feedback_3_5_days` - 3-5天未达成生成关切询问
3. `test_severe_feedback_7_days` - 7天+未达成生成重新评估建议
4. `test_exceeding_feedback_14_days` - 14天超额完成生成庆祝消息
5. `test_completion_message` - 目标达成生成庆祝消息
6. `test_no_feedback_on_track` - 正常进度不发送反馈
7. `test_feedback_message_persistence` - 反馈记录保存到数据库
