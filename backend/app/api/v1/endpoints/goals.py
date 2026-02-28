"""
目标管理 API 端点
Story 2.1: 目标推荐
Story 2.2: 目标创建与追踪
"""

from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.models.goal import UserGoal, GoalProgress, GoalHistory, GoalStatus
from app.schemas.goal import (
    GoalCreate,
    GoalUpdate,
    GoalResponse,
    GoalProgressCreate,
    GoalProgressResponse,
    GoalListResponse,
    GoalRecommendationRequest,
    GoalRecommendationResponse,
    AllRecommendationsResponse,
    PredictionResponse,
)
from app.services.goal_recommendation import GoalRecommendationService

router = APIRouter(prefix="/goals", tags=["goals"])


# ==================== 目标推荐端点 ====================


@router.get("/recommendations", response_model=AllRecommendationsResponse)
def get_all_recommendations(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    获取所有目标推荐

    基于用户档案数据，生成个性化的目标推荐
    """
    # 从数据库获取用户档案
    user_profile = {
        "height": current_user.height,
        "current_weight": current_user.current_weight,
        "age": current_user.age,
        "gender": current_user.gender,
        "activity_level": current_user.activity_level,
    }

    # 获取用户当前的习惯数据
    # TODO: 从 habit 或其他表获取当前步数、饮水量、睡眠等

    service = GoalRecommendationService()
    recommendations = service.get_all_recommendations(user_profile)

    return recommendations


@router.post("/recommendations", response_model=GoalRecommendationResponse)
def get_goal_recommendation(
    request: GoalRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取指定类型的目标推荐

    - goal_type: 目标类型 (weight/exercise/diet/habit)
    - user_profile: 用户资料
    """
    service = GoalRecommendationService()
    user_profile_dict = (
        request.user_profile.model_dump() if request.user_profile else {}
    )

    # 合并用户档案
    if not request.user_profile:
        # 如果没有提供，使用数据库中的用户资料
        user_profile_dict = {
            "height": current_user.height,
            "current_weight": current_user.current_weight,
            "age": current_user.age,
            "gender": current_user.gender,
            "activity_level": current_user.activity_level,
        }

    # 根据目标类型调用对应的推荐方法
    if request.goal_type == "weight":
        if not user_profile_dict.get("height") or not user_profile_dict.get(
            "current_weight"
        ):
            raise HTTPException(
                status_code=400, detail="计算体重目标需要身高和当前体重"
            )
        recommendation = service.calculate_weight_goal(
            height_cm=user_profile_dict["height"],
            current_weight_g=user_profile_dict["current_weight"],
        )

    elif request.goal_type == "exercise":
        if not user_profile_dict.get("activity_level"):
            raise HTTPException(status_code=400, detail="计算运动目标需要活动水平")
        recommendation = service.calculate_exercise_goal(
            activity_level=user_profile_dict["activity_level"],
            current_steps=user_profile_dict.get("current_steps"),
        )

    elif request.goal_type == "diet":
        required = ["weight", "height", "age", "gender", "activity_level"]
        missing = [f for f in required if not user_profile_dict.get(f)]
        if missing:
            raise HTTPException(
                status_code=400, detail=f"计算饮食目标需要: {', '.join(missing)}"
            )
        recommendation = service.calculate_diet_goal(
            weight_g=user_profile_dict["weight"],
            height_cm=user_profile_dict["height"],
            age=user_profile_dict["age"],
            gender=user_profile_dict["gender"],
            activity_level=user_profile_dict["activity_level"],
            diet_goal_type=user_profile_dict.get("diet_goal", "lose"),
        )

    elif request.goal_type == "habit":
        if not user_profile_dict.get("weight"):
            raise HTTPException(status_code=400, detail="计算习惯目标需要体重")
        recommendation = service.calculate_habit_goals(
            weight_g=user_profile_dict["weight"],
            current_water_ml=user_profile_dict.get("current_water_ml"),
            current_sleep_hours=user_profile_dict.get("current_sleep_hours"),
        )

    else:
        raise HTTPException(
            status_code=400,
            detail="无效的目标类型. 必须是: weight, exercise, diet, 或 habit",
        )

    # 生成预测
    prediction = None
    # TODO: 可以基于用户现有目标生成预测

    return {
        "goal_type": request.goal_type,
        "recommendation": recommendation,
        "prediction": prediction,
    }


@router.get("/recommendations/{goal_type}", response_model=GoalRecommendationResponse)
def get_recommendation_by_type(
    goal_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    根据目标类型获取推荐 (使用用户档案)
    """
    service = GoalRecommendationService()

    user_profile = {
        "height": current_user.height,
        "current_weight": current_user.current_weight,
        "age": current_user.age,
        "gender": current_user.gender,
        "activity_level": current_user.activity_level,
    }

    if goal_type == "weight":
        if not user_profile.get("height") or not user_profile.get("current_weight"):
            raise HTTPException(
                status_code=400, detail="计算体重目标需要身高和当前体重"
            )
        recommendation = service.calculate_weight_goal(
            height_cm=user_profile["height"],
            current_weight_g=user_profile["current_weight"],
        )

    elif goal_type == "exercise":
        if not user_profile.get("activity_level"):
            raise HTTPException(status_code=400, detail="计算运动目标需要活动水平")
        recommendation = service.calculate_exercise_goal(
            activity_level=user_profile["activity_level"],
        )

    elif goal_type == "diet":
        required = ["height", "current_weight", "age", "gender", "activity_level"]
        missing = [f for f in required if not user_profile.get(f)]
        if missing:
            raise HTTPException(
                status_code=400, detail=f"计算饮食目标需要: {', '.join(missing)}"
            )
        recommendation = service.calculate_diet_goal(
            weight_g=user_profile["current_weight"],
            height_cm=user_profile["height"],
            age=user_profile["age"],
            gender=user_profile["gender"],
            activity_level=user_profile["activity_level"],
        )

    elif goal_type == "habit":
        if not user_profile.get("current_weight"):
            raise HTTPException(status_code=400, detail="计算习惯目标需要体重")
        recommendation = service.calculate_habit_goals(
            weight_g=user_profile["current_weight"],
        )

    else:
        raise HTTPException(status_code=400, detail="无效的目标类型")

    return {
        "goal_type": goal_type,
        "recommendation": recommendation,
        "prediction": None,
    }


# ==================== 目标 CRUD 端点 ====================


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    创建新目标
    """
    # 创建目标记录
    goal = UserGoal(
        user_id=current_user.id,
        goal_type=goal_data.goal_type,
        current_value=goal_data.current_value,
        target_value=goal_data.target_value,
        unit=goal_data.unit,
        target_date=goal_data.target_date,
        status=GoalStatus.ACTIVE.value,
    )

    db.add(goal)
    db.flush()  # 获取 goal_id

    # 创建初始历史记录
    history = GoalHistory(
        goal_id=goal.goal_id,
        change_type="created",
        previous_state=None,
        new_state={
            "goal_type": goal_data.goal_type,
            "target_value": goal_data.target_value,
            "unit": goal_data.unit,
            "target_date": goal_data.target_date.isoformat()
            if goal_data.target_date
            else None,
        },
        reason="用户创建目标",
        ai_suggested=False,
    )
    db.add(history)

    db.commit()
    db.refresh(goal)

    return goal


@router.get("", response_model=List[GoalListResponse])
def list_goals(
    status_filter: Optional[str] = Query(None, alias="status"),
    goal_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取目标列表

    - status: 筛选状态 (active/paused/completed/cancelled)
    - goal_type: 筛选目标类型
    """
    query = db.query(UserGoal).filter(UserGoal.user_id == current_user.id)

    if status_filter:
        query = query.filter(UserGoal.status == status_filter)

    if goal_type:
        query = query.filter(UserGoal.goal_type == goal_type)

    goals = query.order_by(UserGoal.created_at.desc()).all()

    # 计算进度百分比
    result = []
    for goal in goals:
        goal_dict = {
            "goal_id": goal.goal_id,
            "goal_type": goal.goal_type,
            "current_value": goal.current_value,
            "target_value": goal.target_value,
            "unit": goal.unit,
            "status": goal.status,
            "predicted_date": goal.predicted_date,
            "progress_percentage": 0.0,
        }

        if goal.current_value is not None and goal.target_value:
            if goal.goal_type in ["weight", "diet"]:
                # 减重类型: 进度 = (current - target) / (start - target) * 100
                # 这里简化处理
                if goal.current_value <= goal.target_value:
                    goal_dict["progress_percentage"] = 100.0
                else:
                    goal_dict["progress_percentage"] = 0.0
            else:
                # 增类型: 进度 = current / target * 100
                progress = (goal.current_value / goal.target_value) * 100
                goal_dict["progress_percentage"] = min(100.0, progress)

        result.append(goal_dict)

    return result


@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取目标详情
    """
    goal = (
        db.query(UserGoal)
        .filter(UserGoal.goal_id == goal_id, UserGoal.user_id == current_user.id)
        .first()
    )

    if not goal:
        raise HTTPException(status_code=404, detail="目标不存在")

    return goal


@router.patch("/{goal_id}", response_model=GoalResponse)
def update_goal(
    goal_id: int,
    goal_data: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    更新目标
    """
    goal = (
        db.query(UserGoal)
        .filter(UserGoal.goal_id == goal_id, UserGoal.user_id == current_user.id)
        .first()
    )

    if not goal:
        raise HTTPException(status_code=404, detail="目标不存在")

    # 记录历史
    previous_state = {
        "target_value": goal.target_value,
        "target_date": goal.target_date.isoformat() if goal.target_date else None,
        "current_value": goal.current_value,
        "status": goal.status,
    }

    # 更新字段
    update_data = goal_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(goal, key, value)

    # 创建历史记录
    history = GoalHistory(
        goal_id=goal.goal_id,
        change_type="updated",
        previous_state=previous_state,
        new_state=update_data,
        reason="用户更新目标",
        ai_suggested=False,
    )
    db.add(history)

    db.commit()
    db.refresh(goal)

    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    删除目标
    """
    goal = (
        db.query(UserGoal)
        .filter(UserGoal.goal_id == goal_id, UserGoal.user_id == current_user.id)
        .first()
    )

    if not goal:
        raise HTTPException(status_code=404, detail="目标不存在")

    db.delete(goal)
    db.commit()

    return None


# ==================== 目标进度端点 ====================


@router.post("/{goal_id}/progress", response_model=GoalProgressResponse)
def record_progress(
    goal_id: int,
    progress_data: GoalProgressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    记录进度
    """
    goal = (
        db.query(UserGoal)
        .filter(UserGoal.goal_id == goal_id, UserGoal.user_id == current_user.id)
        .first()
    )

    if not goal:
        raise HTTPException(status_code=404, detail="目标不存在")

    if goal.status != GoalStatus.ACTIVE.value:
        raise HTTPException(status_code=400, detail="只能为活跃目标记录进度")

    # 计算连续达成
    last_progress = (
        db.query(GoalProgress)
        .filter(GoalProgress.goal_id == goal_id)
        .order_by(GoalProgress.recorded_date.desc())
        .first()
    )

    streak = 1
    if last_progress and last_progress.daily_target_met:
        streak = last_progress.streak_count + 1

    # 创建进度记录
    progress = GoalProgress(
        goal_id=goal_id,
        recorded_date=progress_data.recorded_date or datetime.now(),
        value=progress_data.value,
        daily_target_met=progress_data.daily_target_met,
        streak_count=streak,
    )

    # 更新目标当前值
    goal.current_value = progress_data.value

    # 检查是否达成目标
    if goal.goal_type in ["weight", "diet"]:
        # 减重类型
        if progress_data.value <= goal.target_value:
            goal.status = GoalStatus.COMPLETED.value
    else:
        # 增类型
        if progress_data.value >= goal.target_value:
            goal.status = GoalStatus.COMPLETED.value

    db.add(progress)
    db.commit()
    db.refresh(progress)

    return progress


@router.get("/{goal_id}/progress", response_model=List[GoalProgressResponse])
def get_goal_progress(
    goal_id: int,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取目标进度历史
    """
    from datetime import timedelta

    goal = (
        db.query(UserGoal)
        .filter(UserGoal.goal_id == goal_id, UserGoal.user_id == current_user.id)
        .first()
    )

    if not goal:
        raise HTTPException(status_code=404, detail="目标不存在")

    progress_list = (
        db.query(GoalProgress)
        .filter(
            GoalProgress.goal_id == goal_id,
            GoalProgress.recorded_date >= datetime.now() - timedelta(days=days),
        )
        .order_by(GoalProgress.recorded_date.asc())
        .all()
    )

    return progress_list


# ==================== 目标状态端点 ====================


@router.patch("/{goal_id}/status", response_model=GoalResponse)
def update_goal_status(
    goal_id: int,
    new_status: str = Query(..., description="状态: active/paused/cancelled/completed"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    更新目标状态 (暂停/取消/恢复/完成)
    """
    goal = (
        db.query(UserGoal)
        .filter(UserGoal.goal_id == goal_id, UserGoal.user_id == current_user.id)
        .first()
    )

    if not goal:
        raise HTTPException(status_code=404, detail="目标不存在")

    valid_statuses = ["active", "paused", "cancelled", "completed"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=400, detail=f"无效状态. 必须是: {', '.join(valid_statuses)}"
        )

    old_status = goal.status
    goal.status = new_status

    # 创建历史记录
    history = GoalHistory(
        goal_id=goal.goal_id,
        change_type=f"status_change_{new_status}",
        previous_state={"status": old_status},
        new_state={"status": new_status},
        reason=f"状态变更为 {new_status}",
        ai_suggested=False,
    )
    db.add(history)

    db.commit()
    db.refresh(goal)

    return goal


# ==================== 目标历史端点 ====================


@router.get("/{goal_id}/history", response_model=List)
def get_goal_history(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取目标变更历史
    """
    goal = (
        db.query(UserGoal)
        .filter(UserGoal.goal_id == goal_id, UserGoal.user_id == current_user.id)
        .first()
    )

    if not goal:
        raise HTTPException(status_code=404, detail="目标不存在")

    history = (
        db.query(GoalHistory)
        .filter(GoalHistory.goal_id == goal_id)
        .order_by(GoalHistory.created_at.desc())
        .all()
    )

    return history


# ==================== 反馈相关端点 ====================


@router.get("/feedback/check")
def check_goal_feedback(
    force: bool = Query(False, description="强制检查所有目标"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    手动检查目标反馈

    检查用户的目标进度，生成相应的反馈消息
    - force: 是否强制检查（即使正常也返回）
    """
    from app.services.goal_feedback import GoalFeedbackService

    service = GoalFeedbackService(db)
    feedback = service.check_and_send_feedback(current_user.id, force=force)

    if not feedback:
        return {
            "message": "一切正常！继续加油～",
            "feedback": [],
        }

    return {"feedback": feedback}


@router.get("/feedback/summary")
def get_feedback_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取反馈摘要

    返回用户所有目标的反馈摘要，包括需要关注的目标数量等
    """
    from app.services.goal_feedback import GoalFeedbackService

    service = GoalFeedbackService(db)
    summary = service.get_feedback_summary(current_user.id)

    # 添加总体消息
    if summary["needs_attention"] > 0:
        summary["overall_message"] = f"你有 {summary['needs_attention']} 个目标需要关注"
    elif summary["exceeding"] > 0:
        summary["overall_message"] = "太棒了！你所有目标都在超额完成！"
    else:
        summary["overall_message"] = "所有目标都在正常轨道上！继续保持！"

    return summary


@router.post("/feedback/{goal_id}/dismiss")
def dismiss_feedback(
    goal_id: int,
    action: str = Query(
        ..., description="操作: dismiss_forever/dismiss_today/remind_later"
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    处理反馈

    - dismiss_forever: 永久忽略该目标
    - dismiss_today: 今天忽略
    - remind_later: 稍后提醒
    """
    # 验证目标归属
    goal = (
        db.query(UserGoal)
        .filter(UserGoal.goal_id == goal_id, UserGoal.user_id == current_user.id)
        .first()
    )

    if not goal:
        raise HTTPException(status_code=404, detail="目标不存在")

    # TODO: 保存用户选择到数据库
    # 这里可以扩展为记录用户对反馈的处理方式

    messages = {
        "dismiss_forever": "好的，以后不会为这个目标发送提醒了",
        "dismiss_today": "收到，今天不会打扰你了",
        "remind_later": "好的，稍后会再提醒你",
    }

    return {"message": messages.get(action, "已记录你的选择～")}
