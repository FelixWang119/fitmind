"""AI 角色专业服务

提供不同 AI 角色的专业化回复：
- 营养师：饮食建议、营养分析、食谱推荐
- 行为教练：习惯养成、行为改变、目标设定
- 情感陪伴：情绪支持、积极鼓励、心理疏导
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import structlog
import random

logger = structlog.get_logger()


class NutritionistRole:
    """营养师角色 - 提供专业营养建议"""

    # 营养师角色设定
    ROLE_PROMPT = """你是一位专业的营养师，专注于体重管理和健康饮食指导。
你的职责：
1. 提供科学的营养建议和饮食指导
2. 分析用户的饮食记录并提供改进建议
3. 根据用户情况（BMI、BMR、TDEE）提供个性化建议
4. 推荐健康食谱和营养搭配
5. 解释营养学术语（卡路里、蛋白质、碳水化合物、脂肪等）

请使用专业但易懂的语言，给出具体的、可执行的建议。"""

    @classmethod
    def analyze_diet(cls, food_items: List[str], user_profile: Dict) -> str:
        """分析饮食并提供建议"""
        analysis = []

        # 简单分析逻辑
        has_protein = any(
            "肉" in item or "蛋" in item or "鱼" in item or "奶" in item or "豆" in item
            for item in food_items
        )
        has_vegetable = any(
            "菜" in item or "蔬" in item or "瓜" in item for item in food_items
        )
        has_carb = any(
            "饭" in item or "面" in item or "包" in item or "面包" in item
            for item in food_items
        )
        has_fruit = any(
            "果" in item or "蕉" in item or "苹果" in item for item in food_items
        )

        if not has_protein:
            analysis.append("⚠️ 蛋白质摄入不足，建议增加瘦肉、鱼类、蛋类或豆制品")
        if not has_vegetable:
            analysis.append("⚠️ 蔬菜摄入不足，建议每餐至少包含一份蔬菜")
        if has_carb and len([i for i in food_items if "饭" in i or "面" in i]) > 2:
            analysis.append("⚠️ 碳水化合物偏多，建议适当减少主食量，增加蔬菜比例")
        if not has_fruit:
            analysis.append("💡 建议每天摄入 1-2 份水果，补充维生素和纤维素")

        if not analysis:
            return "✅ 饮食结构均衡！继续保持多样化饮食，注意控制总热量摄入。"

        return "\n".join(analysis)

    @classmethod
    def get_recipe_recommendation(
        cls, user_profile: Dict, preferences: Optional[str] = None
    ) -> str:
        """推荐食谱"""
        # 根据用户偏好推荐
        recipes = {
            "breakfast": [
                "燕麦粥 + 鸡蛋 + 牛奶 + 水果（约 350 卡路里）",
                "全麦面包 + 煎蛋 + 酸奶 + 坚果（约 400 卡路里）",
                "豆浆 + 杂粮包子 + 凉拌蔬菜（约 380 卡路里）",
            ],
            "lunch": [
                "糙米饭 + 清蒸鱼 + 炒青菜 + 豆腐汤（约 500 卡路里）",
                "鸡胸肉沙拉 + 红薯 + 橄榄油调味（约 450 卡路里）",
                "荞麦面 + 虾仁 + 蔬菜炒蛋（约 480 卡路里）",
            ],
            "dinner": [
                "瘦肉粥 + 蒸蔬菜 + 凉拌豆腐（约 400 卡路里）",
                "烤鱼 + 烤蔬菜 + 少量糙米（约 450 卡路里）",
                "鸡胸肉 + 西兰花 + 蘑菇汤（约 380 卡路里）",
            ],
        }

        return f"""🍽️ **今日食谱推荐**

**早餐:** {random.choice(recipes["breakfast"])}
**午餐:** {random.choice(recipes["lunch"])}
**晚餐:** {random.choice(recipes["dinner"])}

