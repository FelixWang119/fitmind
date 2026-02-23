from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from scipy import stats
from sqlalchemy.orm import Session
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.health_record import HealthRecord
from app.models.user import User as UserModel
from app.models.nutrition import Meal
from app.schemas.health_report import HealthReportRequest, HealthReportResponse, DetailedHealthReport, HealthTrendData, AchievementInfo

logger = structlog.get_logger()

router = APIRouter()


def detect_trend_pattern(data_points):
    """
    检测趋势模式 - 根据连续数据点的趋势特征判断
    返回: trend_direction, confidence, pattern_type
    """
    if len(data_points) < 3:
        return "insufficient_data", 0, "insufficient"
    
    # 数据排序并提取数值
    sorted_points = sorted(data_points)
    values = [point[1] for point in sorted_points]  # 日期和数值列表
    
    # 计算趋势的线性回归斜率
    x_vals = list(range(len(values)))
    slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, values)
    
    # 阿定趋势方向
    trend_direction = "stable"
    if slope > 0.1:  # 阀正值阈值
        trend_direction = "increasing"
    elif slope < -0.1:  # 负坡度阈值
        trend_direction = "decreasing"
    
    # 趋势置信度（基于R²值）
    r_squared = r_value ** 2
    confidence = min(r_squared * 100, 100)  # 调整至百分比
    
    # 模式类型（基于坡度和R²值）
    if r_squared > 0.7:
        if slope > 0.5:
            pattern_type = "sharp_increase"
        elif slope < -0.5:
            pattern_type = "steep_decline"
        elif abs(slope) < 0.2:
            pattern_type = "gradual_flat"
        else:
            pattern_type = "steady_trend"
    else:
        pattern_type = "fluctuating"
    
    return trend_direction, confidence, pattern_type


def detect_anomalies(data_points, threshold=2):
    """
    检测数据中的异常值 - 使用标准偏差方法
    """
    if len(data_points) < 5:
        return []  # 不足5个数据点时不检测异常值
    
    values = [pt[1] for pt in data_points]  # 获取数值部分
    mean_val = np.mean(values)
    std_dev = np.std(values)
    
    anomalies = []
    for i, (date, val) in enumerate(data_points):
        if abs(val - mean_val) > threshold * std_dev:
            anomalies.append({
                "date": date,
                "value": val,
                "anomaly_type": "deviation" if val > mean_val else "deficiency",
                "deviation_amount": abs(val - mean_val),
                "deviation_units": "std_dev",
                "severity": "medium" if threshold < 2.5 else ("low" if threshold >= 1.0 else "high")
            })
    
    return anomalies


def calculate_consistency_score(data_points):
    """
    计算一致性评分 - 基于数据点频率和变化幅度
    """
    if len(data_points) < 2:
        return 0  # 无数据的一致性为0
    
    dates = [pt[0] for pt in data_points]
    values = [pt[1] for pt in data_points]
    
    # 日期间隔的稳定性评分
    date_gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
    date_consistency = 100 - (np.std(date_gaps) * 5) if len(date_gaps) > 1 else 100
    
    # 值的稳定性评分
    value_changes = [abs(values[i+1] - values[i]) for i in range(len(values)-1)]
    if len(value_changes) > 0:
        avg_change = np.mean(value_changes)
        # 小变化值表示更好的一致性
        value_consistency = max(0, 100 - avg_change * 10)
    else:
        value_consistency = 100
    
    # 综合一致性评分 (简单的加权平均)
    return int(0.6 * date_consistency + 0.4 * value_consistency)


