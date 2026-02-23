from datetime import date, datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field
from typing import Union


class HealthTrendData(BaseModel):
    """健康趋势数据模型"""

    weight_change_kg: Optional[float] = Field(None, description="体重变化(kg)")
    starting_weight_kg: Optional[float] = Field(None, description="初始体重(kg)")
    current_weight_kg: Optional[float] = Field(None, description="当前体重(kg)")
    average_weight_kg: Optional[float] = Field(None, description="平均体重(kg)")
    total_calories_consumed: Optional[float] = Field(
        None, description="总卡路里摄入"
    )  # Was int, changed to float for better precision
    average_daily_calories: Optional[float] = Field(
        None, description="平均每日卡路里摄入"
    )  # Was int
    total_exercise_minutes: Optional[int] = Field(None, description="总运动分钟数")
    average_daily_exercise_minutes: Optional[float] = Field(
        None, description="平均每日运动分钟数"
    )  # Was int
    total_steps: Optional[int] = Field(None, description="总步数")
    average_daily_steps: Optional[float] = Field(
        None, description="平均每日步数"
    )  # Was int
    active_days: Optional[int] = Field(None, description="活跃记录天数")


class AchievementInfo(BaseModel):
    """成就信息"""

    title: str = Field(..., description="成就标题")
    description: str = Field(..., description="成就描述")
    achieved: bool = Field(..., description="是否达成")
    category: str = Field(..., description="成就类别")


class DetailedHealthReport(BaseModel):
    """详细健康报告"""

    period_start: str = Field(..., description="报告开始日期")
    period_end: str = Field(..., description="报告结束日期")
    summary: HealthTrendData = Field(..., description="关键指标概要")
    trends: Dict[str, Dict] = Field(..., description="趋势分析")
    achievements: List[AchievementInfo] = Field(..., description="成就列表")
    recommendations: List[str] = Field(..., description="健康建议")
    detailed_insights: Dict[str, Dict] = Field(..., description="详细洞察")


class HealthReportRequest(BaseModel):
    """健康报告请求"""

    start_date: date = Field(..., description="报告开始日期")
    end_date: Optional[date] = Field(None, description="报告结束日期")
    include_nutrition: bool = Field(True, description="是否包含营养数据")
    include_exercise: bool = Field(True, description="是否包含运动数据")
    include_weight: bool = Field(True, description="是否包含体重数据")
    report_format: str = Field("detailed", description="报告格式: detailed, summary")


class HealthReportResponse(BaseModel):
    """健康报告响应"""

    status: str = Field(..., description="状态：success/error")
    message: str = Field(..., description="响应消息")
    report: DetailedHealthReport = Field(..., description="健康报告数据")
    generated_at: str = Field(..., description="报告生成时间")


class WeeklyHealthTrends(BaseModel):
    """周度健康趋势"""

    week_number: int = Field(..., description="周数")
    year: int = Field(..., description="年份")
    stats: Dict[str, float] = Field(..., description="统计")
    weight_trend_direction: Optional[str] = Field(None, description="体重趋势方向")
    nutrition_consistency_score: Optional[float] = Field(
        None, description="营养一致性评分"
    )
    exercise_frequency: Optional[float] = Field(None, description="运动频率")


class PredictionResult(BaseModel):
    """预测结果"""

    predicted_value: float = Field(..., description="预测值")
    confidence_interval: List[float] = Field(..., description="置信区间")
    prediction_model: str = Field(..., description="预测模型类型")
    model_accuracy: float = Field(..., description="模型准确度")
    trend_direction: str = Field(..., description="趋势方向")


class AnomalyDetectionResult(BaseModel):
    """异常检测结果"""

    is_anomaly: bool = Field(..., description="是否为异常值")
    anomaly_type: str = Field(..., description="异常类型")
    deviation_amount: float = Field(..., description="偏差幅度")
    severity_level: str = Field(..., description="严重程度")
    anomaly_timestamp: datetime = Field(..., description="异常发生时间")
    description: str = Field(..., description="异常描述")


class AdvancedHealthInsights(BaseModel):
    """高级健康洞察"""

    analysis_period: str = Field(..., description="分析周期")
    key_trends: List[str] = Field(..., description="关键趋势")
    potential_risks: List[str] = Field(..., description="潜在风险")
    improvement_areas: List[str] = Field(..., description="改进领域")
    consistency_scores: Dict[str, float] = Field(..., description="各项数据一致性评分")
    predictive_insights: List[PredictionResult] = Field(..., description="预测洞察")
    anomaly_indicators: List[AnomalyDetectionResult] = Field(
        ..., description="异常指标"
    )