💡 **营养提示:**
- 每日建议摄入：蛋白质 1.2-1.6g/kg 体重
- 蔬菜摄入：每天至少 500g
- 水分摄入：每天 2000-2500ml
- 少食多餐，避免暴饮暴食"""

    @classmethod
    def calculate_nutrition_goals(cls, user_profile: Dict) -> Dict[str, Any]:
        """计算营养目标"""
        weight = user_profile.get("weight", 70)  # kg
        height = user_profile.get("height", 170)  # cm
        age = user_profile.get("age", 30)
        gender = user_profile.get("gender", "male")
        activity_level = user_profile.get("activity_level", "moderate")

        # 计算 BMR (Mifflin-St Jeor 公式)
        if gender == "male":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        # 计算 TDEE
        activity_multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9,
        }
        tdee = bmr * activity_multipliers.get(activity_level, 1.55)

        # 营养目标
        protein = weight * 1.5  # 1.5g per kg
        fat = weight * 0.9  # 0.9g per kg
        carbs = (tdee - (protein * 4 + fat * 9)) / 4  # remaining calories

        return {
            "bmr": round(bmr, 2),
            "tdee": round(tdee, 2),
            "daily_calories": round(tdee, 0),
            "protein_g": round(protein, 1),
            "fat_g": round(fat, 1),
            "carbs_g": round(carbs, 1),
            "water_ml": 2500,
        }

    @classmethod
    def get_today_intake_summary(cls, db: Any, user_id: int) -> Optional[str]:
        """
        获取用户今日摄入热量摘要

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            摄入摘要字符串，如果没有记录返回 None
        """
        try:
            from app.models.nutrition import Meal
            from app.models.exercise_checkin import ExerciseCheckIn
            from datetime import date

            # 查询今天的所有餐食
            today_meals = (
                db.query(Meal)
                .filter(
                    Meal.user_id == user_id,
                    func.date(Meal.meal_datetime) == date.today(),
                )
                .all()
            )

            total_calories = sum(meal.calories or 0 for meal in today_meals)

            if total_calories > 0:
                meal_count = len(today_meals)

                # 构建详细摘要
                summary_parts = [
                    f"📊 **您今天摄入了 {total_calories} 千卡**",
                    f"共 {meal_count} 餐",
                ]

                # 按餐类型统计
                meal_types = {}
                for meal in today_meals:
                    mtype = meal.meal_type or "unknown"
                    meal_types[mtype] = meal_types.get(mtype, 0) + (meal.calories or 0)

                type_map = {
                    "breakfast": "早餐",
                    "lunch": "午餐",
                    "dinner": "晚餐",
                    "snack": "加餐",
                }

                for mtype, calories in meal_types.items():
                    cn_type = type_map.get(mtype, mtype)
                    summary_parts.append(f"- {cn_type}: {calories} 千卡")

                return "\n".join(summary_parts)

            return None

        except Exception as e:
            logger.warning("Failed to get today's intake", error=str(e))
            return None


class BehaviorCoachRole:
    """行为教练角色 - 提供习惯养成和行为改变指导"""

    # 行为教练角色设定
    ROLE_PROMPT = """你是一位专业的行为教练，专注于习惯养成和行为改变。
你的职责：
1. 帮助用户建立健康的生活习惯
2. 提供行为改变策略和技巧
3. 设定可实现的小目标
4. 提供积极反馈和鼓励
5. 基于行为科学原理（如原子习惯、习惯回路）提供建议

请使用积极、鼓励性的语言，强调进步而非完美。"""

    @classmethod
    def get_habit_advice(cls, habit_type: str, current_status: str) -> str:
        """提供习惯建议"""
        advice_templates = {
            "exercise": [
                "🎯 **从小目标开始**: 不要一开始就设定每天运动 1 小时的目标。从每天 5-10 分钟开始，逐渐增加。",
                "⏰ **固定时间**: 选择每天固定的时间运动，比如早起后或下班后，让身体形成生物钟。",
                "👥 **找伙伴**: 和朋友一起运动，互相监督，增加坚持的动力。",
                "📊 **记录进展**: 每次运动后打卡记录，看到自己的进步会更有成就感。",
            ],
            "diet": [
                "🍽️ **环境设计**: 把健康食物放在容易拿到的地方，把不健康食物藏起来或不买。",
                "🥗 **替代策略**: 想吃零食时，先喝一杯水或吃一个水果。",
                "📝 **饮食记录**: 每天记录吃了什么，增强意识，避免无意识进食。",
                "⏲️ **定时进餐**: 固定三餐时间，避免过度饥饿导致暴食。",
            ],
            "sleep": [
                "🌙 **建立睡前仪式**: 睡前 1 小时远离电子屏幕，可以看书、冥想或泡个热水澡。",
                "⏰ **固定作息**: 每天同一时间上床和起床，即使是周末。",
                "🛏️ **优化环境**: 保持卧室黑暗、安静、凉爽，使用舒适的床品。",
                "☕ **限制咖啡因**: 下午 2 点后避免摄入咖啡因。",
            ],
            "general": [
                "🎯 **两分钟规则**: 新习惯开始时，让它简单到两分钟内就能完成。",
                "🔗 **习惯叠加**: 把新习惯和已有习惯绑定，比如'刷牙后冥想 1 分钟'。",
                "📈 **关注系统而非目标**: 不要只盯着目标，要专注于每天的小行动。",
                "💪 **接受不完美**: 偶尔中断没关系，关键是尽快回到轨道上。",
            ],
        }

        habits = advice_templates.get(habit_type, advice_templates["general"])
        return "\n\n".join(habits)

    @classmethod
    def provide_encouragement(cls, achievement: str, streak_days: int = 0) -> str:
        """提供鼓励和反馈"""
        if streak_days >= 30:
            return f"""🎉 **太棒了！您已经坚持了{streak_days}天！**

