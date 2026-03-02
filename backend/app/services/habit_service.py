from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

import structlog
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.models.habit import (
    Habit,
    HabitCategory,
    HabitCompletion,
    HabitFrequency,
    HabitGoal,
)
from app.models.user import User
from app.schemas.habit import (
    BehaviorPatterns,
    CompletionRateStats,
    DailyStats,
    HabitCompletionCreate,
    HabitCorrelation,
    HabitCreate,
    HabitDetailedStats,
    HabitGoalCreate,
    HabitGoalInDB,
    HabitGoalType,
    HabitGoalWithProgress,
    HabitRecommendation,
    HabitStats,
    HabitStatsOverview,
    HabitUpdate,
    StreakInfo,
)

logger = structlog.get_logger()


class HabitService:
    """习惯跟踪服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_habit(self, user: User, habit_data: HabitCreate) -> Habit:
        """创建新习惯"""
        logger.info("Creating new habit", user_id=user.id, habit_name=habit_data.name)

        # 检查是否已存在同名习惯
        existing_habit = (
            self.db.query(Habit)
            .filter(
                and_(
                    Habit.user_id == user.id,
                    Habit.name == habit_data.name,
                    Habit.is_active == True,
                )
            )
            .first()
        )

        if existing_habit:
            logger.warning(
                "Habit already exists", user_id=user.id, habit_name=habit_data.name
            )
            raise ValueError(f"习惯 '{habit_data.name}' 已存在")

        # 创建习惯
        habit = Habit(
            user_id=user.id,
            name=habit_data.name,
            description=habit_data.description,
            category=habit_data.category,
            frequency=habit_data.frequency,
            target_value=habit_data.target_value,
            target_unit=habit_data.target_unit,
            preferred_time=habit_data.preferred_time,
            reminder_enabled=habit_data.reminder_enabled,
            reminder_time=habit_data.reminder_time,
        )

        self.db.add(habit)
        self.db.commit()
        self.db.refresh(habit)

        logger.info(
            "Habit created successfully",
            habit_id=habit.id,
            user_id=user.id,
            habit_name=habit.name,
        )

        return habit

    def update_habit(self, habit: Habit, habit_data: HabitUpdate) -> Habit:
        """更新习惯"""
        logger.info("Updating habit", habit_id=habit.id, user_id=habit.user_id)

        update_data = habit_data.dict(exclude_unset=True)

        # 如果更新名称，检查是否与其他习惯冲突
        if "name" in update_data and update_data["name"] != habit.name:
            existing_habit = (
                self.db.query(Habit)
                .filter(
                    and_(
                        Habit.user_id == habit.user_id,
                        Habit.name == update_data["name"],
                        Habit.is_active == True,
                        Habit.id != habit.id,
                    )
                )
                .first()
            )

            if existing_habit:
                logger.warning(
                    "Habit name conflict",
                    user_id=habit.user_id,
                    habit_name=update_data["name"],
                )
                raise ValueError(f"习惯 '{update_data['name']}' 已存在")

        # 更新字段
        for field, value in update_data.items():
            setattr(habit, field, value)

        self.db.commit()
        self.db.refresh(habit)

        logger.info("Habit updated successfully", habit_id=habit.id)

        return habit

    def delete_habit(self, habit: Habit) -> None:
        """删除习惯（软删除）"""
        logger.info("Deleting habit", habit_id=habit.id, user_id=habit.user_id)

        habit.is_active = False
        self.db.commit()

        logger.info("Habit deleted successfully", habit_id=habit.id)

    def get_user_habits(
        self, user: User, active_only: bool = True, category: Optional[str] = None
    ) -> List[Habit]:
        """获取用户习惯"""
        logger.info("Getting user habits", user_id=user.id)

        query = self.db.query(Habit).filter(Habit.user_id == user.id)

        if active_only:
            query = query.filter(Habit.is_active == True)

        if category:
            query = query.filter(Habit.category == category)

        habits = query.order_by(Habit.created_at.desc()).all()

        logger.info("Retrieved user habits", user_id=user.id, habit_count=len(habits))

        return habits

    def get_habit_by_id(self, user: User, habit_id: int) -> Optional[Habit]:
        """根据ID获取习惯"""
        habit = (
            self.db.query(Habit)
            .filter(and_(Habit.id == habit_id, Habit.user_id == user.id))
            .first()
        )

        if habit:
            logger.debug("Found habit", habit_id=habit_id, user_id=user.id)
        else:
            logger.debug("Habit not found", habit_id=habit_id, user_id=user.id)

        return habit

    def record_completion(
        self, habit: Habit, completion_data: HabitCompletionCreate
    ) -> HabitCompletion:
        """记录习惯完成"""
        logger.info("Recording habit completion", habit_id=habit.id)

        # 检查今天是否已经记录过
        today_start = datetime.combine(date.today(), datetime.min.time())
        today_end = datetime.combine(date.today(), datetime.max.time())

        existing_completion = (
            self.db.query(HabitCompletion)
            .filter(
                and_(
                    HabitCompletion.habit_id == habit.id,
                    HabitCompletion.completion_date >= today_start,
                    HabitCompletion.completion_date <= today_end,
                )
            )
            .first()
        )

        if existing_completion:
            logger.warning(
                "Completion already recorded today",
                habit_id=habit.id,
                completion_id=existing_completion.id,
            )
            raise ValueError("今天已经记录过该习惯的完成情况")

        # 创建完成记录
        completion = HabitCompletion(
            habit_id=habit.id,
            completion_date=completion_data.completion_date,
            actual_value=completion_data.actual_value,
            notes=completion_data.notes,
            mood_rating=completion_data.mood_rating,
            difficulty_rating=completion_data.difficulty_rating,
        )

        self.db.add(completion)

        # 更新习惯统计
        habit.total_completions += 1
        habit.updated_at = datetime.utcnow()

        # 更新连续天数
        self._update_streak(habit)

        self.db.commit()
        self.db.refresh(completion)

        # 检查并发送里程碑通知
        self._check_milestones(habit)

        logger.info(
            "Habit completion recorded",
            completion_id=completion.id,
            habit_id=habit.id,
            streak_days=habit.streak_days,
        )

        return completion

    def _check_milestones(self, habit: Habit) -> None:
        """检查并触发里程碑通知"""
        try:
            # 延迟导入避免循环依赖
            from app.services.milestone_service import get_milestone_service

            milestone_service = get_milestone_service(self.db)
            achieved = milestone_service.check_and_notify_milestones(
                habit=habit,
                trigger_type="completion",
            )

            if achieved:
                logger.info(
                    "Milestones achieved",
                    habit_id=habit.id,
                    milestone_count=len(achieved),
                )
        except Exception as e:
            # 里程碑检查不应阻止主流程
            logger.error(
                "Failed to check milestones",
                habit_id=habit.id,
                error=str(e),
            )

    def _update_streak(self, habit: Habit) -> None:
        """更新连续天数"""
        # 获取昨天的完成记录
        yesterday = date.today() - timedelta(days=1)
        yesterday_start = datetime.combine(yesterday, datetime.min.time())
        yesterday_end = datetime.combine(yesterday, datetime.max.time())

        yesterday_completion = (
            self.db.query(HabitCompletion)
            .filter(
                and_(
                    HabitCompletion.habit_id == habit.id,
                    HabitCompletion.completion_date >= yesterday_start,
                    HabitCompletion.completion_date <= yesterday_end,
                )
            )
            .first()
        )

        if yesterday_completion:
            # 昨天有完成，连续天数+1
            habit.streak_days += 1
        else:
            # 昨天没有完成，检查是否中断
            # 获取前天的完成记录
            day_before_yesterday = date.today() - timedelta(days=2)
            day_before_start = datetime.combine(
                day_before_yesterday, datetime.min.time()
            )
            day_before_end = datetime.combine(day_before_yesterday, datetime.max.time())

            day_before_completion = (
                self.db.query(HabitCompletion)
                .filter(
                    and_(
                        HabitCompletion.habit_id == habit.id,
                        HabitCompletion.completion_date >= day_before_start,
                        HabitCompletion.completion_date <= day_before_end,
                    )
                )
                .first()
            )

            if not day_before_completion:
                # 前天也没有完成，连续中断，重置为1
                habit.streak_days = 1
            # 如果前天有完成但昨天没有，说明连续中断，但今天重新开始，保持为1

    def get_completions(
        self,
        habit: Habit,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[HabitCompletion]:
        """获取习惯完成记录"""
        query = self.db.query(HabitCompletion).filter(
            HabitCompletion.habit_id == habit.id
        )

        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            query = query.filter(HabitCompletion.completion_date >= start_datetime)

        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            query = query.filter(HabitCompletion.completion_date <= end_datetime)

        completions = query.order_by(HabitCompletion.completion_date.desc()).all()

        logger.debug(
            "Retrieved habit completions",
            habit_id=habit.id,
            completion_count=len(completions),
        )

        return completions

    def get_habit_stats(self, user: User) -> HabitStats:
        """获取习惯统计"""
        logger.info("Getting habit stats", user_id=user.id)

        # 获取所有活跃习惯
        habits = self.get_user_habits(user, active_only=True)

        # 计算基本统计
        total_habits = len(habits)
        active_habits = total_habits
        total_completions = sum(habit.total_completions for habit in habits)

        # 计算当前最长连续天数
        current_streak = max((habit.streak_days for habit in habits), default=0)

        # 计算完成率（最近7天）
        completion_rate = self._calculate_completion_rate(user, habits)

        # 按类别统计
        category_stats = {}
        for habit in habits:
            category = habit.category.value
            category_stats[category] = category_stats.get(category, 0) + 1

        # 最近7天完成情况
        weekly_completions = self._get_weekly_completions(user)

        stats = HabitStats(
            total_habits=total_habits,
            active_habits=active_habits,
            total_completions=total_completions,
            current_streak=current_streak,
            completion_rate=completion_rate,
            category_stats=category_stats,
            weekly_completions=weekly_completions,
        )

        logger.info(
            "Habit stats calculated",
            user_id=user.id,
            total_habits=total_habits,
            completion_rate=completion_rate,
        )

        return stats

    def _calculate_completion_rate(self, user: User, habits: List[Habit]) -> float:
        """计算完成率（最近7天）"""
        if not habits:
            return 0.0

        # 获取最近7天的日期范围
        end_date = date.today()
        start_date = end_date - timedelta(days=6)

        total_possible = 0
        total_completed = 0

        for habit in habits:
            # 根据频率计算可能完成次数
            if habit.frequency == HabitFrequency.DAILY:
                possible = 7
            elif habit.frequency == HabitFrequency.WEEKLY:
                possible = 1
            else:  # MONTHLY
                possible = 0  # 月度习惯在7天内可能完成0-1次

            total_possible += possible

            # 获取最近7天的完成记录
            completions = self.get_completions(habit, start_date, end_date)
            total_completed += len(completions)

        if total_possible == 0:
            return 0.0

        return round((total_completed / total_possible) * 100, 1)

    def _get_weekly_completions(self, user: User) -> List[int]:
        """获取最近7天每天的习惯完成数量"""
        weekly_completions = [0] * 7  # 最近7天，索引0=6天前，索引6=今天

        # 获取最近7天的日期
        today = date.today()
        for i in range(7):
            target_date = today - timedelta(days=6 - i)
            start_datetime = datetime.combine(target_date, datetime.min.time())
            end_datetime = datetime.combine(target_date, datetime.max.time())

            # 查询该日期所有习惯的完成记录
            completions_count = (
                self.db.query(func.count(HabitCompletion.id))
                .join(Habit)
                .filter(
                    and_(
                        Habit.user_id == user.id,
                        Habit.is_active == True,
                        HabitCompletion.completion_date >= start_datetime,
                        HabitCompletion.completion_date <= end_datetime,
                    )
                )
                .scalar()
            )

            weekly_completions[i] = completions_count or 0

        return weekly_completions

    def get_daily_checklist(self, user: User, target_date: date = None) -> Dict:
        """获取每日习惯检查清单"""
        if target_date is None:
            target_date = date.today()

        logger.info("Getting daily checklist", user_id=user.id, date=target_date)

        # 获取用户所有活跃习惯
        habits = self.get_user_habits(user, active_only=True)

        checklist_items = []
        completed_count = 0

        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())

        for habit in habits:
            # 检查今天是否已完成
            completion = (
                self.db.query(HabitCompletion)
                .filter(
                    and_(
                        HabitCompletion.habit_id == habit.id,
                        HabitCompletion.completion_date >= start_datetime,
                        HabitCompletion.completion_date <= end_datetime,
                    )
                )
                .first()
            )

            is_completed = completion is not None

            if is_completed:
                completed_count += 1

            checklist_items.append(
                {
                    "habit_id": habit.id,
                    "name": habit.name,
                    "description": habit.description,
                    "category": habit.category.value,
                    "target_value": habit.target_value,
                    "target_unit": habit.target_unit,
                    "is_completed": is_completed,
                    "completion_id": completion.id if completion else None,
                    "actual_value": completion.actual_value if completion else None,
                    "notes": completion.notes if completion else None,
                    "mood_rating": completion.mood_rating if completion else None,
                    "difficulty_rating": completion.difficulty_rating
                    if completion
                    else None,
                }
            )

        total_count = len(checklist_items)
        completion_percentage = (
            round((completed_count / total_count) * 100, 1) if total_count > 0 else 0
        )

        return {
            "date": target_date,
            "habits": checklist_items,
            "completed_count": completed_count,
            "total_count": total_count,
            "completion_percentage": completion_percentage,
        }

    def get_habit_recommendations(self, user: User) -> List[HabitRecommendation]:
        """获取习惯建议"""
        logger.info("Getting habit recommendations", user_id=user.id)

        # 获取用户现有习惯的类别
        existing_habits = self.get_user_habits(user, active_only=True)
        existing_categories = {habit.category for habit in existing_habits}

        # 基础习惯建议
        all_recommendations = [
            HabitRecommendation(
                category=HabitCategory.HYDRATION,
                name="每日饮水",
                description="每天喝足够的水",
                why_important="保持身体水分平衡，促进新陈代谢",
                difficulty="easy",
                estimated_time="全天",
                suggested_frequency=HabitFrequency.DAILY,
            ),
            HabitRecommendation(
                category=HabitCategory.DIET,
                name="蔬菜摄入",
                description="每天吃足够的蔬菜",
                why_important="提供维生素、矿物质和纤维",
                difficulty="medium",
                estimated_time="每餐",
                suggested_frequency=HabitFrequency.DAILY,
            ),
            HabitRecommendation(
                category=HabitCategory.EXERCISE,
                name="每日活动",
                description="每天进行适量运动",
                why_important="增强心肺功能，消耗卡路里",
                difficulty="medium",
                estimated_time="30分钟",
                suggested_frequency=HabitFrequency.DAILY,
            ),
            HabitRecommendation(
                category=HabitCategory.SLEEP,
                name="规律睡眠",
                description="保持规律的睡眠时间",
                why_important="促进身体恢复，调节激素",
                difficulty="hard",
                estimated_time="7-8小时",
                suggested_frequency=HabitFrequency.DAILY,
            ),
            HabitRecommendation(
                category=HabitCategory.MENTAL_HEALTH,
                name="正念冥想",
                description="每天进行正念练习",
                why_important="减轻压力，提高专注力",
                difficulty="medium",
                estimated_time="10分钟",
                suggested_frequency=HabitFrequency.DAILY,
            ),
        ]

        # 过滤掉用户已有类别的建议（可选）
        # filtered_recommendations = [
        #     rec for rec in all_recommendations
        #     if rec.category not in existing_categories
        # ]

        # 暂时返回所有建议
        return all_recommendations

    def get_streak_info(self, habit: Habit) -> StreakInfo:
        """获取连续天数信息"""
        logger.debug("Getting streak info", habit_id=habit.id)

        # 获取所有完成记录
        completions = self.get_completions(habit)
        completion_dates = [
            completion.completion_date.date() for completion in completions
        ]

        if not completion_dates:
            return StreakInfo(
                current_streak=0,
                longest_streak=0,
                streak_start_date=None,
                last_completion_date=None,
                is_streak_active=False,
            )

        # 排序日期
        completion_dates.sort(reverse=True)

        # 计算当前连续天数
        current_streak = 0
        streak_start_date = None
        last_completion_date = completion_dates[0]
        today = date.today()

        # 检查今天是否完成
        if last_completion_date == today:
            current_streak = 1
            streak_start_date = today
            # 检查之前的连续完成
            for i in range(1, len(completion_dates)):
                expected_date = today - timedelta(days=i)
                if completion_dates[i] == expected_date:
                    current_streak += 1
                    streak_start_date = expected_date
                else:
                    break
        elif last_completion_date == today - timedelta(days=1):
            # 昨天完成，但今天还没完成
            current_streak = 1
            streak_start_date = last_completion_date
            # 检查之前的连续完成
            for i in range(1, len(completion_dates)):
                expected_date = last_completion_date - timedelta(days=i)
                if completion_dates[i] == expected_date:
                    current_streak += 1
                    streak_start_date = expected_date
                else:
                    break

        # 计算最长连续天数
        longest_streak = 0
        if completion_dates:
            current_run = 1
            completion_dates_sorted = sorted(completion_dates)

            for i in range(1, len(completion_dates_sorted)):
                if (
                    completion_dates_sorted[i] - completion_dates_sorted[i - 1]
                ).days == 1:
                    current_run += 1
                else:
                    longest_streak = max(longest_streak, current_run)
                    current_run = 1

            longest_streak = max(longest_streak, current_run)

        is_streak_active = (
            last_completion_date == today
            or last_completion_date == today - timedelta(days=1)
        )

        return StreakInfo(
            current_streak=current_streak,
            longest_streak=longest_streak,
            streak_start_date=streak_start_date,
            last_completion_date=last_completion_date,
            is_streak_active=is_streak_active,
        )

    def get_stats_overview(
        self, user: User, period: str = "weekly"
    ) -> HabitStatsOverview:
        """获取习惯统计概览"""
        logger.info("Getting habit stats overview", user_id=user.id, period=period)

        habits = self.get_user_habits(user, active_only=True)

        if not habits:
            return HabitStatsOverview(
                total_habits=0,
                active_habits=0,
                completion_rate=0.0,
                total_checkins=0,
                current_longest_streak=0,
                best_streak_ever=0,
                weekly_checkins=0,
                monthly_checkins=0,
                by_category={},
            )

        # Get date ranges
        today = date.today()

        # Weekly: last 7 days
        week_start = today - timedelta(days=6)
        week_end = today

        # Monthly: last 30 days
        month_start = today - timedelta(days=29)
        month_end = today

        # Calculate total checkins
        total_checkins = sum(habit.total_completions for habit in habits)

        # Calculate weekly and monthly checkins
        weekly_checkins = 0
        monthly_checkins = 0

        for habit in habits:
            week_completions = self.get_completions(habit, week_start, week_end)
            month_completions = self.get_completions(habit, month_start, month_end)
            weekly_checkins += len(week_completions)
            monthly_checkins += len(month_completions)

        # Calculate completion rates by period
        weekly_rate = self._calculate_completion_rate_for_period(
            user, habits, week_start, week_end
        )

        # For monthly rate, we need to calculate based on expected completions
        monthly_rate = self._calculate_completion_rate_for_period(
            user, habits, month_start, month_end
        )

        # Determine which rate to return based on period parameter
        completion_rate = weekly_rate if period == "weekly" else monthly_rate

        # Get current and best streaks
        current_longest_streak = max((habit.streak_days for habit in habits), default=0)
        best_streak_ever = self._get_best_streak_ever(habits)

        # Calculate by category
        by_category = self._calculate_completion_rate_by_category(user, habits)

        return HabitStatsOverview(
            total_habits=len(habits),
            active_habits=len(habits),
            completion_rate=completion_rate,
            total_checkins=total_checkins,
            current_longest_streak=current_longest_streak,
            best_streak_ever=best_streak_ever,
            weekly_checkins=weekly_checkins,
            monthly_checkins=monthly_checkins,
            by_category=by_category,
        )

    def _calculate_completion_rate_for_period(
        self, user: User, habits: List[Habit], start_date: date, end_date: date
    ) -> float:
        """计算指定期间的完成率"""
        if not habits:
            return 0.0

        days_diff = (end_date - start_date).days + 1
        total_possible = 0
        total_completed = 0

        for habit in habits:
            if habit.frequency == HabitFrequency.DAILY:
                possible = days_diff
            elif habit.frequency == HabitFrequency.WEEKLY:
                possible = max(1, days_diff // 7)
            else:  # MONTHLY
                possible = max(1, days_diff // 30)

            total_possible += possible

            completions = self.get_completions(habit, start_date, end_date)
            total_completed += len(completions)

        if total_possible == 0:
            return 0.0

        return round((total_completed / total_possible) * 100, 1)

    def _get_best_streak_ever(self, habits: List[Habit]) -> int:
        """获取所有习惯的历史最长连续天数"""
        best_streak = 0

        for habit in habits:
            streak_info = self.get_streak_info(habit)
            if streak_info.longest_streak > best_streak:
                best_streak = streak_info.longest_streak

        return best_streak

    def _calculate_completion_rate_by_category(
        self, user: User, habits: List[Habit]
    ) -> Dict[str, float]:
        """按类别计算完成率"""
        today = date.today()
        week_start = today - timedelta(days=6)

        category_stats: Dict[str, float] = {}
        category_counts: Dict[
            str, Tuple[int, int]
        ] = {}  # {category: (completed, total)}

        for habit in habits:
            category = habit.category
            completions = self.get_completions(habit, week_start, today)

            if habit.frequency == HabitFrequency.DAILY:
                possible = 7
            elif habit.frequency == HabitFrequency.WEEKLY:
                possible = 1
            else:
                possible = 0

            if category not in category_counts:
                category_counts[category] = (0, 0)

            completed, total = category_counts[category]
            category_counts[category] = (completed + len(completions), total + possible)

        for category, (completed, total) in category_counts.items():
            if total > 0:
                category_stats[category] = round((completed / total) * 100, 1)
            else:
                category_stats[category] = 0.0

        return category_stats

    def get_completion_rate_stats(
        self, user: User, period: str = "weekly"
    ) -> CompletionRateStats:
        """获取完成率统计"""
        logger.info("Getting completion rate stats", user_id=user.id, period=period)

        habits = self.get_user_habits(user, active_only=True)

        if not habits:
            return CompletionRateStats(
                period=period,
                completion_rate=0.0,
                total_required=0,
                total_completed=0,
                trend=[],
            )

        today = date.today()

        if period == "weekly":
            start_date = today - timedelta(days=6)
        elif period == "monthly":
            start_date = today - timedelta(days=29)
        else:  # quarterly
            start_date = today - timedelta(days=89)

        # Calculate totals
        total_required = 0
        total_completed = 0

        for habit in habits:
            if habit.frequency == HabitFrequency.DAILY:
                if period == "weekly":
                    possible = 7
                elif period == "monthly":
                    possible = 30
                else:
                    possible = 90
            elif habit.frequency == HabitFrequency.WEEKLY:
                if period == "weekly":
                    possible = 1
                elif period == "monthly":
                    possible = 4
                else:
                    possible = 12
            else:  # MONTHLY
                if period == "weekly":
                    possible = 0
                elif period == "monthly":
                    possible = 1
                else:
                    possible = 3

            total_required += possible

            completions = self.get_completions(habit, start_date, today)
            total_completed += len(completions)

        completion_rate = (
            round((total_completed / total_required) * 100, 1)
            if total_required > 0
            else 0.0
        )

        # Generate trend data (last 7 data points)
        trend = []
        if period == "weekly":
            for i in range(7):
                day = today - timedelta(days=6 - i)
                day_completed = 0
                day_required = len(habits)  # Assume daily for simplicity

                for habit in habits:
                    day_completions = self.get_completions(habit, day, day)
                    day_completed += len(day_completions)

                day_rate = (
                    (day_completed / day_required * 100) if day_required > 0 else 0.0
                )
                trend.append(round(day_rate, 1))

        return CompletionRateStats(
            period=period,
            completion_rate=completion_rate,
            total_required=total_required,
            total_completed=total_completed,
            trend=trend,
        )

    def get_detailed_stats(self, habit: Habit) -> HabitDetailedStats:
        """获取单个习惯的详细统计"""
        logger.info("Getting detailed stats", habit_id=habit.id)

        # Get all completions
        completions = self.get_completions(habit)

        # Get streak info
        streak_info = self.get_streak_info(habit)

        # Calculate completion rate (last 30 days)
        today = date.today()
        thirty_days_ago = today - timedelta(days=29)

        recent_completions = self.get_completions(habit, thirty_days_ago, today)

        if habit.frequency == HabitFrequency.DAILY:
            expected = 30
        elif habit.frequency == HabitFrequency.WEEKLY:
            expected = 4
        else:
            expected = 1

        completion_rate = (
            round((len(recent_completions) / expected) * 100, 1)
            if expected > 0
            else 0.0
        )

        # Get last 30 days trend
        last_30_days_trend = []
        for i in range(30):
            day = today - timedelta(days=29 - i)
            day_start = datetime.combine(day, datetime.min.time())
            day_end = datetime.combine(day, datetime.max.time())

            day_completion = next(
                (c for c in completions if day_start <= c.completion_date <= day_end),
                None,
            )

            last_30_days_trend.append(
                DailyStats(
                    date=day.isoformat(),
                    completed=day_completion is not None,
                    actual_value=day_completion.actual_value
                    if day_completion
                    else None,
                )
            )

        # Get check-in time distribution
        checkin_time_distribution: Dict[str, int] = {}
        for c in completions:
            hour = c.completion_date.hour
            if 6 <= hour < 10:
                time_period = "morning"
            elif 10 <= hour < 14:
                time_period = "midday"
            elif 14 <= hour < 18:
                time_period = "afternoon"
            elif 18 <= hour < 22:
                time_period = "evening"
            else:
                time_period = "night"

            checkin_time_distribution[time_period] = (
                checkin_time_distribution.get(time_period, 0) + 1
            )

        # Get weekly pattern
        weekly_pattern: Dict[str, float] = {}
        day_names = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        for day_name in day_names:
            # Count completions for this day of week over the last 30 days
            day_completions = [
                c
                for c in recent_completions
                if c.completion_date.strftime("%A") == day_name
            ]
            # Each day should have roughly 4 occurrences in 30 days for daily habits
            expected_count = 4 if habit.frequency == HabitFrequency.DAILY else 1
            rate = (
                round((len(day_completions) / expected_count) * 100, 1)
                if expected_count > 0
                else 0.0
            )
            weekly_pattern[day_name] = min(rate, 100.0)

        # Get monthly pattern (last 30 days by day of month)
        monthly_pattern: Dict[str, float] = {}
        for day in range(1, 32):
            day_completions = [
                c for c in recent_completions if c.completion_date.day == day
            ]
            # For daily habits, each day should have at most 1 completion
            rate = min(len(day_completions) * 100, 100.0)
            monthly_pattern[str(day)] = rate

        return HabitDetailedStats(
            habit_id=habit.id,
            habit_name=habit.name,
            total_checkins=len(completions),
            current_streak=streak_info.current_streak,
            best_streak=streak_info.longest_streak,
            completion_rate=completion_rate,
            last_30_days_trend=last_30_days_trend,
            checkin_time_distribution=checkin_time_distribution,
            weekly_pattern=weekly_pattern,
            monthly_pattern=monthly_pattern,
        )

    def get_behavior_patterns(self, user: User) -> BehaviorPatterns:
        """获取行为模式分析"""
        logger.info("Getting behavior patterns", user_id=user.id)

        habits = self.get_user_habits(user, active_only=True)

        if len(habits) < 2:
            return BehaviorPatterns(
                time_preference="unknown",
                checkin_time_histogram={},
                weekly_pattern={},
                weekend_vs_weekday={},
                habit_correlations=[],
                insights=["添加更多习惯以解锁行为分析"],
            )

        # Get all completions for the last 30 days
        today = date.today()
        thirty_days_ago = today - timedelta(days=29)

        all_completions = []
        for habit in habits:
            completions = self.get_completions(habit, thirty_days_ago, today)
            for c in completions:
                all_completions.append(
                    {
                        "habit_id": habit.id,
                        "habit_name": habit.name,
                        "completion_date": c.completion_date,
                    }
                )

        # Analyze time preference
        time_distribution: Dict[str, int] = {}
        for comp in all_completions:
            hour = comp["completion_date"].hour
            if 6 <= hour < 10:
                time_period = "morning"
            elif 10 <= hour < 14:
                time_period = "midday"
            elif 14 <= hour < 18:
                time_period = "afternoon"
            elif 18 <= hour < 22:
                time_period = "evening"
            else:
                time_period = "night"

            time_distribution[time_period] = time_distribution.get(time_period, 0) + 1

        # Determine time preference
        time_preference = "evening"
        if time_distribution:
            time_preference = max(
                time_distribution.keys(), key=lambda k: time_distribution[k]
            )

        # Analyze weekly pattern
        weekly_pattern: Dict[str, float] = {}
        day_names = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        for day_name in day_names:
            day_completions = [
                c
                for c in all_completions
                if c["completion_date"].strftime("%A") == day_name
            ]
            # Each day should have len(habits) * 4 completions in 30 days for daily habits
            expected = len(habits) * 4
            rate = (
                round((len(day_completions) / expected) * 100, 1)
                if expected > 0
                else 0.0
            )
            weekly_pattern[day_name] = min(rate, 100.0)

        # Weekend vs weekday
        weekday_completions = [
            c for c in all_completions if c["completion_date"].weekday() < 5
        ]
        weekend_completions = [
            c for c in all_completions if c["completion_date"].weekday() >= 5
        ]

        weekday_rate = (
            round((len(weekday_completions) / (len(habits) * 20)) * 100, 1)
            if len(habits) > 0
            else 0.0
        )
        weekend_rate = (
            round((len(weekend_completions) / (len(habits) * 10)) * 100, 1)
            if len(habits) > 0
            else 0.0
        )

        weekend_vs_weekday = {
            "weekday": min(weekday_rate, 100.0),
            "weekend": min(weekend_rate, 100.0),
        }

        # Habit correlations (simple co-occurrence analysis)
        habit_correlations: List[HabitCorrelation] = []

        # Find habits that are often completed on the same day
        for i, h1 in enumerate(habits):
            for h2 in habits[i + 1 :]:
                # Get completions for both habits
                c1 = self.get_completions(h1, thirty_days_ago, today)
                c2 = self.get_completions(h2, thirty_days_ago, today)

                # Find days when both were completed
                dates1 = {c.completion_date.date() for c in c1}
                dates2 = {c.completion_date.date() for c in c2}
                common_dates = dates1 & dates2

                if len(common_dates) >= 3:  # At least 3 common days
                    correlation = len(common_dates) / 30  # Normalize
                    habit_correlations.append(
                        HabitCorrelation(
                            habit_ids=[h1.id, h2.id],
                            habit_names=[h1.name, h2.name],
                            correlation_strength=round(correlation, 2),
                            description=f"这两个习惯经常一起完成（{len(common_dates)}天）",
                        )
                    )

        # Generate insights
        insights: List[str] = []

        if time_preference == "morning":
            insights.append("你倾向于在早晨完成习惯")
        elif time_preference == "afternoon":
            insights.append("你倾向于在下午完成习惯")
        elif time_preference == "evening":
            insights.append("你倾向于在晚间完成习惯")

        if weekend_rate > weekday_rate * 1.2:
            insights.append(
                f"周末完成率比工作日高{round(weekend_rate - weekday_rate)}%"
            )
        elif weekday_rate > weekend_rate * 1.2:
            insights.append(
                f"工作日完成率比周末高{round(weekday_rate - weekend_rate)}%"
            )

        # Find best day
        if weekly_pattern:
            best_day = max(weekly_pattern.keys(), key=lambda k: weekly_pattern[k])
            insights.append(f"你在一周{best_day}完成习惯最多")

        return BehaviorPatterns(
            time_preference=time_preference,
            checkin_time_histogram=time_distribution,
            weekly_pattern=weekly_pattern,
            weekend_vs_weekday=weekend_vs_weekday,
            habit_correlations=habit_correlations[:5],  # Limit to top 5
            insights=insights,
        )

    # ============== Goal Management ==============

    def create_goal(self, user: User, goal_data: HabitGoalCreate) -> HabitGoal:
        """创建习惯目标"""
        logger.info("Creating habit goal", user_id=user.id, habit_id=goal_data.habit_id)

        # Verify habit belongs to user
        habit = self.get_habit_by_id(user, goal_data.habit_id)
        if not habit:
            raise ValueError("习惯不存在")

        goal = HabitGoal(
            user_id=user.id,
            habit_id=goal_data.habit_id,
            goal_type=goal_data.goal_type.value,
            target_value=goal_data.target_value,
            period=goal_data.period.value,
            start_date=datetime.combine(goal_data.start_date, datetime.min.time()),
            end_date=datetime.combine(goal_data.end_date, datetime.max.time()),
        )

        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)

        logger.info("Goal created", goal_id=goal.id)

        return goal

    def get_user_goals(
        self, user: User, habit_id: Optional[int] = None, active_only: bool = False
    ) -> List[HabitGoal]:
        """获取用户目标列表"""
        logger.info("Getting user goals", user_id=user.id)

        query = self.db.query(HabitGoal).filter(HabitGoal.user_id == user.id)

        if habit_id:
            query = query.filter(HabitGoal.habit_id == habit_id)

        if active_only:
            query = query.filter(HabitGoal.is_active == True)

        goals = query.order_by(HabitGoal.created_at.desc()).all()

        return goals

    def get_goal_by_id(self, user: User, goal_id: int) -> Optional[HabitGoal]:
        """根据ID获取目标"""
        goal = (
            self.db.query(HabitGoal)
            .filter(and_(HabitGoal.id == goal_id, HabitGoal.user_id == user.id))
            .first()
        )
        return goal

    def update_goal(self, goal: HabitGoal, goal_data: "HabitGoalUpdate") -> HabitGoal:
        """更新目标"""
        logger.info("Updating goal", goal_id=goal.id)

        update_data = goal_data.dict(exclude_unset=True)

        # Handle date fields
        if "start_date" in update_data and update_data["start_date"]:
            update_data["start_date"] = datetime.combine(
                update_data["start_date"], datetime.min.time()
            )
        if "end_date" in update_data and update_data["end_date"]:
            update_data["end_date"] = datetime.combine(
                update_data["end_date"], datetime.max.time()
            )

        # Handle enum fields
        if "goal_type" in update_data and update_data["goal_type"]:
            update_data["goal_type"] = update_data["goal_type"].value
        if "period" in update_data and update_data["period"]:
            update_data["period"] = update_data["period"].value

        for field, value in update_data.items():
            setattr(goal, field, value)

        self.db.commit()
        self.db.refresh(goal)

        logger.info("Goal updated", goal_id=goal.id)

        return goal

    def delete_goal(self, goal: HabitGoal) -> None:
        """删除目标"""
        logger.info("Deleting goal", goal_id=goal.id)

        self.db.delete(goal)
        self.db.commit()

        logger.info("Goal deleted", goal_id=goal.id)

    def get_goal_with_progress(
        self, user: User, goal_id: int
    ) -> Optional[HabitGoalWithProgress]:
        """获取目标及进度"""
        goal = self.get_goal_by_id(user, goal_id)

        if not goal:
            return None

        # Calculate progress
        today = date.today()
        start_date = (
            goal.start_date.date()
            if isinstance(goal.start_date, datetime)
            else goal.start_date
        )
        end_date = (
            goal.end_date.date()
            if isinstance(goal.end_date, datetime)
            else goal.end_date
        )

        # Get habit
        habit = self.get_habit_by_id(user, goal.habit_id)

        if not habit:
            return None

        # Get completions in the goal period
        completions = self.get_completions(habit, start_date, end_date)

        # Calculate current progress based on goal type
        if goal.goal_type == "completion_rate":
            # For completion rate, we need to calculate expected vs actual
            if goal.period == "weekly":
                expected = 7
            elif goal.period == "monthly":
                expected = 30
            else:
                expected = 90

            current_progress = (
                round((len(completions) / expected) * 100, 1) if expected > 0 else 0.0
            )
        elif goal.goal_type == "streak":
            # For streak, get current streak
            streak_info = self.get_streak_info(habit)
            current_progress = streak_info.current_streak
        else:  # total_count
            current_progress = len(completions)

        # Update goal with current progress
        goal.current_progress = current_progress

        # Check if goal is achieved
        is_achieved = current_progress >= goal.target_value

        # Check if expired
        is_expired = today > end_date

        # Calculate days remaining
        if today <= end_date:
            days_remaining = (end_date - today).days
        else:
            days_remaining = 0

        # Determine status
        if is_achieved:
            status = "achieved"
        elif is_expired:
            status = "expired"
        else:
            status = "in_progress"

        progress_percentage = (
            round((current_progress / goal.target_value) * 100, 1)
            if goal.target_value > 0
            else 0.0
        )

        return HabitGoalWithProgress(
            id=goal.id,
            user_id=goal.user_id,
            habit_id=goal.habit_id,
            goal_type=goal.goal_type,
            target_value=goal.target_value,
            period=goal.period,
            start_date=start_date,
            end_date=end_date,
            is_active=goal.is_active,
            is_achieved=is_achieved,
            current_progress=current_progress,
            created_at=goal.created_at,
            progress_percentage=progress_percentage,
            days_remaining=days_remaining,
            status=status,
        )


def get_habit_service(db: Session) -> HabitService:
    """获取习惯服务实例"""
    return HabitService(db)
