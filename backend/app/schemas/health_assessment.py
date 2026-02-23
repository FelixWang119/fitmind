from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, date


class HealthAssessmentRequest(BaseModel):
    """健康评估请求"""

    start_date: date = Field(..., description="评估开始日期")
    end_date: Optional[date] = Field(None, description="评估结束日期")
    include_trends: bool = Field(True, description="是否包含趋势分析")
    include_risks: bool = Field(True, description="是否包含风险评估")
    include_recommendations: bool = Field(True, description="是否包含个性化建议")


class HealthDimensionAssessment(BaseModel):
    """健康维度评估"""

    score: float = Field(..., description="得分", ge=0, le=100)
    max_score: float = Field(..., description="最高分")
    status: str = Field(
        ..., description="状态", examples=["excellent", "good", "fair", "poor"]
    )
    metrics: Dict[str, Any] = Field(default={}, description="指标数据")
    interpretation: Optional[str] = Field(None, description="解释说明")

    class Config:
        from_attributes = True


class HealthTrendAnalysis(BaseModel):
    """健康趋势分析"""

    period: str = Field(
        ..., description="分析周期", examples=["week", "month", "quarter"]
    )
    overall_trend: str = Field(
        ..., description="总体趋势", examples=["improving", "stable", "declining"]
    )
    dimension_trends: Dict[str, str] = Field(..., description="各维度趋势")
    confidence_score: float = Field(..., description="置信度", ge=0, le=1)
    key_insights: List[str] = Field(..., description="关键洞察")

    class Config:
        from_attributes = True


class HealthRiskAssessment(BaseModel):
    """健康风险评估"""

    risk_level: str = Field(
        ..., description="风险等级", examples=["low", "medium", "high"]
    )
    risk_factors: List[str] = Field(..., description="风险因素")
    mitigation_strategies: List[str] = Field(..., description="缓解策略")
    monitoring_recommendations: List[str] = Field(..., description="监测建议")

    class Config:
        from_attributes = True


class HealthGoalProgress(BaseModel):
    """健康目标进度"""

    goal_type: str = Field(..., description="目标类型")
    current_value: float = Field(..., description="当前值")
    target_value: float = Field(..., description="目标值")
    progress_percentage: float = Field(..., description="进度百分比", ge=0, le=100)
    estimated_completion: Optional[str] = Field(None, description="预计完成时间")
    confidence_level: float = Field(..., description="置信度", ge=0, le=1)

    class Config:
        from_attributes = True


class ComprehensiveHealthScore(BaseModel):
    """综合健康评分"""

    score: float = Field(..., description="得分", ge=0, le=100)
    max_score: float = Field(..., description="最高分")
    category: str = Field(
        ...,
        description="分类",
        examples=["excellent", "good", "normal", "needs_improvement", "concerning"],
    )
    interpretation: str = Field(..., description="解释说明")

    class Config:
        from_attributes = True


class HealthRecommendation(BaseModel):
    """健康建议"""

    category: str = Field(..., description="分类")
    title: str = Field(..., description="标题")
    content: str = Field(..., description="内容")
    priority: str = Field(..., description="优先级", examples=["high", "medium", "low"])
    action_needed: bool = Field(..., description="是否需要行动")

    class Config:
        from_attributes = True


class WellnessTrendAnalysis(BaseModel):
    """健康趋势分析"""

    period_days: int = Field(..., description="分析周期天数")
    trends_identified: List[str] = Field(..., description="识别出的趋势")
    patterns: List[str] = Field(..., description="模式识别")
    predictive_insights: List[str] = Field(..., description="预测性洞察")

    class Config:
        from_attributes = True


class RiskFactorAssessment(BaseModel):
    """风险因素评估"""

    type: str = Field(..., description="风险类型")
    severity: str = Field(
        ..., description="严重程度", examples=["low", "medium", "high"]
    )
    description: str = Field(..., description="描述")
    timeframe: str = Field(
        ...,
        description="时间范围",
        examples=["short_term", "medium_term", "long_term", "ongoing"],
    )

    class Config:
        from_attributes = True


