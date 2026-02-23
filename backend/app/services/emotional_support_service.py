import random
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

import structlog
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.models.emotional_support import (
    EmotionalState,
    EmotionalSupport,
    EmotionType,
    GratitudeJournal,
    MindfulnessExercise,
    PositiveAffirmation,
    StressLevel,
    SupportType,
)
from app.models.user import User
from app.schemas.emotional_support import (
    CopingStrategy,
    DailyEmotionalSummary,
    EmotionalCheckIn,
    EmotionalInsight,
    EmotionalStateCreate,
    EmotionalSupportCreate,
    EmotionalWellnessPlan,
    GratitudeJournalCreate,
    MindfulnessExerciseCreate,
    PositiveAffirmationCreate,
    StressLevelCreate,
    SupportRecommendation,
)

logger = structlog.get_logger()


class EmotionalSupportService:
    """情感支持服务"""

    def __init__(self, db: Session):
        self.db = db

    # ========== 情感状态管理 ==========

    def record_emotional_state(
        self, user: User, state_data: EmotionalStateCreate
    ) -> EmotionalState:
        """记录情感状态"""
        logger.info("Recording emotional state", user_id=user.id)

        emotional_state = EmotionalState(
            user_id=user.id,
            emotion_type=state_data.emotion_type,
            intensity=state_data.intensity,
            description=state_data.description,
            trigger=state_data.trigger,
            context=state_data.context,
            recorded_at=state_data.recorded_at,
        )

        self.db.add(emotional_state)
        self.db.commit()
        self.db.refresh(emotional_state)

        logger.info(
            "Emotional state recorded",
            state_id=emotional_state.id,
            emotion=emotional_state.emotion_type.value,
        )

        return emotional_state

    def get_emotional_states(
        self,
        user: User,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        emotion_type: Optional[EmotionType] = None,
    ) -> List[EmotionalState]:
        """获取情感状态记录"""
        query = self.db.query(EmotionalState).filter(EmotionalState.user_id == user.id)

        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            query = query.filter(EmotionalState.recorded_at >= start_datetime)

        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            query = query.filter(EmotionalState.recorded_at <= end_datetime)

        if emotion_type:
            query = query.filter(EmotionalState.emotion_type == emotion_type)

        states = query.order_by(EmotionalState.recorded_at.desc()).all()

        logger.debug(
            "Retrieved emotional states",
            user_id=user.id,
            count=len(states),
        )

        return states

    # ========== 情感支持生成 ==========

    def provide_emotional_support(
        self,
        user: User,
        emotion_type: EmotionType,
        intensity: int,
        context: Optional[str] = None,
    ) -> SupportRecommendation:
        """提供情感支持建议"""
        logger.info(
            "Providing emotional support",
            user_id=user.id,
            emotion=emotion_type.value,
            intensity=intensity,
        )

        # 根据情感类型和强度选择支持策略
        support_strategy = self._select_support_strategy(emotion_type, intensity)

        # 生成个性化消息
        message = self._generate_support_message(
            emotion_type, intensity, context, support_strategy
        )

        # 生成建议行动
        suggested_actions = self._generate_suggested_actions(
            emotion_type, intensity, support_strategy
        )

        # 提供资源
        resources = self._get_support_resources(support_strategy)

        recommendation = SupportRecommendation(
            support_type=support_strategy,
            message=message,
            rationale=self._get_strategy_rationale(support_strategy),
            suggested_actions=suggested_actions,
            resources=resources,
        )

        # 记录支持提供
        self._record_support_provided(user, recommendation)

        return recommendation

    def _select_support_strategy(
        self, emotion_type: EmotionType, intensity: int
    ) -> SupportType:
        """选择支持策略"""
        # 基于情感类型和强度的策略映射
        strategy_map = {
            EmotionType.SAD: {
                "low": SupportType.VALIDATION,
                "medium": SupportType.SELF_COMPASSION,
                "high": SupportType.ENCOURAGEMENT,
            },
            EmotionType.ANXIOUS: {
                "low": SupportType.MINDFULNESS,
                "medium": SupportType.PROBLEM_SOLVING,
                "high": SupportType.MINDFULNESS,
            },
            EmotionType.STRESSED: {
                "low": SupportType.MINDFULNESS,
                "medium": SupportType.PROBLEM_SOLVING,
                "high": SupportType.PERSPECTIVE_SHIFT,
            },
            EmotionType.FRUSTRATED: {
                "low": SupportType.VALIDATION,
                "medium": SupportType.PROBLEM_SOLVING,
                "high": SupportType.PERSPECTIVE_SHIFT,
            },
            EmotionType.TIRED: {
                "low": SupportType.SELF_COMPASSION,
                "medium": SupportType.ENCOURAGEMENT,
                "high": SupportType.VALIDATION,
            },
            EmotionType.HAPPY: {
                "low": SupportType.GRATITUDE,
                "medium": SupportType.GRATITUDE,
                "high": SupportType.ENCOURAGEMENT,
            },
            EmotionType.MOTIVATED: {
                "low": SupportType.ENCOURAGEMENT,
                "medium": SupportType.ENCOURAGEMENT,
                "high": SupportType.ENCOURAGEMENT,
            },
            EmotionType.PEACEFUL: {
                "low": SupportType.GRATITUDE,
                "medium": SupportType.MINDFULNESS,
                "high": SupportType.GRATITUDE,
            },
            EmotionType.NEUTRAL: {
                "low": SupportType.GRATITUDE,
                "medium": SupportType.MINDFULNESS,
                "high": SupportType.SELF_COMPASSION,
            },
        }

        # 确定强度级别
        intensity_level = (
            "low" if intensity <= 3 else "medium" if intensity <= 7 else "high"
        )

        return strategy_map.get(emotion_type, {}).get(
            intensity_level, SupportType.VALIDATION
        )

    def _generate_support_message(
        self,
        emotion_type: EmotionType,
        intensity: int,
        context: Optional[str],
        strategy: SupportType,
    ) -> str:
        """生成支持消息"""
        # 消息模板库
        message_templates = {
            SupportType.ENCOURAGEMENT: [
                "我理解你现在可能感到{emotion}，但请记住你已经走了这么远。",
                "每个挑战都是成长的机会，我相信你能处理好这个情况。",
                "你比想象中更坚强，今天的小进步也是值得庆祝的。",
            ],
            SupportType.VALIDATION: [
                "感到{emotion}是完全正常的，你的感受是有效的。",
                "在这种情况下感到{emotion}是可以理解的，很多人都会有类似的感受。",
                "承认自己的感受是勇敢的表现，你不需要为感到{emotion}而自责。",
            ],
            SupportType.PROBLEM_SOLVING: [
                "让我们一起来分析这个情况，找到可行的解决方案。",
                "有时候把问题分解成小步骤会更容易处理。",
                "你之前成功应对过类似的情况，这次也可以。",
            ],
            SupportType.MINDFULNESS: [
                "试着关注当下的感受，不做评判地观察它们。",
                "深呼吸几次，让身体和心灵都放松下来。",
                "感受身体的感觉，让思绪像云朵一样飘过。",
            ],
            SupportType.GRATITUDE: [
                "即使在困难时刻，也总有一些值得感恩的小事。",
                "回想今天让你感到温暖或感激的三个瞬间。",
                "感恩练习可以帮助我们重新聚焦于积极的事物。",
            ],
            SupportType.PERSPECTIVE_SHIFT: [
                "换个角度看这个问题，也许会有新的发现。",
                "这个问题在一年后还会这么重要吗？",
                "每个困难都包含着学习和成长的机会。",
            ],
            SupportType.SELF_COMPASSION: [
                "对自己温柔一些，就像对待好朋友一样。",
                "你正在尽力做到最好，这就足够了。",
                "允许自己休息和恢复，这不是软弱的表现。",
            ],
        }

        # 获取情感描述
        emotion_descriptions = {
            EmotionType.HAPPY: "开心",
            EmotionType.SAD: "难过",
            EmotionType.ANXIOUS: "焦虑",
            EmotionType.STRESSED: "压力大",
            EmotionType.MOTIVATED: "有动力",
            EmotionType.TIRED: "疲惫",
            EmotionType.FRUSTRATED: "沮丧",
            EmotionType.PEACEFUL: "平静",
            EmotionType.NEUTRAL: "平静",
        }

        emotion_desc = emotion_descriptions.get(emotion_type, "这样")

        # 选择模板并填充
        templates = message_templates.get(strategy, ["我在这里支持你。"])
        template = random.choice(templates)
        message = template.format(emotion=emotion_desc)

        # 添加上下文相关的内容
        if context:
            message += f" 关于'{context}'，我们可以一起找到应对方法。"

        return message

    def _generate_suggested_actions(
        self, emotion_type: EmotionType, intensity: int, strategy: SupportType
    ) -> List[str]:
        """生成建议行动"""
        actions_by_strategy = {
            SupportType.ENCOURAGEMENT: [
                "写下你今天做得好的三件事",
                "给自己一个小小的奖励",
                "回想过去成功克服困难的经历",
            ],
            SupportType.VALIDATION: [
                "在日记中写下你的感受",
                "对自己说'我的感受是合理的'",
                "与信任的人分享你的感受",
            ],
            SupportType.PROBLEM_SOLVING: [
                "把问题写在纸上，分析可能的解决方案",
                "制定一个简单的行动计划",
                "寻求他人的建议或帮助",
            ],
            SupportType.MINDFULNESS: [
                "进行5分钟的深呼吸练习",
                "关注身体的感受，从头到脚扫描一遍",
                "观察周围的环境，注意五个你能看到的事物",
            ],
            SupportType.GRATITUDE: [
                "写下三件你今天感恩的事情",
                "感谢一个帮助过你的人",
                "关注生活中美好的小细节",
            ],
            SupportType.PERSPECTIVE_SHIFT: [
                "从不同角度思考这个问题",
                "想象给朋友同样的建议",
                "考虑这个问题在更大图景中的位置",
            ],
            SupportType.SELF_COMPASSION: [
                "对自己说一些温暖鼓励的话",
                "做一些让自己感到舒适的事情",
                "允许自己休息，不需要完美",
            ],
        }

        return actions_by_strategy.get(strategy, ["休息一下，照顾自己"])

    def _get_support_resources(self, strategy: SupportType) -> List[str]:
        """获取支持资源"""
        resources = {
            SupportType.MINDFULNESS: [
                "正念冥想引导音频",
                "呼吸练习教程",
                "身体扫描练习指南",
            ],
            SupportType.PROBLEM_SOLVING: [
                "问题解决工作表",
                "决策矩阵模板",
                "目标设定指南",
            ],
            SupportType.GRATITUDE: [
                "感恩日记模板",
                "感恩练习提示",
                "积极心理学资源",
            ],
        }

        return resources.get(strategy, ["情感支持热线", "心理咨询资源"])

    def _get_strategy_rationale(self, strategy: SupportType) -> str:
        """获取策略理由"""
        rationales = {
            SupportType.ENCOURAGEMENT: "鼓励可以帮助建立信心和韧性",
            SupportType.VALIDATION: "情感验证有助于情绪调节和自我接纳",
            SupportType.PROBLEM_SOLVING: "结构化的问题解决方法可以减少无助感",
            SupportType.MINDFULNESS: "正念练习可以帮助情绪调节和压力管理",
            SupportType.GRATITUDE: "感恩练习可以提升积极情绪和幸福感",
            SupportType.PERSPECTIVE_SHIFT: "视角转换可以减少认知扭曲",
            SupportType.SELF_COMPASSION: "自我同情可以减轻自我批评和压力",
        }

        return rationales.get(strategy, "这个策略基于积极心理学和认知行为疗法")

    def _record_support_provided(
        self, user: User, recommendation: SupportRecommendation
    ) -> None:
        """记录支持提供"""
        support = EmotionalSupport(
            user_id=user.id,
            support_type=recommendation.support_type,
            message=recommendation.message,
            suggested_action=", ".join(recommendation.suggested_actions),
            resources=", ".join(recommendation.resources),
            provided_at=datetime.utcnow(),
        )

        self.db.add(support)
        self.db.commit()

        logger.info(
            "Emotional support recorded",
            user_id=user.id,
            support_type=recommendation.support_type.value,
        )

    # ========== 压力管理 ==========

    def record_stress_level(
        self, user: User, stress_data: StressLevelCreate
    ) -> StressLevel:
        """记录压力水平"""
        logger.info("Recording stress level", user_id=user.id)

        stress_level = StressLevel(
            user_id=user.id,
            stress_level=stress_data.stress_level,
            physical_symptoms=stress_data.physical_symptoms,
            emotional_symptoms=stress_data.emotional_symptoms,
            cognitive_symptoms=stress_data.cognitive_symptoms,
            stressors=stress_data.stressors,
            coping_strategies=stress_data.coping_strategies,
            recorded_at=stress_data.recorded_at,
        )

        self.db.add(stress_level)
        self.db.commit()
        self.db.refresh(stress_level)

        logger.info(
            "Stress level recorded",
            stress_id=stress_level.id,
            level=stress_level.stress_level,
        )

        return stress_level

    def get_stress_trend(self, user: User, days: int = 7) -> List[Dict]:
        """获取压力趋势"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)

        stress_levels = (
            self.db.query(StressLevel)
            .filter(
                and_(
                    StressLevel.user_id == user.id,
                    StressLevel.recorded_at
                    >= datetime.combine(start_date, datetime.min.time()),
                    StressLevel.recorded_at
                    <= datetime.combine(end_date, datetime.max.time()),
                )
            )
            .order_by(StressLevel.recorded_at.asc())
            .all()
        )

        trend = []
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            daily_levels = [
                sl for sl in stress_levels if sl.recorded_at.date() == current_date
            ]

            if daily_levels:
                avg_level = sum(sl.stress_level for sl in daily_levels) / len(
                    daily_levels
                )
                trend.append(
                    {
                        "date": current_date.isoformat(),
                        "stress_level": round(avg_level, 1),
                        "record_count": len(daily_levels),
                    }
                )
            else:
                trend.append(
                    {
                        "date": current_date.isoformat(),
                        "stress_level": None,
                        "record_count": 0,
                    }
                )

        return trend

    def get_coping_strategies(self, stress_level: int) -> List[CopingStrategy]:
        """获取应对策略"""
        strategies = []

        if stress_level <= 3:
            strategies = [
                CopingStrategy(
                    name="深呼吸练习",
                    description="简单的4-7-8呼吸法，帮助放松",
                    category="放松技巧",
                    duration_minutes=5,
                    difficulty="简单",
                    effectiveness_rating=4.2,
                ),
                CopingStrategy(
                    name="感恩记录",
                    description="写下三件感恩的事情",
                    category="积极心理学",
                    duration_minutes=3,
                    difficulty="简单",
                    effectiveness_rating=4.5,
                ),
            ]
        elif stress_level <= 7:
            strategies = [
                CopingStrategy(
                    name="正念冥想",
                    description="引导式冥想，关注当下",
                    category="正念练习",
                    duration_minutes=10,
                    difficulty="中等",
                    effectiveness_rating=4.7,
                ),
                CopingStrategy(
                    name="问题分解",
                    description="将大问题分解为可管理的小步骤",
                    category="问题解决",
                    duration_minutes=15,
                    difficulty="中等",
                    effectiveness_rating=4.3,
                ),
            ]
        else:
            strategies = [
                CopingStrategy(
                    name="渐进式肌肉放松",
                    description="系统地放松身体各部位",
                    category="放松技巧",
                    duration_minutes=20,
                    difficulty="中等",
                    effectiveness_rating=4.8,
                ),
                CopingStrategy(
                    name="认知重构",
                    description="识别和挑战负面思维模式",
                    category="认知行为",
                    duration_minutes=15,
                    difficulty="困难",
                    effectiveness_rating=4.6,
                ),
            ]

        return strategies

    # ========== 感恩日记 ==========

    def record_gratitude(
        self, user: User, gratitude_data: GratitudeJournalCreate
    ) -> GratitudeJournal:
        """记录感恩日记"""
        logger.info("Recording gratitude journal", user_id=user.id)

        gratitude_journal = GratitudeJournal(
            user_id=user.id,
            entry=gratitude_data.entry,
            category=gratitude_data.category,
            intensity=gratitude_data.intensity,
            mood_before=gratitude_data.mood_before,
            mood_after=gratitude_data.mood_after,
            recorded_at=gratitude_data.recorded_at,
        )

        self.db.add(gratitude_journal)
        self.db.commit()
        self.db.refresh(gratitude_journal)

        logger.info("Gratitude journal recorded", journal_id=gratitude_journal.id)

        return gratitude_journal

    def get_gratitude_prompts(self) -> List[str]:
        """获取感恩提示"""
        prompts = [
            "今天有什么小事让你感到温暖？",
            "你感谢自己的哪些品质或努力？",
            "谁的支持或善意让你感激？",
            "身体健康的哪些方面让你感恩？",
            "生活中有什么便利或舒适让你感激？",
            "自然中的什么美景让你感到愉悦？",
            "今天学到了什么有价值的东西？",
            "有什么挑战让你成长和感激？",
            "你拥有哪些物质或非物质财富？",
            "未来有什么让你期待和感恩？",
        ]

        return random.sample(prompts, 3)

    # ========== 积极肯定语 ==========

    def get_positive_affirmations(
        self, user: User, category: Optional[str] = None, count: int = 3
    ) -> List[PositiveAffirmation]:
        """获取积极肯定语"""
        query = self.db.query(PositiveAffirmation).filter(
            PositiveAffirmation.user_id == user.id
        )

        if category:
            query = query.filter(PositiveAffirmation.category == category)

        affirmations = query.order_by(func.random()).limit(count).all()

        # 如果用户没有足够的个性化肯定语，添加通用肯定语
        if len(affirmations) < count:
            generic_affirmations = self._get_generic_affirmations(
                category, count - len(affirmations)
            )
            affirmations.extend(generic_affirmations)

        # 更新使用次数
        for affirmation in affirmations:
            if hasattr(affirmation, "id"):  # 只更新数据库中已有的
                affirmation.times_used += 1
                affirmation.last_used = datetime.utcnow()

        self.db.commit()

        return affirmations

    def _get_generic_affirmations(
        self, category: Optional[str], count: int
    ) -> List[PositiveAffirmation]:
        """获取通用肯定语"""
        affirmations_by_category = {
            "health": [
                "我的身体值得被关爱和尊重",
                "我选择滋养身心的食物和活动",
                "我的健康之旅是独特而有价值的",
                "我每天都在变得更健康、更强壮",
                "我倾听身体的需求并给予回应",
            ],
            "self_worth": [
                "我足够好，值得被爱和尊重",
                "我的价值不取决于外在成就",
                "我接纳自己的不完美",
                "我为自己感到骄傲",
                "我值得幸福和成功",
            ],
            "growth": [
                "每个挑战都是成长的机会",
                "我每天都在学习和进步",
                "我有能力克服困难",
                "我的潜力是无限的",
                "我拥抱变化和新的可能性",
            ],
            "default": [
                "今天会是美好的一天",
                "我有能力处理遇到的任何情况",
                "我选择关注积极的事物",
                "我对自己和他人充满善意",
                "我相信一切都会好起来",
            ],
        }

        category_key = category if category in affirmations_by_category else "default"
        affirmations_list = affirmations_by_category[category_key]

        selected = random.sample(affirmations_list, min(count, len(affirmations_list)))

        # 创建临时对象（不在数据库中）
        return [
            PositiveAffirmation(
                affirmation=text,
                category=category_key,
                personalized=False,
                times_used=0,
            )
            for text in selected
        ]

    # ========== 正念练习 ==========

    def record_mindfulness_exercise(
        self, user: User, exercise_data: MindfulnessExerciseCreate
    ) -> MindfulnessExercise:
        """记录正念练习"""
        logger.info("Recording mindfulness exercise", user_id=user.id)

        exercise = MindfulnessExercise(
            user_id=user.id,
            exercise_type=exercise_data.exercise_type,
            duration_minutes=exercise_data.duration_minutes,
            focus_area=exercise_data.focus_area,
            difficulty_level=exercise_data.difficulty_level,
            relaxation_level=exercise_data.relaxation_level,
            focus_level=exercise_data.focus_level,
            notes=exercise_data.notes,
            completed_at=exercise_data.completed_at,
        )

        self.db.add(exercise)
        self.db.commit()
        self.db.refresh(exercise)

        logger.info(
            "Mindfulness exercise recorded",
            exercise_id=exercise.id,
            type=exercise.exercise_type,
        )

        return exercise

    def get_mindfulness_exercises(self, duration: Optional[int] = None) -> List[Dict]:
        """获取正念练习建议"""
        exercises = [
            {
                "name": "呼吸觉察",
                "description": "专注于呼吸的进出，不做评判",
                "duration": 5,
                "difficulty": "简单",
                "instructions": "舒适地坐着，关注呼吸的自然流动",
            },
            {
                "name": "身体扫描",
                "description": "系统地关注身体各部位的感觉",
                "duration": 10,
                "difficulty": "中等",
                "instructions": "从头顶开始，逐渐向下扫描身体的感受",
            },
            {
                "name": "慈心冥想",
                "description": "培养对自己和他人的善意",
                "duration": 15,
                "difficulty": "中等",
                "instructions": "重复慈心短语，扩展善意范围",
            },
            {
                "name": "行走冥想",
                "description": "在行走中保持正念",
                "duration": 10,
                "difficulty": "简单",
                "instructions": "缓慢行走，关注脚步和身体的感觉",
            },
            {
                "name": "声音冥想",
                "description": "关注环境中的声音",
                "duration": 8,
                "difficulty": "简单",
                "instructions": "倾听周围的声音，不做评判",
            },
        ]

        if duration:
            exercises = [e for e in exercises if e["duration"] <= duration]

        return exercises

    # ========== 情感洞察和分析 ==========

    def get_emotional_insights(self, user: User, days: int = 30) -> EmotionalInsight:
        """获取情感洞察"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)

        # 获取情感状态数据
        emotional_states = self.get_emotional_states(user, start_date, end_date)

        # 计算情感趋势
        emotion_counts = {}
        total_intensity = 0
        for state in emotional_states:
            emotion = state.emotion_type.value
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            total_intensity += state.intensity

        # 确定主导情感
        dominant_emotion = (
            max(emotion_counts.items(), key=lambda x: x[1])[0]
            if emotion_counts
            else EmotionType.NEUTRAL.value
        )

        # 获取压力趋势
        stress_trend_data = self.get_stress_trend(user, days)
        stress_trend = [day["stress_level"] or 0 for day in stress_trend_data]
        avg_stress_level = (
            sum(s for s in stress_trend if s > 0)
            / len([s for s in stress_trend if s > 0])
            if any(s > 0 for s in stress_trend)
            else 0
        )

        # 获取感恩频率
        gratitude_count = (
            self.db.query(GratitudeJournal)
            .filter(
                and_(
                    GratitudeJournal.user_id == user.id,
                    GratitudeJournal.recorded_at
                    >= datetime.combine(start_date, datetime.min.time()),
                    GratitudeJournal.recorded_at
                    <= datetime.combine(end_date, datetime.max.time()),
                )
            )
            .count()
        )

        # 获取正念练习次数
        mindfulness_count = (
            self.db.query(MindfulnessExercise)
            .filter(
                and_(
                    MindfulnessExercise.user_id == user.id,
                    MindfulnessExercise.completed_at
                    >= datetime.combine(start_date, datetime.min.time()),
                    MindfulnessExercise.completed_at
                    <= datetime.combine(end_date, datetime.max.time()),
                )
            )
            .count()
        )

        # 计算应对策略有效性（简化版）
        coping_effectiveness = 0.7  # 默认值，实际应该基于用户反馈计算

        return EmotionalInsight(
            emotion_trend=emotion_counts,
            dominant_emotion=EmotionType(dominant_emotion),
            stress_trend=stress_trend,
            avg_stress_level=round(avg_stress_level, 1),
            coping_effectiveness=round(coping_effectiveness, 2),
            gratitude_frequency=gratitude_count,
            mindfulness_practice=mindfulness_count,
        )

    def get_daily_emotional_summary(
        self, user: User, target_date: date
    ) -> DailyEmotionalSummary:
        """获取每日情感总结"""
        emotional_states = self.get_emotional_states(user, target_date, target_date)

        stress_levels = (
            self.db.query(StressLevel)
            .filter(
                and_(
                    StressLevel.user_id == user.id,
                    StressLevel.recorded_at
                    >= datetime.combine(target_date, datetime.min.time()),
                    StressLevel.recorded_at
                    <= datetime.combine(target_date, datetime.max.time()),
                )
            )
            .all()
        )

        gratitude_entries = (
            self.db.query(GratitudeJournal)
            .filter(
                and_(
                    GratitudeJournal.user_id == user.id,
                    GratitudeJournal.recorded_at
                    >= datetime.combine(target_date, datetime.min.time()),
                    GratitudeJournal.recorded_at
                    <= datetime.combine(target_date, datetime.max.time()),
                )
            )
            .all()
        )

        mindfulness_exercises = (
            self.db.query(MindfulnessExercise)
            .filter(
                and_(
                    MindfulnessExercise.user_id == user.id,
                    MindfulnessExercise.completed_at
                    >= datetime.combine(target_date, datetime.min.time()),
                    MindfulnessExercise.completed_at
                    <= datetime.combine(target_date, datetime.max.time()),
                )
            )
            .all()
        )

        # 获取情感洞察（仅当天）
        insight = self.get_emotional_insights(user, 1)

        return DailyEmotionalSummary(
            date=target_date.isoformat(),
            emotional_states=emotional_states,
            stress_levels=stress_levels,
            gratitude_entries=gratitude_entries,
            mindfulness_exercises=mindfulness_exercises,
            emotional_insight=insight,
        )

    def create_emotional_check_in(self, user: User) -> EmotionalCheckIn:
        """创建情感签到"""
        # 获取最近的情感状态
        recent_states = self.get_emotional_states(user, None, None)
        current_emotion = EmotionType.NEUTRAL
        intensity = 5

        if recent_states:
            # 使用最近的情感状态
            latest_state = recent_states[0]
            current_emotion = latest_state.emotion_type
            intensity = latest_state.intensity
        else:
            # 默认值
            current_emotion = EmotionType.NEUTRAL
            intensity = 5

        # 获取最近的应力水平
        recent_stress = (
            self.db.query(StressLevel)
            .filter(StressLevel.user_id == user.id)
            .order_by(StressLevel.recorded_at.desc())
            .first()
        )

        stress_level = recent_stress.stress_level if recent_stress else None

        # 判断是否需要支持
        needs_support = (
            current_emotion
            in [
                EmotionType.SAD,
                EmotionType.ANXIOUS,
                EmotionType.STRESSED,
                EmotionType.FRUSTRATED,
            ]
            and intensity >= 6
        ) or (stress_level and stress_level >= 7)

        # 如果需要支持，生成建议
        support_recommendation = None
        if needs_support:
            support_recommendation = self.provide_emotional_support(
                user, current_emotion, intensity
            )

        return EmotionalCheckIn(
            current_emotion=current_emotion,
            intensity=intensity,
            stress_level=stress_level,
            needs_support=needs_support,
            support_recommendation=support_recommendation,
        )

    def create_emotional_wellness_plan(self, user: User) -> EmotionalWellnessPlan:
        """创建情感健康计划"""
        insights = self.get_emotional_insights(user, 30)

        # 基于洞察生成计划
        daily_practices = []
        weekly_goals = []
        coping_strategies = []

        # 根据主导情感添加练习
        if insights.dominant_emotion in [EmotionType.SAD, EmotionType.ANXIOUS]:
            daily_practices.append("每日感恩记录")
            daily_practices.append("早晨积极肯定语")
            coping_strategies.extend(self.get_coping_strategies(5))

        if insights.avg_stress_level >= 5:
            daily_practices.append("5分钟正念呼吸")
            weekly_goals.append("完成3次10分钟以上正念练习")
            coping_strategies.extend(self.get_coping_strategies(7))

        if insights.gratitude_frequency < 3:
            daily_practices.append("睡前感恩反思")
            weekly_goals.append("记录7条感恩条目")

        if insights.mindfulness_practice < 2:
            daily_practices.append("身体扫描练习")
            weekly_goals.append("尝试2种不同的正念练习")

        # 添加通用实践
        if not daily_practices:
            daily_practices = ["早晨积极肯定语", "晚间情绪反思"]

        if not weekly_goals:
            weekly_goals = ["记录情绪变化模式", "尝试一种新的放松技巧"]

        # 支持资源
        support_resources = [
            "情感支持热线信息",
            "正冥想引导音频",
            "认知行为疗法自助材料",
        ]

        # 进度跟踪指标
        progress_tracking = {
            "daily_practice_completion": 0.0,
            "weekly_goal_progress": 0.0,
            "stress_reduction": 0.0,
            "positive_emotion_increase": 0.0,
        }

        return EmotionalWellnessPlan(
            daily_practices=daily_practices,
            weekly_goals=weekly_goals,
            coping_strategies=coping_strategies,
            support_resources=support_resources,
            progress_tracking=progress_tracking,
        )


def get_emotional_support_service(db: Session) -> EmotionalSupportService:
    """获取情感支持服务实例"""
    return EmotionalSupportService(db)
