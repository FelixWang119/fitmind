from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WeightStatistics(BaseModel):
    """体重统计"""

    mean_weight_kg: float = Field(..., description="平均体重(kg)")
    std_deviation_kg: float = Field(..., description="标准差(kg)")
    coefficient_of_variation: float = Field(..., description="变异系数(%)")
    median_weight_kg: float = Field(..., description="中位数体重(kg)")
    min_weight_kg: float = Field(..., description="最小体重(kg)")
    max_weight_kg: float = Field(..., description="最大体重(kg)")


class WeightTrend(BaseModel):
    """体重趋势"""

    trend: str = Field(..., description="趋势描述")
    slope_g_per_day: float = Field(..., description="每日变化斜率(g)")
    r_squared: float = Field(..., description="R²值")
    trend_reliability: str = Field(..., description="趋势可靠性")
    predicted_days_to_target: Optional[int] = Field(None, description="预计达标天数")


class VolatilityAnalysis(BaseModel):
    """波动性分析"""

    daily_change_avg_g: float = Field(..., description="平均每日变化(g)")
    volatility_index: float = Field(..., description="波动指数")
    stability_assessment: str = Field(..., description="稳定性评估")


class TargetProgress(BaseModel):
    """目标进度"""

    has_goal: bool = Field(..., description="是否有目标")
    target_weight_kg: Optional[float] = Field(None, description="目标体重(kg)")
    initial_weight_kg: Optional[float] = Field(None, description="初始体重(kg)")
    current_weight_kg: Optional[float] = Field(None, description="当前体重(kg)")
    progress_percent: Optional[float] = Field(None, description="进度百分比")
    remaining_kg: Optional[float] = Field(None, description="剩余体重(kg)")
    weeks_elapsed: Optional[float] = Field(None, description="已过周数")
    avg_weekly_loss_kg: Optional[float] = Field(None, description="平均每周减重(kg)")
    pace_assessment: Optional[str] = Field(None, description="速度评估")
    estimated_weeks_remaining: Optional[int] = Field(None, description="预计剩余周数")


class ClinicalSignificance(BaseModel):
    """临床意义"""

    clinical_significance: str = Field(..., description="临床意义")
    health_benefits: List[str] = Field(..., description="健康益处")
    recommended_next_steps: List[str] = Field(..., description="推荐下一步")


class WeightAnalysis(BaseModel):
    """体重分析"""

    data_available: bool = Field(..., description="数据是否可用")
    message: Optional[str] = Field(None, description="消息")
    record_count: Optional[int] = Field(None, description="记录数量")
    current_weight_kg: Optional[float] = Field(None, description="当前体重(kg)")
    initial_weight_kg: Optional[float] = Field(None, description="初始体重(kg)")
    weight_change_kg: Optional[float] = Field(None, description="体重变化(kg)")
    weight_change_percent: Optional[float] = Field(None, description="体重变化百分比")
    statistics: Optional[WeightStatistics] = Field(None, description="统计数据")
    trend_analysis: Optional[WeightTrend] = Field(None, description="趋势分析")
    volatility: Optional[VolatilityAnalysis] = Field(None, description="波动性")
    target_progress: Optional[TargetProgress] = Field(None, description="目标进度")
    clinical_significance: Optional[ClinicalSignificance] = Field(
        None, description="临床意义"
    )


class CalorieAnalysis(BaseModel):
    """卡路里分析"""

    avg_daily_calories: float = Field(..., description="平均每日卡路里")
    target_calories: float = Field(..., description="目标卡路里")
    adherence_percent: float = Field(..., description="依从性百分比")
    variance: float = Field(..., description="方差")
    consistency: str = Field(..., description="一致性")


class MacronutrientData(BaseModel):
    """宏量营养素数据"""

    avg_daily_g: float = Field(..., description="平均每日(g)")
    target_g: float = Field(..., description="目标(g)")
    adherence_percent: float = Field(..., description="依从性百分比")
    adequacy: str = Field(..., description="充足性")


class NutritionScore(BaseModel):
    """营养评分"""

    overall_score: float = Field(..., description="总分")
    calorie_component: float = Field(..., description="卡路里成分")
    macro_component: float = Field(..., description="宏量营养素成分")
    consistency_component: float = Field(..., description="一致性成分")
    grade: str = Field(..., description="等级")


