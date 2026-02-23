from datetime import datetime
from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.scientific_persona import (
    BMICalculation,
    HealthRiskAssessment,
    MetabolicMetrics,
    PersonaMessage,
    ScientificInsight,
    ScientificReport,
)
from app.services.scientific_persona_service import get_scientific_persona_service

logger = structlog.get_logger()

router = APIRouter()


@router.get("/scientific-report", response_model=ScientificReport)
async def get_scientific_report(
    days: int = Query(30, ge=7, le=90, description="报告周期天数"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取科学量化健康报告"""
    logger.info("Generating scientific report", user_id=current_user.id, days=days)

    persona_service = get_scientific_persona_service(db)

    try:
        report = persona_service.generate_scientific_report(current_user, days)
        return report

    except Exception as e:
        logger.error(
            "Failed to generate scientific report",
            user_id=current_user.id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate scientific report",
        )


@router.get("/bmi", response_model=BMICalculation)
async def calculate_bmi(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """计算BMI"""
    logger.info("Calculating BMI", user_id=current_user.id)

    persona_service = get_scientific_persona_service(db)

    try:
        bmi = persona_service._calculate_bmi(current_user)
        category = persona_service._get_bmi_category(current_user)

        healthy_ranges = {
            "偏瘦": "建议增加营养摄入，适度增重",
            "正常": "保持当前体重，继续健康生活方式",
            "超重": "建议适度减重，改善饮食和运动习惯",
            "肥胖": "强烈建议制定减重计划，咨询专业人士",
        }

        return BMICalculation(
            bmi=bmi,
            category=category,
            healthy_range="18.5 - 24.9",
            recommendation=healthy_ranges.get(category, "保持健康生活方式"),
        )

    except Exception as e:
        logger.error("Failed to calculate BMI", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate BMI",
        )


@router.get("/metabolic-metrics", response_model=MetabolicMetrics)
async def get_metabolic_metrics(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取代谢指标"""
    logger.info("Getting metabolic metrics", user_id=current_user.id)

    persona_service = get_scientific_persona_service(db)
    nutrition_service = persona_service.nutrition_service

    try:
        bmr = nutrition_service.calculate_bmr(current_user)
        tdee = nutrition_service.calculate_tdee(current_user)
        metabolic_age = persona_service._estimate_metabolic_age(current_user)

        # 估算身体成分（简化版）
        bmi = persona_service._calculate_bmi(current_user)
        if current_user.gender == "male":
            body_fat_estimate = (1.20 * bmi) + (0.23 * (current_user.age or 30)) - 16.2
        else:
            body_fat_estimate = (1.20 * bmi) + (0.23 * (current_user.age or 30)) - 5.4

        return MetabolicMetrics(
            bmr=round(bmr, 0),
            tdee=round(tdee, 0),
            metabolic_age=metabolic_age.get("estimated", current_user.age or 30),
            body_composition_estimate={
                "body_fat_percent": round(max(10, min(50, body_fat_estimate)), 1),
                "lean_mass_estimate_kg": round(
                    ((current_user.initial_weight or 70000) / 1000)
                    * (1 - max(10, min(50, body_fat_estimate)) / 100),
                    1,
                )
                if current_user.initial_weight
                else 0,
            },
        )

    except Exception as e:
        logger.error(
            "Failed to get metabolic metrics", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate metabolic metrics",
        )


@router.get("/health-risk-assessment", response_model=HealthRiskAssessment)
async def get_health_risk_assessment(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取健康风险评估"""
    logger.info("Getting health risk assessment", user_id=current_user.id)

    persona_service = get_scientific_persona_service(db)

    try:
        risk_assessment = persona_service._assess_health_risk(current_user)

        # 获取BMI
        bmi = persona_service._calculate_bmi(current_user)
        bmi_category = persona_service._get_bmi_category(current_user)

        # 评估各类风险
        cardiovascular_risk = (
            "高" if bmi_category == "肥胖" else "中等" if bmi_category == "超重" else "低"
        )
        metabolic_risk = "高" if bmi >= 30 else "中等" if bmi >= 25 else "低"

        # 识别生活方式风险因素
        lifestyle_risks = []
        if bmi_category in ["超重", "肥胖"]:
            lifestyle_risks.append("体重超标")
        if (
            not current_user.activity_level
            or current_user.activity_level == "sedentary"
        ):
            lifestyle_risks.append("久坐生活方式")

        # 保护因素
        protective_factors = []
        if current_user.activity_level in ["active", "very_active"]:
            protective_factors.append("规律运动")
        if bmi_category == "正常":
            protective_factors.append("健康体重")

        return HealthRiskAssessment(
            overall_risk=risk_assessment["risk_level"],
            cardiovascular_risk=cardiovascular_risk,
            metabolic_risk=metabolic_risk,
            lifestyle_risk_factors=lifestyle_risks,
            protective_factors=protective_factors,
            recommendations=[
                "定期体检监测血压、血糖、血脂",
                "保持健康体重",
                "每周至少150分钟中等强度运动",
                "均衡饮食，控制热量摄入",
            ],
        )

    except Exception as e:
        logger.error(
            "Failed to assess health risk", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assess health risk",
        )


@router.get("/scientific-insights", response_model=List[ScientificInsight])
async def get_scientific_insights(
    days: int = Query(30, ge=7, le=90, description="分析周期天数"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取科学洞察"""
    logger.info("Getting scientific insights", user_id=current_user.id)

    persona_service = get_scientific_persona_service(db)

    try:
        report = persona_service.generate_scientific_report(current_user, days)
        insights = []

        # 体重洞察
        if report["weight_analysis"].get("data_available"):
            weight_trend = report["weight_analysis"]["trend_analysis"]["trend"]
            insights.append(
                ScientificInsight(
                    insight_type="体重趋势",
                    finding=f"体重呈{weight_trend}趋势",
                    clinical_relevance="反映能量平衡状态",
                    actionable_recommendation="根据趋势调整饮食和运动计划",
                )
            )

        # 营养洞察
        if report["nutrition_analysis"].get("data_available"):
            score = report["nutrition_analysis"]["nutrition_score"]["overall_score"]
            insights.append(
                ScientificInsight(
                    insight_type="营养管理",
                    finding=f"营养管理评分{score}分",
                    clinical_relevance="营养质量直接影响健康结果",
                    actionable_recommendation="持续保持高营养质量饮食",
                )
            )

        # 行为洞察
        stage = report["behavior_analysis"]["behavior_change_stage"]["current_stage"]
        insights.append(
            ScientificInsight(
                insight_type="行为改变",
                finding=f"当前处于{stage}",
                statistical_significance="基于跨理论模型",
                clinical_relevance="不同阶段需要不同支持策略",
                actionable_recommendation="采用适合当前阶段的干预方法",
            )
        )

        # 心理洞察
        stress_level = report["psychological_analysis"]["stress_analysis"][
            "average_stress_level"
        ]
        insights.append(
            ScientificInsight(
                insight_type="压力管理",
                finding=f"平均压力水平{stress_level}/10",
                clinical_relevance="慢性压力影响代谢和体重管理",
                actionable_recommendation="实施压力管理策略"
                if stress_level > 5
                else "继续当前压力管理",
            )
        )

        return insights

    except Exception as e:
        logger.error(
            "Failed to get scientific insights", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate scientific insights",
        )


@router.post("/generate-persona-message", response_model=PersonaMessage)
async def generate_persona_message(
    context: str = Query(..., description="对话上下文或用户问题"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """生成科学人设的回复消息"""
    logger.info("Generating persona message", user_id=current_user.id, context=context)

    persona_service = get_scientific_persona_service(db)

    try:
        # 获取用户数据
        report = persona_service.generate_scientific_report(current_user, 30)

        # 生成科学人设消息
        message = persona_service.generate_scientific_persona_message(
            current_user, context, report
        )

        return PersonaMessage(
            message=message,
            tone="科学、专业、循证",
            scientific_citations=[
                "基于最新营养学和运动科学研究",
                "参考WHO和AHA指南",
            ],
            confidence_level="高"
            if report["data_quality_assessment"]["overall_quality"] >= 70
            else "中",
        )

    except Exception as e:
        logger.error(
            "Failed to generate persona message", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate persona message",
        )


@router.get("/data-quality")
async def get_data_quality_assessment(
    days: int = Query(30, ge=7, le=90, description="评估周期天数"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取数据质量评估"""
    logger.info("Getting data quality assessment", user_id=current_user.id)

    persona_service = get_scientific_persona_service(db)

    try:
        quality_assessment = persona_service._assess_data_quality(current_user, days)
        return quality_assessment

    except Exception as e:
        logger.error(
            "Failed to assess data quality", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assess data quality",
        )


@router.get("/health-score-summary")
async def get_health_score_summary(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取健康评分摘要"""
    logger.info("Getting health score summary", user_id=current_user.id)

    persona_service = get_scientific_persona_service(db)

    try:
        report = persona_service.generate_scientific_report(current_user, 30)
        health_score = report["comprehensive_health_score"]

        return {
            "total_score": health_score["total_score"],
            "grade": health_score["grade"],
            "percentile": health_score["percentile"],
            "interpretation": health_score["interpretation"],
            "components": health_score["components"],
            "last_updated": report["generated_at"],
        }

    except Exception as e:
        logger.error(
            "Failed to get health score summary", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get health score summary",
        )


@router.get("/evidence-based-recommendations")
async def get_evidence_based_recommendations(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取循证建议"""
    logger.info("Getting evidence-based recommendations", user_id=current_user.id)

    persona_service = get_scientific_persona_service(db)

    try:
        report = persona_service.generate_scientific_report(current_user, 30)
        return report["evidence_based_recommendations"]

    except Exception as e:
        logger.error(
            "Failed to get recommendations", user_id=current_user.id, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendations",
        )