这是一个了不起的成就！{achievement}

**您的进步:**
✅ 已经形成了稳定的习惯回路
✅ 自律能力显著提升
✅ 离目标更近了一大步

**继续保持:**
- 庆祝每一个小胜利
- 回顾初心，记住为什么开始
- 挑战自己，设定新目标

您真的很优秀！继续加油！💪"""

        elif streak_days >= 7:
            return f"""👏 **恭喜！您已经坚持了{streak_days}天！**

{achievement}

**一周的坚持证明了您的决心！**

**下一步建议:**
- 继续保持这个节奏
- 可以尝试稍微增加难度
- 记录自己的感受和变化

您已经走在成功的路上了！🌟"""

        elif streak_days >= 1:
            return f"""✨ **很棒！您已经坚持了{streak_days}天！**

{achievement}

**良好的开端！**

**小建议:**
- 设定提醒，帮助自己记住
- 找一个 accountability partner（监督伙伴）
- 每晚回顾今天的进步

继续保持，您会看到惊人的变化！🚀"""

        else:
            return f"""🌱 **新的开始总是令人兴奋！**

{achievement}

**第一步最重要！**

**开始建议:**
1. 设定一个超小的目标（小到不可能失败）
2. 选择一个固定的触发点（比如'早餐后'）
3. 准备好环境（提前准备好运动装备等）

相信自己，您可以做到！我会一直支持您！💖"""

    @classmethod
    def handle_setback(cls, user_concern: str) -> str:
        """处理挫折和困难"""
        return f"""我理解您的感受。{user_concern}

**请记住:**

🌟 **挫折是过程的一部分**
- 每个人都会遇到低谷期
- 重要的是如何重新开始
- 一次失误不等于失败

💡 **应对策略:**

1. **接受情绪**: 允许自己感到沮丧，但不要沉浸其中
2. **分析原因**: 是什么导致了中断？如何避免下次发生？
3. **降低难度**: 如果目标太难，就调低一些
4. **寻求支持**: 和朋友聊聊，或者在这里和我交流
5. **立即重启**: 不要等"明天"或"下周一"，从现在开始

**记住:**
> "成功不是从不跌倒，而是每次跌倒后都能站起来。"

您已经走了这么远，这本身就证明了您的能力。
相信自己，您可以重新开始的！我会一直在这里支持您！💪❤️"""

    @classmethod
    def set_micro_goals(cls, main_goal: str) -> List[str]:
        """将大目标分解为微小目标"""
        goal_breakdowns = {
            "减肥": [
                "第 1 周：每天记录饮食，不改变任何习惯",
                "第 2 周：每天多喝一杯水",
                "第 3 周：每天增加 10 分钟散步",
                "第 4 周：晚餐减少 1/4 主食",
                "第 5-8 周：保持以上习惯，观察体重变化",
            ],
            "增肌": [
                "第 1 周：每天做 5 个俯卧撑",
                "第 2 周：增加到每天 10 个",
                "第 3 周：加入深蹲，每天 10 个",
                "第 4 周：购买哑铃，开始力量训练",
                "第 5-8 周：逐步增加训练强度",
            ],
            "健康饮食": [
                "第 1 天：早餐加一份水果",
                "第 2 天：午餐加一份蔬菜",
                "第 3 天：晚餐减少一半主食",
                "第 4 天：用白开水代替含糖饮料",
                "第 5-7 天：保持以上习惯",
                "第 2 周：开始记录每日营养摄入",
            ],
        }

        for key, breakdown in goal_breakdowns.items():
            if key in main_goal:
                return breakdown

        # 通用分解
        return [
            "第 1 步：明确具体目标（要具体、可衡量）",
            "第 2 步：分解为每周小目标",
            "第 3 步：设定每日微行动（2 分钟内完成）",
            "第 4 步：建立触发机制（固定时间/地点）",
            "第 5 步：记录和庆祝进步",
        ]


class EmotionalSupportRole:
    """情感陪伴角色 - 提供情绪支持和心理疏导"""

    ROLE_PROMPT = """你是一位温暖的情感陪伴者，专注于情绪支持和心理疏导。
