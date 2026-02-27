from fastapi import APIRouter

from app.api.v1.endpoints import (
    system_config,
    ai,
    auth,
    chat,
    dashboard,
    emotional_support,
    exercises,
    exercise_checkin,
    gamification,
    habit,
    habits,
    habit_stats,
    health,
    health_assessment,
    health_data,
    health_reports,
    health_score,
    meals,
    meal_checkin,
    memory,
    # notifications,  # 临时注释，待修复认证依赖
    # nutrition,  # 已删除 - 只保留 2 个端点，合并到 meals.py 更合适
    personalized_advice,
    professional_fusion,
    reward_analytics,
    reward_personalization,
    rewards,
    scientific_persona,
    scientific_visualization,
    user_experience,
    users,
)

api_router = APIRouter()

# 包含核心模块的路由
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
# api_router.include_router(nutrition.router, prefix="/nutrition", tags=["nutrition"])  # 已删除
api_router.include_router(habits.router, prefix="/habits", tags=["habits"])
api_router.include_router(habit_stats.router, prefix="/habits", tags=["habits-stats"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

# 核心端点
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(
    health_data.router, prefix="/health-data", tags=["health-data"]
)

# 记忆系统端点
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])

# 情感支持端点
api_router.include_router(
    emotional_support.router, prefix="/emotional-support", tags=["emotional-support"]
)

# 运动记录端点
api_router.include_router(exercises.router, prefix="/exercises", tags=["exercises"])

# 运动打卡端点
api_router.include_router(
    exercise_checkin.router, prefix="/exercise-checkin", tags=["exercise-checkin"]
)

# 餐饮记录端点
api_router.include_router(meals.router, prefix="/meals", tags=["meals"])

# 饮食打卡端点
api_router.include_router(
    meal_checkin.router, prefix="/meal-checkin", tags=["meal-checkin"]
)

# 游戏化系统端点
api_router.include_router(
    gamification.router, prefix="/gamification", tags=["gamification"]
)
api_router.include_router(rewards.router, prefix="/rewards", tags=["rewards"])
api_router.include_router(
    reward_analytics.router, prefix="/reward-analytics", tags=["reward-analytics"]
)
api_router.include_router(
    reward_personalization.router,
    prefix="/reward-personalization",
    tags=["reward-personalization"],
)

# 通知系统端点
# api_router.include_router(
#     notifications.router, prefix="/notifications", tags=["notifications"]
# )

# 健康评估与报告端点
api_router.include_router(
    health_assessment.router, prefix="/health-assessment", tags=["health-assessment"]
)
api_router.include_router(
    health_reports.router, prefix="/health-reports", tags=["health-reports"]
)
api_router.include_router(
    health_score.router, prefix="/health-score", tags=["health-score"]
)

# 个性化建议端点
api_router.include_router(
    personalized_advice.router,
    prefix="/personalized-advice",
    tags=["personalized-advice"],
)

# 科学可视化端点
api_router.include_router(
    scientific_visualization.router,
    prefix="/scientific-visualization",
    tags=["scientific-visualization"],
)
api_router.include_router(
    scientific_persona.router, prefix="/scientific-persona", tags=["scientific-persona"]
)

# 专业融合端点
api_router.include_router(
    professional_fusion.router,
    prefix="/professional-fusion",
    tags=["professional-fusion"],
)

# 用户体验端点
api_router.include_router(
    user_experience.router, prefix="/user-experience", tags=["user-experience"]
)

# 系统管理端点
api_router.include_router(system_config.router, prefix="/admin", tags=["system-config"])