class HealthAssessmentResponse(BaseModel):
    """健康评估响应"""

    user_id: int = Field(..., description="用户ID")
    assessment_period_start: str = Field(..., description="评估周期开始")
    assessment_period_end: str = Field(..., description="评估周期结束")
    timestamp: str = Field(..., description="评估时间戳")
    overall_health_score: ComprehensiveHealthScore = Field(
        ..., description="总体健康评分"
    )
    health_dimensions: Dict[str, HealthDimensionAssessment] = Field(
        ..., description="健康维度评估"
    )
    wellness_trends: WellnessTrendAnalysis = Field(..., description="健康趋势分析")
    risk_assessment: List[RiskFactorAssessment] = Field(..., description="风险评估")
    personalized_recommendations: List[HealthRecommendation] = Field(
        ..., description="个性化建议"
    )
    data_quality_score: float = Field(..., description="数据质量评分", ge=0, le=100)

    class Config:
        from_attributes = True


# =====================================================
# 新增：健康评估记录相关Schema (Story 6.1)
# =====================================================


class NutritionDetail(BaseModel):
    """营养维度详情"""

    calorie_balance: float = Field(..., description="热量均衡度得分")
    macro_balance: float = Field(..., description="宏量营养素平衡得分")
    diet_regularity: float = Field(..., description="饮食规律性得分")
    nutrition_diversity: float = Field(..., description="营养多样性得分")
    healthy_habits: float = Field(..., description="健康饮食习惯得分")

    # 详细指标
    avg_daily_calories: float = Field(..., description="平均每日热量")
    target_calories: Optional[float] = Field(None, description="目标热量")
    protein_ratio: float = Field(..., description="蛋白质比例")
    carbs_ratio: float = Field(..., description="碳水化合物比例")
    fat_ratio: float = Field(..., description="脂肪比例")
    meal_regularity_score: float = Field(..., description="用餐规律性得分")

    class Config:
        from_attributes = True


class BehaviorDetail(BaseModel):
    """行为维度详情"""

    habit_completion_rate: float = Field(..., description="习惯完成率得分")
    exercise_frequency: float = Field(..., description="运动频率得分")
    sleep_quality: float = Field(..., description="睡眠质量得分")
    routine_regularity: float = Field(..., description="作息规律性得分")

    # 详细指标
    total_active_habits: int = Field(..., description="活跃习惯数")
    completed_habits: int = Field(..., description="完成的习惯数")
    avg_daily_exercise_minutes: float = Field(..., description="平均每日运动分钟数")
    weekly_exercise_days: int = Field(..., description="每周运动天数")
    avg_daily_steps: float = Field(..., description="平均每日步数")
    avg_sleep_hours: float = Field(..., description="平均睡眠时长")
    sleep_quality_score: float = Field(..., description="睡眠质量评分")

    class Config:
        from_attributes = True


class EmotionDetail(BaseModel):
    """情感维度详情"""

    emotional_stability: float = Field(..., description="情绪稳定性得分")
    positive_emotion_ratio: float = Field(..., description="积极情绪占比得分")
    stress_level: float = Field(..., description="压力水平得分")
    psychological_resilience: float = Field(..., description="心理韧性得分")

    # 详细指标
    emotional_check_ins: int = Field(..., description="情绪记录次数")
    primary_emotion: str = Field(..., description="主要情绪")
    positive_ratio: float = Field(..., description="积极情绪比例")
    emotional_variety: int = Field(..., description="情绪多样性")
    stress_indicators: List[str] = Field(default=[], description="压力指标")

    class Config:
        from_attributes = True


class DataCompleteness(BaseModel):
    """数据完整性"""

    food_logs_complete: bool = Field(..., description="饮食记录是否完整")
    food_logs_days: int = Field(..., description="饮食记录天数")
    habit_logs_complete: bool = Field(..., description="习惯日志是否完整")
    habit_logs_days: int = Field(..., description="习惯日志天数")
    sleep_logs_complete: bool = Field(..., description="睡眠记录是否完整")
    sleep_logs_days: int = Field(..., description="睡眠记录天数")
    overall_completeness: float = Field(..., description="整体完整性百分比")

    class Config:
        from_attributes = True