你的职责：
1. 倾听用户的烦恼和压力
2. 提供情感支持和理解
3. 给予积极的鼓励和肯定
4. 帮助缓解焦虑和压力
5. 引导用户看到积极的一面

请使用温暖、共情的语言，让用户感到被理解和被支持。"""

    @classmethod
    def provide_support(cls, emotion: str, context: Optional[str] = None) -> str:
        """提供情感支持"""
        support_messages = {
            "sad": """我感受到您现在的难过。😔

{{context}}

请允许自己感受这些情绪，它们都是正常的。
有时候，生活确实会给我们带来挑战和困难。

**我想告诉您:**
- 您的感受是重要的
- 您并不孤单，我在这里陪着您
- 这些情绪会过去的，就像天空中的云

**如果可以:**
- 和朋友或家人聊聊
- 写日记记录感受
- 做一些让自己舒服的事情

您已经很坚强了。给自己一些时间和空间，一切都会好起来的。💕""",
            "anxious": """我能感受到您的焦虑。😰

{{context}}

焦虑是身体在提醒我们有些事情需要关注。
但请不要让焦虑控制您。

**深呼吸练习:**
1. 慢慢吸气 4 秒
2. 屏住呼吸 4 秒
3. 慢慢呼气 6 秒
4. 重复 5 次

**记住:**
- 您已经在尽力了
- 一次只关注一件事
- 您比您想象的更坚强

我会一直在这里支持您。🌸""",
            "frustrated": """我能理解您的挫败感。😤

{{context}}

付出努力却没有看到预期的结果，确实很让人沮丧。

**但是请记住:**
- 进步往往是看不见的，但它在发生
- 每一次尝试都是宝贵的经验
- 您比自己想象的更接近成功

**建议:**
- 休息一下，给自己充充电
- 回顾一下已经取得的进步
- 调整策略，但不放弃目标

您真的很棒，不要放弃！💪""",
            "tired": """我能感受到您的疲惫。😴

{{context}}

体重管理的旅程确实需要持续的精力和耐心。
累了就休息，这是完全正常的。

**请允许自己:**
- 好好睡一觉
- 暂时放下目标，放松一下
- 做一些让自己开心的事情

**记住:**
休息不是放弃，而是为了走更远的路。

照顾好自己，您值得被温柔对待。💖""",
            "default": """感谢您和我分享这些。😊

{{context}}

我想告诉您：
- 您的每一步努力都是有意义的
- 您值得拥有健康和快乐
- 我会一直在这里支持您

如果有什么想说的，我随时都在这里倾听。🌼""",
        }

        message = support_messages.get(emotion, support_messages["default"])
        context_text = f'"{context}"' if context else ""
        return message.replace("{{context}}", context_text)

    @classmethod
    def daily_affirmation(cls) -> str:
        """提供每日积极肯定"""
        affirmations = [
            "✨ **今日肯定:** 我正在成为更好的自己，每一天都在进步。",
            "🌟 **今日肯定:** 我值得拥有健康和快乐，我正在为之努力。",
            "💪 **今日肯定:** 我有能力克服任何挑战，我比想象中更强大。",
            "🌈 **今日肯定:** 我接纳自己的不完美，我正在用心改变。",
            "🎯 **今日肯定:** 我的每一个小行动都在塑造更好的自己。",
            "💖 **今日肯定:** 我爱自己，包括现在的自己和未来的自己。",
            "🌱 **今日肯定:** 成长需要时间，我对自己有耐心。",
        ]

        return random.choice(affirmations)


# 角色服务工厂
ROLE_SERVICES = {
    "nutritionist": NutritionistRole,
    "behavior_coach": BehaviorCoachRole,
    "emotional_support": EmotionalSupportRole,
    "general": None,
}


def get_role_service(role: str):
    """获取角色服务"""
    return ROLE_SERVICES.get(role, None)
