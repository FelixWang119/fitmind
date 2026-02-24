from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
from sqlalchemy.orm import Session

from app.models.user import User

logger = structlog.get_logger()


class ExerciseCalorieService:
    """运动卡路里估算服务

    基于 MET (Metabolic Equivalent of Task) 标准公式
    参考：ACSM (美国运动医学会) 标准
    """

    # F7: MET 值标准配置 (基于 ACSM 标准)
    MET_VALUES: Dict[str, float] = {
        "Running": 8.0,  # 跑步 (8km/h)
        "Cycling": 6.0,  # 骑行 (中等)
        "Swimming": 6.0,  # 游泳 (中等)
        "Strength Training": 3.5,  # 力量训练
        "Yoga": 2.5,  # 瑜伽
        "Walking": 3.5,  # 走路 (5km/h)
        "HIIT": 8.0,  # 高强度间歇
        "Elliptical": 5.0,  # 椭圆机
        "Rowing": 7.0,  # 划船机
        "Basketball": 6.5,  # 篮球
        "Soccer": 7.0,  # 足球
        "Tennis": 7.3,  # 网球
        "Hiking": 6.0,  # 徒步
        "Dancing": 4.5,  # 舞蹈
        "Pilates": 3.0,  # 普拉提
        "CrossFit": 8.0,  # CrossFit
    }

    # F5: 强度系数 - 仅用于计算，不持久化
    INTENSITY_FACTORS: Dict[str, float] = {
        "low": 0.8,
        "medium": 1.0,
        "high": 1.2,
    }

    # 默认体重 (kg) - 当用户体重缺失时使用
    DEFAULT_WEIGHT_KG = 70.0

    def __init__(self, db: Session):
        self.db = db

    def estimate_calories(
        self,
        exercise_type: str,
        duration_minutes: int,
        intensity: str,
        weight_kg: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        估算卡路里燃烧

        公式：卡路里 = MET × 体重 (kg) × 时长 (小时) × 强度系数

        F5 说明：intensity_factor 是计算中间值，不存储到数据库
        数据库仅存储 intensity (low/medium/high) 和最终 calories_burned

        F10: 同步计算，在创建打卡时立即执行

        Args:
            exercise_type: 运动类型
            duration_minutes: 时长 (分钟)
            intensity: 强度 (low/medium/high)
            weight_kg: 体重 (kg)，如果为 None 则使用默认值

        Returns:
            {
                "calories_burned": int,
                "is_estimated": True,
                "estimation_details": {
                    "met_value": float,
                    "weight_kg": float,
                    "duration_hours": float,
                    "intensity_factor": float,
                    "formula": str
                },
                "weight_warning": Optional[str]  # 如果使用默认体重，提示用户设置
            }
        """
        # 获取 MET 值 (未知运动使用默认值 5.0)
        met_value = self.MET_VALUES.get(exercise_type, 5.0)

        # 获取强度系数
        intensity_factor = self.INTENSITY_FACTORS.get(intensity, 1.0)

        # 计算时长 (小时)
        duration_hours = duration_minutes / 60.0

        # 使用提供的体重或默认值
        used_weight = weight_kg if weight_kg is not None else self.DEFAULT_WEIGHT_KG
        weight_warning = None

        if weight_kg is None:
            weight_warning = f"使用默认体重 {self.DEFAULT_WEIGHT_KG}kg 计算，请在个人资料中设置您的体重以获得更准确的结果"

        # 计算卡路里
        calories_burned = met_value * used_weight * duration_hours * intensity_factor

        logger.info(
            "Calories estimated",
            exercise_type=exercise_type,
            duration_minutes=duration_minutes,
            intensity=intensity,
            weight_kg=used_weight,
            calories_burned=int(calories_burned),
        )

        return {
            "calories_burned": int(calories_burned),
            "is_estimated": True,
            "estimation_details": {
                "met_value": met_value,
                "weight_kg": used_weight,
                "duration_hours": duration_hours,
                "intensity_factor": intensity_factor,
                "formula": "MET × 体重 (kg) × 时长 (h) × 强度系数",
            },
            "weight_warning": weight_warning,
        }

    def get_user_weight_kg(self, user_id: int) -> Optional[float]:
        """
        获取用户体重 (kg)

        项目中体重存储为克，需要转换为千克
        """
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user or not user.initial_weight:
            return None

        # 克转千克
        return user.initial_weight / 1000.0

    def get_exercise_types(self) -> List[Dict[str, Any]]:
        """
        返回预设运动类型列表 (包含 MET 值和分类)
        """
        # 运动类型分类映射
        CATEGORY_MAP: Dict[str, str] = {
            "Running": "有氧",
            "Cycling": "有氧",
            "Swimming": "有氧",
            "Walking": "有氧",
            "HIIT": "有氧",
            "Elliptical": "有氧",
            "Rowing": "有氧",
            "Basketball": "有氧",
            "Soccer": "有氧",
            "Tennis": "有氧",
            "Hiking": "有氧",
            "Dancing": "有氧",
            "Strength Training": "力量",
            "CrossFit": "力量",
            "Yoga": "灵活",
            "Pilates": "灵活",
        }

        return [
            {
                "type": type_name,
                "met_value": met,
                "category": CATEGORY_MAP.get(type_name, "其他"),
            }
            for type_name, met in self.MET_VALUES.items()
        ]

    def recalculate_calories(
        self,
        exercise_type: str,
        duration_minutes: int,
        intensity: str,
        old_weight_kg: float,
        new_weight_kg: float,
    ) -> Dict[str, Any]:
        """
        重新计算卡路里 (当用户更新体重时)

        注意：当前设计不支持历史数据重算，此方法保留供未来扩展
        """
        # 计算体重变化比例
        weight_ratio = new_weight_kg / old_weight_kg

        # 重新估算
        met_value = self.MET_VALUES.get(exercise_type, 5.0)
        intensity_factor = self.INTENSITY_FACTORS.get(intensity, 1.0)
        duration_hours = duration_minutes / 60.0

        new_calories = met_value * new_weight_kg * duration_hours * intensity_factor

        return {
            "old_calories": int(
                met_value * old_weight_kg * duration_hours * intensity_factor
            ),
            "new_calories": int(new_calories),
            "weight_change_kg": new_weight_kg - old_weight_kg,
        }


def get_exercise_calorie_service(db: Session) -> ExerciseCalorieService:
    """获取卡路里估算服务实例"""
    return ExerciseCalorieService(db)