class DietaryPatterns(BaseModel):
    """饮食模式"""

    pattern: str = Field(..., description="模式")
    high_calorie_days: int = Field(..., description="高热量天数")
    low_calorie_days: int = Field(..., description="低热量天数")
    recommendation: str = Field(..., description="建议")
    confidence: float = Field(..., description="置信度")


class NutritionAnalysis(BaseModel):
    """营养分析"""

    data_available: bool = Field(..., description="数据是否可用")
    message: Optional[str] = Field(None, description="消息")
    record_count: Optional[int] = Field(None, description="记录数量")
    calorie_analysis: Optional[CalorieAnalysis] = Field(None, description="卡路里分析")
    macronutrient_analysis: Optional[Dict[str, MacronutrientData]] = Field(
        None, description="宏量营养素分析"
    )
    nutrition_score: Optional[NutritionScore] = Field(None, description="营养评分")
    dietary_patterns: Optional[DietaryPatterns] = Field(None, description="饮食模式")


class HabitStatistics(BaseModel):
    """习惯统计"""

    total_active_habits: int = Field(..., description="活跃习惯总数")
    overall_completion_rate: float = Field(..., description="总体完成率")
    current_longest_streak: int = Field(..., description="当前最长连续")
    category_distribution: Dict[str, int] = Field(..., description="类别分布")


class ConsistencyMetrics(BaseModel):
    """一致性指标"""

    overall_consistency: float = Field(..., description="总体一致性")
    individual_habits: int = Field(..., description="个体习惯数")
    consistency_trend: str = Field(..., description="一致性趋势")


class BehaviorChangeStage(BaseModel):
    """行为改变阶段"""

    current_stage: str = Field(..., description="当前阶段")
    stage_description: str = Field(..., description="阶段描述")
    stage_duration_estimate: str = Field(..., description="阶段持续估计")
    interventions_for_stage: List[str] = Field(..., description="阶段干预")


class BehavioralMomentum(BaseModel):
    """行为动量"""

    momentum_score: float = Field(..., description="动量分数")
    trend: str = Field(..., description="趋势")
    recent_week_avg: float = Field(..., description="最近一周平均")
    previous_week_avg: float = Field(..., description="前一周平均")
    recommendation: str = Field(..., description="建议")


class BehaviorAnalysis(BaseModel):
    """行为分析"""

    habit_statistics: HabitStatistics = Field(..., description="习惯统计")
    consistency_metrics: ConsistencyMetrics = Field(..., description="一致性指标")
    behavior_change_stage: BehaviorChangeStage = Field(..., description="行为改变阶段")
    behavioral_momentum: BehavioralMomentum = Field(..., description="行为动量")


class EmotionalWellness(BaseModel):
    """情感健康"""

    dominant_emotion: str = Field(..., description="主导情感")
    emotional_variety: int = Field(..., description="情感多样性")
    positive_emotion_ratio: float = Field(..., description="积极情感比例")


class StressAnalysis(BaseModel):
    """压力分析"""

    average_stress_level: float = Field(..., description="平均压力水平")
    stress_trend: List[Dict] = Field(..., description="压力趋势")
    stress_management_effectiveness: float = Field(..., description="压力管理有效性")


class ResilienceMetrics(BaseModel):
    """韧性指标"""

    resilience_score: int = Field(..., description="韧性分数")
    gratitude_practice_frequency: int = Field(..., description="感恩练习频率")
    mindfulness_practice_frequency: int = Field(..., description="正念练习频率")
    resilience_level: str = Field(..., description="韧性水平")


class MentalHealthStatus(BaseModel):
    """心理健康状态"""

    overall_status: str = Field(..., description="整体状态")
    risk_level: str = Field(..., description="风险等级")
    recommendations: List[str] = Field(..., description="建议")
    warning_signs: List[str] = Field(..., description="警告信号")


class PsychologicalAnalysis(BaseModel):
    """心理分析"""

    emotional_wellness: EmotionalWellness = Field(..., description="情感健康")
    stress_analysis: StressAnalysis = Field(..., description="压力分析")
    resilience_metrics: ResilienceMetrics = Field(..., description="韧性指标")
    mental_health_status: MentalHealthStatus = Field(..., description="心理健康状态")