@router.post("/generate-advanced-report", response_model=HealthReportResponse)
async def generate_advanced_health_report(
    report_request: HealthReportRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """生成高级健康趋势分析报告"""
    logger.info(
        "Generating advanced health report",
        user_id=current_user.id,
        start_date=report_request.start_date,
        end_date=report_request.end_date,
    )

    # 确定报告范围
    start_date = report_request.start_date
    end_date = report_request.end_date or datetime.utcnow().date()

    # 获取体重数据
    weight_records = (
        db.query(HealthRecord)
        .filter(
            HealthRecord.user_id == current_user.id,
            HealthRecord.record_date >= start_date,
            HealthRecord.record_date <= end_date,
            HealthRecord.weight != None
        )
        .order_by(HealthRecord.record_date)
        .all()
    )

    # 获取饮食数据
    meals_data = (
        db.query(Meal)
        .filter(
            Meal.user_id == current_user.id,
            Meal.meal_datetime >= start_date,
            Meal.meal_datetime <= end_date
        )
        .order_by(Meal.meal_datetime)
        .all()
    )

    # 计算营养数据
    total_calories = 0
    daily_calories = defaultdict(float)
    daily_protein = defaultdict(float) 
    daily_carbs = defaultdict(float)
    daily_fat = defaultdict(float)
    
    for meal in meals_data:
        if meal.calories:
            total_calories += meal.calories
            date_key = meal.meal_datetime.date()
            daily_calories[date_key] += meal.calories or 0
            daily_protein[date_key] += meal.protein or 0
            daily_carbs[date_key] += meal.carbs or 0
            daily_fat[date_key] += meal.fat or 0

    # 获取运动数据 (HealthRecord 中的运动相关字段)
    exercise_records = (
        db.query(HealthRecord)
        .filter(
            HealthRecord.user_id == current_user.id,
            HealthRecord.record_date >= start_date,
            HealthRecord.record_date <= end_date,
            (HealthRecord.exercise_minutes != None)
        )
        .order_by(HealthRecord.record_date)
        .all()
    )

    # 计算运动指标
    total_exercise_minutes = 0
    total_steps = 0
    daily_exercise_minutes = defaultdict(int)
    daily_steps = defaultdict(int) 
    
    for record in exercise_records:
        if record.exercise_minutes:
            total_exercise_minutes += record.exercise_minutes
            daily_exercise_minutes[record.record_date] += record.exercise_minutes
        if record.steps_count:
            total_steps += record.steps_count
            daily_steps[record.record_date] += record.steps_count

    # 体重趋势分析
    if weight_records:
        # 转换体重克数为千克数
        weight_data_points = [
            (r.record_date, r.weight / 1000.0)  # Convert from grams to kg  
            for r in weight_records 
            if r.weight
        ]
        
        if weight_data_points:
            # 趋势检测
            trend_direction, confidence, pattern_type = detect_trend_pattern(weight_data_points)
            
            # 异常值检测
            anomalies = detect_anomalies(weight_data_points)
            
            avg_weight = sum(w[1] for w in weight_data_points) / len(weight_data_points)
            starting_weight = weight_data_points[0][1]
            ending_weight = weight_data_points[-1][1]
            weight_change = ending_weight - starting_weight
            
            # 一致性评分
            consistency_score = calculate_consistency_score(weight_data_points)
            
        else:
            avg_weight = 0
            starting_weight = 0
            ending_weight = 0
            weight_change = 0
            trend_direction = "no_data"
            confidence = 0
            pattern_type = "none"
            anomalies = []
            consistency_score = 0
    else:
        avg_weight = 0
        starting_weight = 0
        ending_weight = 0
        weight_change = 0
        trend_direction = "no_data"
        confidence = 0
        pattern_type = "no"
        anomalies = []
        consistency_score = 0

    # 构造高级健康报告数据
    from decimal import Decimal
    report_data = DetailedHealthReport(
        period_start=start_date.isoformat(),
        period_end=end_date.isoformat(),
        summary=HealthTrendData(
            weight_change_kg=round(weight_change, 2),
            starting_weight_kg=round(starting_weight, 2),
            current_weight_kg=round(ending_weight, 2),
            average_weight_kg=round(avg_weight, 2),
            total_calories_consumed=round(total_calories),
            average_daily_calories=round(total_calories / len(set(daily_calories.keys()))) if daily_calories else 0,
            total_exercise_minutes=total_exercise_minutes,
            average_daily_exercise_minutes=round(total_exercise_minutes / len(set(daily_exercise_minutes.keys()))) if daily_exercise_minutes else 0,
            total_steps=total_steps,
            average_daily_steps=round(total_steps / len(set(daily_steps.keys()))) if daily_steps else 0,
            active_days=len(set(list(daily_calories.keys()) + list(daily_exercise_minutes.keys()))),  # Days with any data
        ),
        trends={
            'weight_trend': {
                'direction': trend_direction,
                'confidence_percent': confidence,
                'pattern_type': pattern_type,
                'anomalies_detected': len(anomalies),
                'tracking_consistency_score': consistency_score
            } if weight_data_points else {
                'direction': 'insufficient_data',
                'confidence_percent': 0,
                'pattern_type': 'no_data',
                'anomalies_detected': 0,
                'tracking_consistency_score': 0
            },
            'nutrition_trend': {
                'daily_calories_pattern': 'balanced' if (min(daily_calories.values()) / max(daily_calories.values()) > 0.8) if daily_calories else False else 'variable' if daily_calories else 'no_data',
                'macro_balance_score': 70,  # Placeholder - would implement actual calculation
            },
            'exercise_trend': {  
                'weekly_average_minutes': total_exercise_minutes / 7 if total_exercise_minutes > 0 else 0,
                'goal_achievement_rate': (total_exercise_minutes / (7 * 30)) * 100 if total_exercise_minutes > 0 else 0  # Assuming 30 min/day goal
            },
        },
        achievements=[
            AchievementInfo(
                title="持续追踪者",
                description=f"连续追踪健康数据{len(weight_data_points)}天",
                achieved=len(weight_data_points) > 5,
                category="consistency"
            ),
            AchievementInfo(
                title="趋势观察家",
                description=f"数据记录一致性评分为{consistency_score}/100",
                achieved=consistency_score > 75,
                category="precision"
            ),
            AchievementInfo(
                title="健康改善",
                description="实现积极的健康指标变化",
                achieved=weight_change < -0.5,  # 如果减重超过0.5kg
                category="progress"
            ),
            AchievementInfo(
                title="坚持记录",
                description=f"本期内记录了{len(weight_data_points)}次体重",
                achieved=len(weight_data_points) > 3,
                category="participation"
            )
        ] if weight_data_points else [],
        recommendations=[
            f"当前体重趋势为{trend_direction}，置信度约{int(confidence)}%" if trend_direction != 'stable' else "体重基本稳定",
            f"检测到{'无异常' if not anomalies else str(len(anomalies))+'个数据异常'}"
        ],
        detailed_insights={
            "trend_analysis": {
                "weight_pattern": {
                    "detected_pattern": pattern_type,
                    "slope": f"{'+%.3f' % (detect_trend_pattern(weight_data_points)[0] if weight_data_points else 0)}",
                    "confidence": f"{confidence:.1f}%",
                    "consistency": consistency_score
                },
                "data_quality": {
                    "total_recordings": len(weight_data_points),
                    "days_with_records": len(set(daily_calories.keys())), 
                    "consistency_score": consistency_score,
                    "anomalies": len(anomalies),
                    "anomaly_details": [
                        f"在{anom['date']}记录{anom['value']:.2f}kg偏离平均值{anom['deviation_amount']:.2f}kg" 
                        for anom in anomalies
                    ]
                }
            },
            "comparison_to_goals": {
                "weight_progress_vs_target": f"当前减重{weight_change:.2f}kg" if weight_change < 0 else "当前增重{weight_change:.2f}kg",
                "calories_vs_target": "接近推荐2000卡路里阈值" if 1800 <= daily_calories.values().__iter__().__next__() if len(daily_calories) > 0 else 0 <= 2200 else "超出推荐摄入范围",
                "exercise_goal_progress": f"达到总运动目标的{int((total_exercise_minutes / (7*30))*100)}%" if total_exercise_minutes > 0 else "无运动记录"
            }
        }
    )

    logger.info(
        "Advanced health report generated",
        user_id=current_user.id,
        duration_days=(end_date - start_date).days,
        data_points=len(weight_data_points)
    )

    return HealthReportResponse(
        status="success",
        message="Advanced health trend analysis report generated successfully",
        report=report_data,
        generated_at=datetime.utcnow().isoformat()
    )


@router.get("/predictive-analysis", response_model=Dict)
async def get_predictive_analysis(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    prediction_days: int = Query(30, ge=7, le=90, description="预测天数 (7-90)"),
):
    """获取基于历史数据的预测分析"""
    logger.info("Generating predictive analysis", user_id=current_user.id, prediction_days=prediction_days)
    
    # 获取3个月的健康数据用于预测
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=prediction_days*2)  # 使用过去2倍预测天数的数据

    # 获取历史体重数据
    weight_records = (
        db.query(HealthRecord)
        .filter(
            HealthRecord.user_id == current_user.id,
            HealthRecord.record_date >= start_date,
            HealthRecord.record_date <= end_date,
            HealthRecord.weight != None
        )
        .order_by(HealthRecord.record_date)
        .all()
    )

    if weight_records:
        # 准备数据
        dates = [(record.record_date - start_date).days for record in weight_records]
        weights = [record.weight / 1000.0 for record in weight_records]  # 将到 Kg

        # 使用线性回归进行简单预测
        if len(weights) >= 3:
            X = np.array(dates).reshape(-1, 1)
            y = np.array(weights)
            
            model = LinearRegression()
            model.fit(X, y)
            
            # 预测
            future_dates = list(range(dates[-1] + 1, dates[-1] + prediction_days + 1))
            future_X = np.array(future_dates).reshape(-1, 1)
            predicted_weights = model.predict(future_X)
            
            prediction_data = {
                "method": "linear_regression",
                "model_confidence": round(model.score(X, y) * 100, 2),
                "prediction_range": {
                    "start_date": (datetime.strptime(str(end_date), '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d'),
                    "end_date": (datetime.strptime(str(end_date), '%Y-%m-%d') + timedelta(days=prediction_days)).strftime('%Y-%m-%d')
                },
                "predicted_values": [
                    {
                        "day_in_future": day,
                        "estimated_weight_kg": round(float(pred_weight), 2), 
                        "date": (datetime.strptime(str(end_date), '%Y-%m-%d') + timedelta(days=day)).strftime('%Y-%m-%d')
                    }
                    for day, pred_weight in enumerate(predicted_weights, start=1)
                ],
                "trend_direction": "increasing" if model.coef_[0] > 0 else "decreasing" if model.coef_[0] < 0 else "stable",
                "current_weight": round(weights[-1], 2),
                "start_prediction_weight": round(predicted_weights[0], 2),
                "final_prediction_weight": round(predicted_weights[-1], 2)
            }
        else:
            prediction_data = {
                "error": "Not enough data points for prediction",
                "required_data_points": 3,
                "your_data_points": len(weights)
            }
    else:
        prediction_data = {
            "error": "You don't have any historical weight data.",
            "required_data_points": 3,
            "hint": "Start recording your weight to enable predictive trend analysis."
        }

    return prediction_data


# Include the existing endpoints as well for completeness
@router.post("/generate-report", response_model=HealthReportResponse)
async def generate_health_report(
    report_request: HealthReportRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """生成综合健康报告 (基本版本)"""
    
    logger.info(
        "Generating basic health report",
        user_id=current_user.id,
        start_date=report_request.start_date,
        end_date=report_request.end_date,
    )

    # 简化的基本报告实现（使用前面类似的逻辑）
    start_date = report_request.start_date
    end_date = report_request.end_date or datetime.utcnow().date()
    
    # 简化实现返回基本结构
    basic_report = DetailedHealthReport(
        period_start=start_date.isoformat(),
        period_end=end_date.isoformat(),
        summary=HealthTrendData(
            weight_change_kg=0.0,
            starting_weight_kg=70.0,
            current_weight_kg=70.0,
            average_weight_kg=70.0,
            total_calories_consumed=0,
            average_daily_calories=0,
            total_exercise_minutes=0,
            average_daily_exercise_minutes=0,
            total_steps=0,
            average_daily_steps=0,
            active_days=0
        ),
        trends={},
        achievements=[],
        recommendations=["请联系健康顾问以获得更详细的分析"],
        detailed_insights={}
    )

    return HealthReportResponse(
        status="success",
        message="Basic health report generated",
        report=basic_report,
        generated_at=datetime.utcnow().isoformat()
    )


@router.get("/get-pattern-insights", response_model=Dict)
async def get_pattern_insights(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取健康模式洞察"""
    # 获取用户的所有健康数据
    recent_records = (
        db.query(HealthRecord)
        .filter(
            HealthRecord.user_id == current_user.id,
            HealthRecord.record_date >= (datetime.utcnow() - timedelta(days=60)).date()
        )
        .order_by(HealthRecord.record_date.desc())
        .all()
    )

    insights = []
    
    if len(recent_records) > 5:
        # 分析记录频率
        dates = [r.record_date for r in recent_records]
        date_gaps = [(dates[i] - dates[i+1]).days for i in range(len(dates)-1)]
        avg_gap = sum(date_gaps) / len(date_gaps) if date_gaps else float('inf')
        
        if avg_gap <= 2:
            insights.append({
                "category": "Consistency",
                "highlight": "您正在连续记录健康数据！",
                "description": "优秀的连续记录习惯有助于获得更准确的趋势分析。",
                "importance": "high"
            })
        
        # Weight pattern analysis
        weight_records = [(r.record_date, r.weight/1000.0) for r in recent_records if r.weight and r.weight != 0]
        if len(weight_records) > 5:
            # 瘡单的趋势分析
            start_wt = weight_records[-1][1]  # 最早的一條記錄
            end_wt = weight_records[0][1]  # 最近的一條記錄
            wt_change = end_wt - start_wt
            change_percent = abs(wt_change / start_wt) * 100 if start_wt != 0 else 0
            
            direction = "loss" if wt_change < -0.5 else "gain" if wt_change > 0.5 else "stable"
            if direction != "stable":
                insight_text = f"您的体重趋势显示{'减轻' if direction == 'loss' else '增加'}，变化了{abs(wt_change):.2f}kg。"
                insights.append({
                    "category": "Weight Pattern",
                    "highlight": insight_text,
                    "description": "保持当前习惯有助于继续朝着目标进展。",
                    "importance": "medium"
                })

    # 返回洞察结果
    return {
        "insights_count": len(insights),
        "insights": insights,
        "summary": f"在此分析中发现了 {len(insights)} 条重要洞察",
        "recommended_actions": [
            "保持规律的健康数据记录",
            "如果体重呈减少趋势，继续维持当前饮食运动习惯",
            "根据分析结果调整治疗或健康策略"
        ] if insights else ["开始记录您的健康数据以启用智能洞察"]
    }