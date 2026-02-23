from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, date


class HealthMetricDataPoint(BaseModel):
    """健康指标数据点"""

    date: str = Field(..., description="日期")
    value: float = Field(..., description="值")
    unit: str = Field(..., description="单位")
    category: str = Field(..., description="分类")

    class Config:
        from_attributes = True


class CorrelationAnalysis(BaseModel):
    """相关性分析"""

    metric1: str = Field(..., description="指标1")
    metric2: str = Field(..., description="指标2")
    correlation_coefficient: float = Field(..., description="相关系数", ge=-1, le=1)
    p_value: float = Field(..., description="P值", ge=0, le=1)
    significance: str = Field(
        ..., description="显著性", examples=["high", "medium", "low", "none"]
    )
    interpretation: str = Field(..., description="解释")

    class Config:
        from_attributes = True


class TrendAnalysis(BaseModel):
    """趋势分析"""

    metric: str = Field(..., description="指标")
    period: str = Field(
        ..., description="周期", examples=["daily", "weekly", "monthly"]
    )
    trend_direction: str = Field(
        ..., description="趋势方向", examples=["increasing", "decreasing", "stable"]
    )
    trend_strength: float = Field(..., description="趋势强度", ge=0, le=1)
    confidence_interval: List[float] = Field(..., description="置信区间")
    prediction: Dict[str, Any] = Field(..., description="预测")

    class Config:
        from_attributes = True


class ScientificHealthDashboardResponse(BaseModel):
    """科学健康仪表板响应"""

    user_id: int = Field(..., description="用户ID")
    dashboard_timestamp: str = Field(..., description="仪表板时间戳")
    time_period: Dict[str, str] = Field(..., description="时间周期")
    health_metrics: Dict[str, List[HealthMetricDataPoint]] = Field(
        ..., description="健康指标"
    )
    correlation_analyses: List[CorrelationAnalysis] = Field(
        ..., description="相关性分析"
    )
    trend_analyses: List[TrendAnalysis] = Field(..., description="趋势分析")
    key_insights: List[str] = Field(..., description="关键洞察")
    recommendations: List[str] = Field(..., description="建议")
    data_quality_score: float = Field(..., description="数据质量评分", ge=0, le=100)

    class Config:
        from_attributes = True


class VisualizationData(BaseModel):
    """可视化数据"""

    chart_type: str = Field(..., description="图表类型")
    title: str = Field(..., description="标题")
    x_axis_label: str = Field(..., description="X轴标签")
    y_axis_label: str = Field(..., description="Y轴标签")
    data_points: List[Dict[str, Any]] = Field(..., description="数据点")
    options: Dict[str, Any] = Field(default={}, description="选项")

    class Config:
        from_attributes = True


class StatisticalSummary(BaseModel):
    """统计摘要"""

    metric: str = Field(..., description="指标")
    mean: float = Field(..., description="均值")
    median: float = Field(..., description="中位数")
    std_dev: float = Field(..., description="标准差")
    min: float = Field(..., description="最小值")
    max: float = Field(..., description="最大值")
    percentile_25: float = Field(..., description="25百分位")
    percentile_75: float = Field(..., description="75百分位")

    class Config:
        from_attributes = True


class PatternRecognition(BaseModel):
    """模式识别"""

    pattern_type: str = Field(..., description="模式类型")
    description: str = Field(..., description="描述")
    confidence: float = Field(..., description="置信度", ge=0, le=1)
    implications: List[str] = Field(..., description="影响")
    recommendations: List[str] = Field(..., description="建议")

    class Config:
        from_attributes = True


class CorrelationMatrixData(BaseModel):
    """相关性矩阵数据"""

    metrics: List[str] = Field(..., description="指标列表")
    correlation_matrix: List[List[float]] = Field(..., description="相关性矩阵")
    significant_correlations: List[Dict[str, Any]] = Field(
        ..., description="显著相关性"
    )
    heatmap_data: Dict[str, Any] = Field(..., description="热力图数据")

    class Config:
        from_attributes = True


class TimeSeriesAnalysisData(BaseModel):
    """时间序列分析数据"""

    metric: str = Field(..., description="指标")
    timestamps: List[str] = Field(..., description="时间戳")
    values: List[float] = Field(..., description="值")
    trend_line: List[float] = Field(..., description="趋势线")
    seasonal_pattern: Dict[str, Any] = Field(..., description="季节性模式")
    forecast: Dict[str, Any] = Field(..., description="预测")

    class Config:
        from_attributes = True


class ClusteringAnalysisData(BaseModel):
    """聚类分析数据"""

    cluster_labels: List[int] = Field(..., description="聚类标签")
    cluster_centers: List[List[float]] = Field(..., description="聚类中心")
    feature_importance: Dict[str, float] = Field(..., description="特征重要性")
    silhouette_score: float = Field(..., description="轮廓系数", ge=-1, le=1)
    cluster_profiles: List[Dict[str, Any]] = Field(..., description="聚类画像")

    class Config:
        from_attributes = True


class DistributionAnalysisData(BaseModel):
    """分布分析数据"""

    metric: str = Field(..., description="指标")
    values: List[float] = Field(..., description="值")
    distribution_type: str = Field(..., description="分布类型")
    parameters: Dict[str, float] = Field(..., description="参数")
    goodness_of_fit: float = Field(..., description="拟合优度", ge=0, le=1)
    histogram_data: Dict[str, Any] = Field(..., description="直方图数据")

    class Config:
        from_attributes = True
