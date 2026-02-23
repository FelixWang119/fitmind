from datetime import datetime, timedelta
from typing import List, Dict, Optional
import structlog
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, extract

# Scientific visualization libraries
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import seaborn as sns
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User as UserModel
from app.models.health_record import HealthRecord
from app.models.habit import Habit, HabitCompletion
from app.models.nutrition import Meal
from app.models.emotional_support import EmotionalSupport
from app.schemas.scientific_visualization import (
    ScientificHealthDashboardResponse,
    CorrelationMatrixData,
    TimeSeriesAnalysisData,
    ClusteringAnalysisData,
    DistributionAnalysisData,
)

logger = structlog.get_logger()

router = APIRouter()


@router.get("/scientific-dashboard", response_model=ScientificHealthDashboardResponse)
async def get_scientific_health_dashboard(
    days_back: int = Query(90, ge=7, le=365, description="回溯天数 (7-365天)"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取科学健康数据可视化仪表板"""
    logger.info(
        "Generating scientific health dashboard",
        user_id=current_user.id,
        days_back=days_back,
    )

    # Calculate date range
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days_back)

    # Get comprehensive health data
    health_records = (
        db.query(HealthRecord)
        .filter(
            HealthRecord.user_id == current_user.id,
            HealthRecord.record_date >= start_date,
            HealthRecord.record_date <= end_date,
        )
        .order_by(HealthRecord.record_date)
        .all()
    )

    # Get habit completion data
    habit_completions = (
        db.query(HabitCompletion)
        .join(Habit, HabitCompletion.habit_id == Habit.id)
        .filter(
            Habit.user_id == current_user.id,
            HabitCompletion.completion_date >= start_date,
            HabitCompletion.completion_date <= end_date,
        )
        .order_by(HabitCompletion.completion_date)
        .all()
    )

    # Get nutrition data
    meals = (
        db.query(Meal)
        .filter(
            Meal.user_id == current_user.id,
            func.date(Meal.meal_datetime) >= start_date,
            func.date(Meal.meal_datetime) <= end_date,
        )
        .order_by(Meal.meal_datetime)
        .all()
    )

    # Get emotional check-in data
    from app.models.emotional_support import EmotionalSupport as EmoCheckIn

    emotional_records = (
        db.query(EmoCheckIn)
        .filter(
            EmoCheckIn.user_id == current_user.id,
            EmoCheckIn.created_at >= start_date,
            EmoCheckIn.created_at <= end_date,
        )
        .order_by(EmoCheckIn.created_at)
        .all()
    )

    # Extract and organize data for analysis
    weight_data = [
        (r.record_date, r.weight / 1000.0 if r.weight else 0)
        for r in health_records
        if r.weight
    ]
    steps_data = [
        (r.record_date, r.steps_count if r.steps_count else 0)
        for r in health_records
        if r.steps_count
    ]
    emotional_data = [
        (e.created_at.date(), e.intensity_level if e.intensity_level else 0)
        for e in emotional_records
        if e.intensity_level
    ]

    if not weight_data and not steps_data and not emotional_data:
        return {
            "message": "您在该时间范围内没有足够的健康数据进行科学分析",
            "status": "insufficient_data",
            "data_available": {},
        }

    # 1. Correlation Analysis
    correlation_matrix = {}
    if len(weight_data) > 2 and len(steps_data) > 2:
        # Align weight and steps data by date
        aligned_data = []
        weight_dict = {date: wt for date, wt in weight_data}
        steps_dict = {date: st for date, st in steps_data}

        for date in set(weight_dict.keys()) & set(steps_dict.keys()):
            aligned_data.append([weight_dict[date], steps_dict[date]])

        if len(aligned_data) > 2:
            df = pd.DataFrame(aligned_data, columns=["weight_kg", "steps_count"])
            correlation_matrix["weight_steps_corr"] = df.corr().to_dict()
            correlation_matrix["sample_size"] = len(aligned_data)
            correlation_matrix["corr_value"] = (
                df["weight_kg"].corr(df["steps_count"]) if len(aligned_data) > 1 else 0
            )

    # 2. Time Series Analysis
    time_series_data = {}
    if weight_data:
        dates, weights = zip(*weight_data)
        time_series_data["weight_trend"] = {
            "slope": calculate_linear_trend_slopes(
                list(zip(pd.to_datetime(dates), weights))
            ),
            "r_squared": calculate_r_squared(list(zip(pd.to_datetime(dates), weights))),
            "seasonal_components": analyze_seasonality(weights),
        }

    # 3. Distribution Analysis
    dist_analysis = {}
    if weight_data:
        weights_only = [wt for _, wt in weight_data]
        dist_analysis["weight_stats"] = {
            "mean": float(np.mean(weights_only)),
            "median": float(np.median(weights_only)),
            "std": float(np.std(weights_only)),
            "percentiles_25": float(np.percentile(weights_only, 25)),
            "percentiles_75": float(np.percentile(weights_only, 75)),
            "distribution_shape": classify_distribution_shape(weights_only),
        }

    # 4. Advanced clustering for behavioral patterns
    cluster_data = None
    if len(weight_data) > 10 and len(steps_data) > 10:
        # Prepare behavioral features
        features_df = pd.DataFrame(
            {
                "date": pd.to_datetime([date for date, _ in weight_data]),
                "weight": [wt for _, wt in weight_data],
                "steps": [step for _, step in steps_data]
                if steps_data
                else [0] * len(weight_data),
            }
        )

        # Keep only overlapping dates
        dates_set = set([date for date, _ in weight_data]) & set(
            [date for date, _ in steps_data]
        )
        if len(dates_set) > 10:  # Need at least 10 data points for clustering
            features_filtered = features_df[features_df["date"].dt.date.isin(dates_set)]
            if len(features_filtered) > 10:
                feature_cols = ["weight", "steps"]

                # Standardize the features
                scaler = StandardScaler()
                scaled_features = scaler.fit_transform(features_df[feature_cols])

                # Perform cluster analysis
                kmeans = KMeans(
                    n_clusters=3, random_state=42
                )  # 3 cluster groups: weight gain/loss/stable
                clusters = kmeans.fit_predict(scaled_features)

                cluster_analysis = {
                    "cluster_centers": kmeans.cluster_centers_.tolist(),
                    "data_points_cluster": features_df.assign(cluster=clusters).to_dict(
                        "records"
                    ),
                    "cluster_counts": pd.Series(clusters).value_counts().to_dict(),
                    "algorithm_applied": "k-means-n=3",
                }

                cluster_data.update(cluster_analysis)

    # 5. Statistical validity analysis
    validity_metrics = {}
    sample_size_weight = len(weight_data)
    if sample_size_weight >= 30:
        validity_metrics["statistical_power"] = "high"
        validity_metrics["confidence_level"] = "0.95"
    elif sample_size_weight >= 10:
        validity_metrics["statistical_power"] = "medium"
        validity_metrics["confidence_level"] = "0.85"
    else:
        validity_metrics["statistical_power"] = "low"
        validity_metrics["confidence_level"] = "0.70"

    # Compile scientific dashboard response
    dashboard_data = ScientificHealthDashboardResponse(
        period_start=start_date.isoformat(),
        period_end=end_date.isoformat(),
        data_points_count={
            "weight_records": len(weight_data),
            "steps_records": len(steps_data),
            "habit_completions": len(habit_completions),
            "emotional_checkins": len(emotional_data),
            "nutrition_logs": len(meals),
        },
        correlation_analysis={
            "matrix": correlation_matrix,
            "significant_relationships": [
                f"体重-步数相关性: {correlation_matrix.get('corr_value', 0):.3f}"
            ]
            if "corr_value" in correlation_matrix
            else [],
        },
        time_series_analysis=time_series_data,
        distribution_analysis=dist_analysis,
        clustering_analysis=cluster_data,
        statistical_validity=validity_metrics,
        scientific_insights=generate_scientific_insights(
            weight_data, steps_data, sample_size_weight
        ),
        visualization_recommendations=[
            "体重变化趋势使用加权移动平均线以平滑波动",
            "建议使用双轴图比较体重和步数趋势",
            "采用箱型图展示不同时间段体重分布变化",
        ],
        confidence_intervals={
            "weight_mean_ci": calculate_confidence_interval(
                [wt for _, wt in weight_data]
            )
            if weight_data
            else None
        },
    )

    logger.info(
        "Scientific health dashboard generated",
        user_id=current_user.id,
        days_analyzed=days_back,
        data_points=len(weight_data),
    )

    return dashboard_data


def calculate_linear_trend_slopes(date_values):
    """计算线性趋势的斜率"""
    if len(date_values) < 2:
        return 0

    # Convert dates to numeric (seconds from epoch) and values to array
    x_values = [
        (dt - date_values[0][0]).days for dt, _ in date_values
    ]  # Days since first data point
    y_values = [val for _, val in date_values]

    # Calculate linear regression
    slope, _, _, _, _ = stats.linregress(x_values, y_values)
    return float(slope)


def calculate_r_squared(date_values):
    """计算R²值"""
    if len(date_values) < 2:
        return 0

    x_values = [(dt - date_values[0][0]).days for dt, _ in date_values]
    y_values = [val for _, val in date_values]

    slope, intercept, r_value, p_value, std_err = stats.linregress(x_values, y_values)
    return r_value**2


def analyze_seasonality(data_values):
    """分析季节性模式"""
    # Simplified seasonality analysis - in real app would use more sophisticated analysis
    seasonal_patterns = {
        "trend": "increasing"
        if data_values and data_values[-1] > data_values[0]
        else "decreasing"
        if data_values and data_values[-1] < data_values[0]
        else "stable",
        "volatility": float(np.std(data_values)) if len(data_values) > 1 else 0,
    }
    return seasonal_patterns


def classify_distribution_shape(values):
    """分类分布形状"""
    if len(values) < 4:
        return "insufficient_data"

    # Calculate skewness and kurtosis to classify distribution
    skewness = stats.skew(values)
    kurtosis = stats.kurtosis(values)  # This is excess kurtosis (normal = 0)

    if abs(skewness) < 0.5:
        symmetry = "symmetrical"
    elif skewness > 0.5:
        symmetry = "right_skewed"
    else:
        symmetry = "left_skewed"

    if abs(kurtosis) < 0.5:
        peakedness = "mesokurtic"
    elif kurtosis > 0.5:
        peakedness = "leptokurtic"  # Fat tails
    else:
        peakedness = "platykurtic"  # Thin tails

    return {
        "symmetry": symmetry,
        "peakedness": peakedness,
        "skewness": float(skewness),
        "kurtosis": float(kurtosis),
    }


def calculate_confidence_interval(data_values, confidence=0.95):
    """计算置信区间"""
    if len(data_values) < 2:
        return None

    mean_val = np.mean(data_values)
    stderr = stats.sem(data_values)  # Standard error of the mean
    margin_error = stderr * stats.t.ppf((1 + confidence) / 2.0, len(data_values) - 1)

    return {
        "mean": float(mean_val),
        "lower_bound": float(mean_val - margin_error),
        "upper_bound": float(mean_val + margin_error),
        "confidence_level": confidence,
    }


def generate_scientific_insights(weight_data, steps_data, sample_size):
    """生成科学洞察"""
    insights = []

    if sample_size >= 10:
        if len(weight_data) > 1:
            weight_change = weight_data[-1][1] - weight_data[0][1]
            trend_desc = (
                "减少"
                if weight_change < -0.5
                else "增加"
                if weight_change > 0.5
                else "稳定"
            )

            if abs(weight_change) >= 1.0:
                time_span_days = (weight_data[-1][0] - weight_data[0][0]).days
                if time_span_days > 0:
                    avg_daily_change = weight_change / time_span_days
                    insights.append(
                        f"在过去的{time_span_days}天里，您的体重呈现{trend_desc}趋势，平均每天{'减轻' if avg_daily_change < 0 else '增加'}{'%.2f' % abs(avg_daily_change)}kg"
                    )

        if len(steps_data) > 5:
            avg_steps = np.mean([st for _, st in steps_data])
            if avg_steps > 8000:  # High activity
                insights.append("平均步数处于健康活动水平，有利于体重管理和心血管健康")
            elif avg_steps > 4000:  # Moderate activity
                insights.append("平均步数水平适中，建议逐渐增加活动量以提高健康效益")
            else:
                insights.append(
                    "平均步数偏少，建议制定循序渐渐的步行计划以提高活动水平"
                )

        if len(steps_data) > 5 and len(weight_data) > 10:
            # Analyze correlation if we have sufficient data points
            # Align data by date for correlation
            weight_dict = {date: wt for date, wt in weight_data}
            steps_dict = {date: st for date, st in steps_data}
            aligned_dates = set(weight_dict.keys()) & set(steps_dict.keys())

            if (
                len(aligned_dates) > 5
            ):  # Need at least 5 overlapping data points for reliable correlation
                weight_vals = [weight_dict[d] for d in aligned_dates]
                steps_vals = [steps_dict[d] for d in aligned_dates]

                corr, p_value = stats.pearsonr(weight_vals, steps_vals)

                if abs(corr) > 0.3:  # Moderate correlation
                    direction = "负相关" if corr < 0 else "正相关"
                    insights.append(
                        f"您的步数与体重呈现{abs(corr):.2f}的{direction}关系，表明活动水平与体重变化存在一定的关联性"
                    )

    return insights