class AssessmentSuggestion(BaseModel):
    """评估建议"""

    category: str = Field(..., description="建议类别")
    content: str = Field(..., description="建议内容")
    priority: str = Field(..., description="优先级", examples=["high", "medium", "low"])

    class Config:
        from_attributes = True


class HealthAssessmentRecord(BaseModel):
    """健康评估记录（数据库存储格式）"""

    id: int = Field(..., description="评估ID")
    user_id: int = Field(..., description="用户ID")
    assessment_date: str = Field(..., description="评估日期")

    # 综合评分
    overall_score: int = Field(..., description="综合评分", ge=0, le=100)
    overall_grade: str = Field(..., description="综合等级")

    # 营养维度
    nutrition_score: int = Field(..., description="营养评分", ge=0, le=100)
    nutrition_details: NutritionDetail = Field(..., description="营养详情")
    nutrition_suggestions: List[AssessmentSuggestion] = Field(
        default=[], description="营养建议"
    )

    # 行为维度
    behavior_score: int = Field(..., description="行为评分", ge=0, le=100)
    behavior_details: BehaviorDetail = Field(..., description="行为详情")
    behavior_suggestions: List[AssessmentSuggestion] = Field(
        default=[], description="行为建议"
    )

    # 情感维度
    emotion_score: int = Field(..., description="情感评分", ge=0, le=100)
    emotion_details: EmotionDetail = Field(..., description="情感详情")
    emotion_suggestions: List[AssessmentSuggestion] = Field(
        default=[], description="情感建议"
    )

    # 综合建议
    overall_suggestions: List[AssessmentSuggestion] = Field(
        default=[], description="综合建议"
    )

    # 数据完整性
    data_completeness: DataCompleteness = Field(..., description="数据完整性")

    # 评估周期
    assessment_period_start: Optional[str] = Field(None, description="评估周期开始")
    assessment_period_end: Optional[str] = Field(None, description="评估周期结束")
    created_at: str = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class HealthAssessmentCreateRequest(BaseModel):
    """创建健康评估请求"""

    start_date: Optional[date] = Field(None, description="评估开始日期（默认7天前）")
    end_date: Optional[date] = Field(None, description="评估结束日期（默认今天）")

    class Config:
        from_attributes = True


class HealthAssessmentCreateResponse(BaseModel):
    """创建健康评估响应"""

    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    assessment: Optional[HealthAssessmentRecord] = Field(None, description="评估记录")

    class Config:
        from_attributes = True


class HealthAssessmentHistoryItem(BaseModel):
    """健康评估历史项（简化版）"""

    id: int = Field(..., description="评估ID")
    assessment_date: str = Field(..., description="评估日期")
    overall_score: int = Field(..., description="综合评分", ge=0, le=100)
    overall_grade: str = Field(..., description="综合等级")
    nutrition_score: int = Field(..., description="营养评分")
    behavior_score: int = Field(..., description="行为评分")
    emotion_score: int = Field(..., description="情感评分")

    class Config:
        from_attributes = True


class HealthAssessmentHistoryResponse(BaseModel):
    """健康评估历史响应"""

    assessments: List[HealthAssessmentHistoryItem] = Field(
        ..., description="评估历史列表"
    )
    total_count: int = Field(..., description="总记录数")

    class Config:
        from_attributes = True


class HealthAssessmentComparison(BaseModel):
    """健康评估对比（与上次评估）"""

    current: HealthAssessmentRecord = Field(..., description="当前评估")
    previous: Optional[HealthAssessmentRecord] = Field(None, description="上次评估")

    # 变化指标
    overall_change: Optional[int] = Field(None, description="综合评分变化")
    overall_change_percent: Optional[float] = Field(
        None, description="综合评分变化百分比"
    )

    nutrition_change: Optional[int] = Field(None, description="营养评分变化")
    behavior_change: Optional[int] = Field(None, description="行为评分变化")
    emotion_change: Optional[int] = Field(None, description="情感评分变化")

    # 趋势标识
    trends: Dict[str, str] = Field(
        ...,
        description="各维度趋势",
        examples=[
            {"nutrition": "improving", "behavior": "stable", "emotion": "declining"}
        ],
    )

    class Config:
        from_attributes = True
