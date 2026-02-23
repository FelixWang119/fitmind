from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class NutritionAssessment(BaseModel):
    """营养评估"""

    calorie_needs: Dict[str, float] = Field(..., description="卡路里需求")
    macronutrient_needs: Dict[str, float] = Field(..., description="宏量营养素需求")
    hydration_needs: float = Field(..., description="饮水需求(毫升)")
    dietary_preferences: List[str] = Field(..., description="饮食偏好")
    diet_patterns: Dict[str, Any] = Field(..., description="饮食模式")
    supplement_needs: List[str] = Field(..., description="补充剂需求")
    priority_level: str = Field(..., description="优先级: 高/中/低")


class BehaviorAssessment(BaseModel):
    """行为评估"""

    habit_stats: Dict[str, Any] = Field(..., description="习惯统计")
    behavior_patterns: Dict[str, Any] = Field(..., description="行为模式")
    identified_barriers: List[str] = Field(..., description="识别障碍")
    motivation_level: str = Field(..., description="动机水平: 高/中/低/未知")
    self_efficacy: str = Field(..., description="自我效能感: 高/中/低/未知")
    priority_level: str = Field(..., description="优先级: 高/中/低")


class EmotionalAssessment(BaseModel):
    """情感评估"""

    emotional_insights: Dict[str, Any] = Field(..., description="情感洞察")
    stress_trend: List[Dict] = Field(..., description="压力趋势")
    emotional_needs: List[str] = Field(..., description="情感需求")
    priority_level: str = Field(..., description="优先级: 高/中/低")


class IntegratedAssessment(BaseModel):
    """综合评估"""

    cross_cutting_issues: List[str] = Field(..., description="交叉领域问题")
    overall_priority: str = Field(..., description="整体优先级: 高/中/低")
    priority_distribution: Dict[str, int] = Field(..., description="优先级分布")
    integrated_focus_areas: List[str] = Field(..., description="综合关注领域")


class UserNeedsAssessment(BaseModel):
    """用户需求评估"""

    nutrition_assessment: NutritionAssessment = Field(..., description="营养评估")
    behavior_assessment: BehaviorAssessment = Field(..., description="行为评估")
    emotional_assessment: EmotionalAssessment = Field(..., description="情感评估")
    integrated_assessment: IntegratedAssessment = Field(..., description="综合评估")
    recommended_role: str = Field(..., description="推荐角色")
    assessment_date: str = Field(..., description="评估日期")


class InterventionComponent(BaseModel):
    """干预组件"""

    type: str = Field(..., description="类型")
    focus: str = Field(..., description="关注领域")
    activities: List[str] = Field(..., description="活动")


class IntegratedIntervention(BaseModel):
    """综合干预计划"""

    primary_role: str = Field(..., description="主要角色")
    focus_areas: List[str] = Field(..., description="关注领域")
    duration_weeks: int = Field(..., description="持续时间(周)")
    weekly_sessions: Dict[str, int] = Field(..., description="每周会话次数")
    intervention_components: List[InterventionComponent] = Field(
        ..., description="干预组件"
    )


class ShortTermGoal(BaseModel):
    """短期目标"""

    area: str = Field(..., description="领域")
    goal: str = Field(..., description="目标")
    measure: str = Field(..., description="衡量标准")
    timeframe: str = Field(..., description="时间框架")


class IntegratedGuidance(BaseModel):
    """综合指导"""

    context: str = Field(..., description="上下文")
    assessment_summary: Dict[str, Any] = Field(..., description="评估摘要")
    immediate_actions: List[str] = Field(..., description="立即行动")
    short_term_goals: List[ShortTermGoal] = Field(..., description="短期目标")
    integrated_advice: str = Field(..., description="综合建议")
    follow_up_plan: Dict[str, Any] = Field(..., description="跟进计划")


class ProgressMetrics(BaseModel):
    """进展指标"""

    calorie_adherence: float = Field(..., description="卡路里依从性")
    weight_change: int = Field(..., description="体重变化(克)")
    record_count: int = Field(..., description="记录数量")
    hydration_progress: float = Field(..., description="饮水进展")


class BehaviorProgress(BaseModel):
    """行为进展"""

    completion_rate: float = Field(..., description="完成率")
    weekly_completion_rate: float = Field(..., description="每周完成率")
    current_streak: int = Field(..., description="当前连续天数")
    habit_count: int = Field(..., description="习惯数量")
    new_habits: int = Field(..., description="新习惯数量")


class IntegratedProgress(BaseModel):
    """综合进展"""

    overall_score: float = Field(..., description="整体评分")
    status: str = Field(..., description="状态")
    trend: str = Field(..., description="趋势")


class ProgressTracking(BaseModel):
    """进展跟踪"""

    nutrition_progress: ProgressMetrics = Field(..., description="营养进展")
    behavior_progress: BehaviorProgress = Field(..., description="行为进展")
    emotional_progress: Dict[str, Any] = Field(..., description="情感进展")
    integrated_progress: IntegratedProgress = Field(..., description="综合进展")
    overall_status: str = Field(..., description="整体状态")
    recommendations: List[str] = Field(..., description="建议")
    tracking_date: str = Field(..., description="跟踪日期")


class RoleSwitchRequest(BaseModel):
    """角色切换请求"""

    current_role: str = Field(..., description="当前角色")
    target_role: str = Field(..., description="目标角色")
    reason: Optional[str] = Field(None, description="切换原因")
    user_preferences: Optional[Dict[str, Any]] = Field(None, description="用户偏好")


class RoleTransition(BaseModel):
    """角色转换"""

    from_role: str = Field(..., description="原角色")
    to_role: str = Field(..., description="新角色")
    transition_reason: str = Field(..., description="转换原因")
    recommended_approach: str = Field(..., description="推荐方法")
    expected_outcomes: List[str] = Field(..., description="预期结果")