class HealthScoreComponents(BaseModel):
    """健康评分组件"""

    weight: float = Field(..., description="体重评分")
    nutrition: float = Field(..., description="营养评分")
    behavior: float = Field(..., description="行为评分")
    psychological: float = Field(..., description="心理评分")


class ComprehensiveHealthScore(BaseModel):
    """综合健康评分"""

    total_score: float = Field(..., description="总分")
    max_score: int = Field(..., description="最高分")
    components: HealthScoreComponents = Field(..., description="组件")
    grade: str = Field(..., description="等级")
    percentile: int = Field(..., description="百分位")
    interpretation: str = Field(..., description="解读")


class EvidenceBasedRecommendation(BaseModel):
    """循证建议"""

    area: str = Field(..., description="领域")
    recommendation: str = Field(..., description="建议")
    evidence: str = Field(..., description="证据")
    priority: str = Field(..., description="优先级")


class UserProfile(BaseModel):
    """用户档案"""

    bmi: float = Field(..., description="BMI")
    bmi_category: str = Field(..., description="BMI分类")
    metabolic_age: Dict[str, Any] = Field(..., description="代谢年龄")
    health_risk_level: Dict[str, Any] = Field(..., description="健康风险等级")


class DataQualityAssessment(BaseModel):
    """数据质量评估"""

    overall_quality: float = Field(..., description="总体质量")
    weight_data_coverage: float = Field(..., description="体重数据覆盖")
    nutrition_data_coverage: float = Field(..., description="营养数据覆盖")
    assessment: str = Field(..., description="评估")
    recommendations: List[str] = Field(..., description="建议")


class ScientificReport(BaseModel):
    """科学报告"""

    report_type: str = Field(..., description="报告类型")
    period_days: int = Field(..., description="周期天数")
    generated_at: str = Field(..., description="生成时间")
    user_profile: UserProfile = Field(..., description="用户档案")
    weight_analysis: WeightAnalysis = Field(..., description="体重分析")
    nutrition_analysis: NutritionAnalysis = Field(..., description="营养分析")
    behavior_analysis: BehaviorAnalysis = Field(..., description="行为分析")
    psychological_analysis: PsychologicalAnalysis = Field(..., description="心理分析")
    comprehensive_health_score: ComprehensiveHealthScore = Field(
        ..., description="综合健康评分"
    )
    evidence_based_recommendations: List[EvidenceBasedRecommendation] = Field(
        ..., description="循证建议"
    )
    data_quality_assessment: DataQualityAssessment = Field(..., description="数据质量评估")


class BMICalculation(BaseModel):
    """BMI计算"""

    bmi: float = Field(..., description="BMI值")
    category: str = Field(..., description="分类")
    healthy_range: str = Field(..., description="健康范围")
    recommendation: str = Field(..., description="建议")


class MetabolicMetrics(BaseModel):
    """代谢指标"""

    bmr: float = Field(..., description="基础代谢率")
    tdee: float = Field(..., description="总能量消耗")
    metabolic_age: int = Field(..., description="代谢年龄")
    body_composition_estimate: Dict[str, float] = Field(..., description="身体成分估算")


class HealthRiskAssessment(BaseModel):
    """健康风险评估"""

    overall_risk: str = Field(..., description="整体风险")
    cardiovascular_risk: str = Field(..., description="心血管风险")
    metabolic_risk: str = Field(..., description="代谢风险")
    lifestyle_risk_factors: List[str] = Field(..., description="生活方式风险因素")
    protective_factors: List[str] = Field(..., description="保护因素")
    recommendations: List[str] = Field(..., description="建议")


class ScientificInsight(BaseModel):
    """科学洞察"""

    insight_type: str = Field(..., description="洞察类型")
    finding: str = Field(..., description="发现")
    statistical_significance: Optional[str] = Field(None, description="统计显著性")
    clinical_relevance: str = Field(..., description="临床相关性")
    actionable_recommendation: str = Field(..., description="可行建议")


class PersonaMessage(BaseModel):
    """人设消息"""

    message: str = Field(..., description="消息内容")
    tone: str = Field(..., description="语气")
    scientific_citations: Optional[List[str]] = Field(None, description="科学引用")
    confidence_level: str = Field(..., description="置信水平")
