"""AI Report Generation Service: Generates human-readable interpretations of health reports"""

from typing import Dict, Any
from app.services.report_data_service import ReportDataService, ReportData
from app.models.user import UserModel
from datetime import date, datetime


class AIReportGenerator:
    """AI 报告生成服务 - 为健康数据提供自然语言解读"""

    def __init__(self, report_data_service: ReportDataService):
        self.report_data_service = report_data_service

    def generate_daily_summary(
        self, report_data: ReportData, user_profile: Dict[str, Any]
    ) -> str:
        """
        生成日报解读文本

        Args:
            report_data: 从ReportDataService获取的数据
            user_profile: 用户个人信息 {age, gender, target_weight, etc}

        Returns:
            str: 温暖、积极的日报解读
        """
        # Extract key data points
        nutrients = report_data.nutrition
        exercises = report_data.exercise
        habits = report_data.habits
        weight = report_data.weight

        # Generate personalized interpretation
        day_of_week = report_data.period.start_date.strftime("%A")

        # Diet analysis
        diet_feedback = ""
        if nutrients.meals_count == 0:
            diet_feedback = "今天似乎忘记了记录饮食，记得养成记录习惯哦～"
        elif nutrients.meals_count < 2:
            diet_feedback = "今天记录了{}餐，可以再增加一些饮食记录，让我们更好地了解你的营养摄入。".format(
                nutrients.meals_count
            )
        else:
            calories_msg = ""
            if nutrients.average_daily_calories > 0:
                calories_msg = "平均每日热量 {:.0f} kcal，".format(
                    nutrients.average_daily_calories
                )

            meal_breakdown_msg = (
                "餐食分布：早餐 {} 次，午餐 {} 次，晚餐 {} 次，加餐 {} 次。".format(
                    nutrients.meal_breakdown.get("breakfast", 0),
                    nutrients.meal_breakdown.get("lunch", 0),
                    nutrients.meal_breakdown.get("dinner", 0),
                    nutrients.meal_breakdown.get("snack", 0),
                )
            )
            diet_feedback = "{}{}".format(calories_msg, meal_breakdown_msg)

        # Exercise/habit analysis
        exercise_habit_feedback = ""
        if exercises.total_minutes == 0 and habits.total_checkins == 0:
            exercise_habit_feedback = (
                "今天在运动和习惯方面还有提升空间，明天记得给自己制定一个小目标哦！"
            )
        else:
            exercise_part = ""
            habit_part = ""

            if exercises.total_minutes > 0:
                exercise_part = "运动了 {} 分钟，".format(exercises.total_minutes)

            if habits.total_checkins > 0:
                # Calculate how many habits were completed vs missed
                completed_count = len(habits.habits_completed)
                missed_habits = ", ".join(
                    habits.habits_missed[:3]
                )  # Only mention first 3 missed habits

                habit_part = "完成 {} 次习惯打卡".format(habits.total_checkins)
                if completed_count > 0:
                    habit_part += "（表现优异: {}）".format(
                        ", ".join(habits.habits_completed[:2])
                    )
                if missed_habits:
                    habit_part += "，还需加强: {}".format(missed_habits)

            exercise_habit_feedback = exercise_part + habit_part

        # Weight analysis (if applicable)
        weight_feedback = ""
        if weight.current_weight is not None:
            change_msg = ""
            if weight.weight_change is not None:
                direction = "减重" if weight.weight_change < 0 else "增重"
                change_msg = "，{}{:.2f}kg".format(direction, abs(weight.weight_change))
            weight_feedback = "当前体重 {:.1f}kg{}。保持关注！".format(
                weight.current_weight, change_msg
            )
        else:
            weight_feedback = "今日未记录体重，记得持续关注体重变化哦！"

        # Motivational closing
        closing_msg = ""
        if habits.total_checkins > 3:  # High achievement
            closing_msg = "今天的努力很棒！每一个小进步都在带你迈向更大的改变。"
        elif exercises.total_minutes > 30:  # Good exercise
            closing_msg = "运动是健康生活的基础，继续保持这种积极的生活方式！"
        elif nutrients.meals_count >= 3:
            closing_msg = "记录是改变的第一步，感谢你对健康的负责态度！"
        else:
            closing_msg = "坚持就是胜利，在健康生活的道路上，你会越来越强的！"

        summary = f"""
        今天是{day_of_week}，来看看今天的健康小结吧～

        🍽️  饮食方面: {diet_feedback}
        
        🏃‍♂️  运动/习惯: {exercise_habit_feedback}
        
        📊  体重关注: {weight_feedback}
        
        💡  温馨提示: {closing_msg}
        """.replace("  ", "").strip()

        return summary

    def generate_weekly_summary(
        self, report_data: ReportData, user_profile: Dict[str, Any]
    ) -> str:
        """
        生成周报解读文本

        Args:
            report_data: 从ReportDataService获取的数据
            user_profile: 用户个人信息

        Returns:
            str: 详细的周报解读
        """
        # Extract key data points
        nutrients = report_data.nutrition
        exercises = report_data.exercise
        habits = report_data.habits
        weight = report_data.weight
        period_info = report_data.period

        # Week overview analysis
        week_start = period_info.start_date.strftime("%m月%d日")
        week_end = period_info.end_date.strftime("%m月%d日")

        # Analyze trends
        consistent_days = (
            nutrients.meals_count
        )  # Every recorded day counts as consistent

        exercise_days = exercises.sessions_count
        habit_completion_rate = habits.checkin_rate

        # Determine strong performances
        strengths = []
        areas_for_improvement = []

        if habit_completion_rate >= 85:
            strengths.append(
                "习惯坚持很棒，{}%的完成率展现了你强大的自律！".format(
                    habit_completion_rate
                )
            )
        elif habit_completion_rate >= 70:
            strengths.append(
                "习惯完成率{}%，稳步前进，再接再厉！".format(habit_completion_rate)
            )
        else:
            areas_for_improvement.append("习惯方面可以继续加强")

        if exercise_days >= 4:
            strengths.append(
                "本周运动天数达到{}天，身体状态在明显改善！".format(exercise_days)
            )
        elif exercise_days >= 2:
            strengths.append("维持了一定的运动频率，继续保持！")
        else:
            areas_for_improvement.append("可以适当增加运动频率")

        if nutrients.meals_count >= 14:  # roughly 2 per day for 7 days
            strengths.append("饮食记录很到位，对营养摄入的把控更加精准")
        elif nutrients.meals_count >= 10:
            strengths.append("饮食记录持续进行中，有助于了解营养结构")
        else:
            areas_for_improvement.append("可以加强饮食记录习惯")

        # Weight analysis
        weight_note = ""
        if weight.weight_change is not None:
            direction = "减重" if weight.weight_change < 0 else "增重"
            weight_note = "体重{}{:.2f}kg，".format(
                direction, abs(weight.weight_change)
            )
        else:
            weight_note = ""

        improvement_tips = ""
        if areas_for_improvement:
            improvement_tips = "建议下周在 {} 方面多加注意。".format(
                "、".join(areas_for_improvement)
            )
        else:
            improvement_tips = "各个方面都表现得很不错！"

        closing_message = ""
        if len(strengths) >= 2:
            closing_message = "这一周你在多个方面都取得了进步，继续保持这种势头，下一周可能会有更大突破！"
        else:
            closing_message = (
                "每一次的努力都是为了更好的自己，坚持下去，收获会越来越多！"
            )

        summary = f"""
        📅 第{period_info.start_date.isocalendar()[1]}周总结（{week_start}-{week_end}）

        🌟 本周亮点:
        {chr(10).join(["• " + s for s in strengths])}

        🎯 待提升之处:
        {improvement_tips}

        📊 营养&运动: 
        记录了 {nutrients.meals_count} 餐，运动 {exercise_days} 次，{weight_note}
        习惯坚持率: {habit_completion_rate}%

        💪 总结: {closing_message}
        """.replace("  ", "").strip()

        return summary

    def generate_monthly_summary(
        self, report_data: ReportData, user_profile: Dict[str, Any]
    ) -> str:
        """
        生成月报解读文本

        Args:
            report_data: 从ReportDataService获取的数据
            user_profile: 用户个人信息

        Returns:
            str: 详尽的月报解读
        """
        # Extract key data points
        nutrients = report_data.nutrition
        exercises = report_data.exercise
        habits = report_data.habits
        weight = report_data.weight
        period_info = report_data.period

        # Month overview
        month_str = period_info.start_date.strftime("%Y年%m月")

        # Analysis
        days_in_month = period_info.days_count

        nutrition_consistency = (
            nutrients.meals_count / days_in_month if days_in_month > 0 else 0
        )
        exercise_pattern = (
            exercises.sessions_count / days_in_month if days_in_month > 0 else 0
        )
        habit_pattern = habit_completion_rate = habits.checkin_rate

        # Milestones and achievements
        achievements = []
        if weight.weight_change is not None:
            direction = "减重" if weight.weight_change < 0 else "增重"
            if abs(weight.weight_change) >= 2.0:  # Significant change
                achievements.append(
                    "{} {:.2f}kg - 这是一个显著的里程碑！".format(
                        direction, abs(weight.weight_change)
                    )
                )
            else:
                achievements.append(
                    "{} {:.2f}kg".format(direction, abs(weight.weight_change))
                )

        if habit_pattern >= 85:
            achievements.append(
                "习惯坚持率达到{:0.1f}% - 自律的力量正在显现！".format(habit_pattern)
            )
        elif habit_pattern >= 70:
            achievements.append(
                "习惯坚持率达到{:0.1f}% - 稳步前进".format(habit_pattern)
            )

        if (
            exercises.sessions_count >= days_in_month * 0.6
        ):  # Over 60% of days with exercise
            achievements.append("运动频率很高 - 这对身体健康有长期益处")

        # Pattern analysis
        patterns_identified = []
        if nutrition_consistency >= 1.5:  # More than once per day on average
            patterns_identified.append("建立了良好的饮食记录习惯")
        if exercise_pattern >= 0.4:  # 40% of days with exercise
            patterns_identified.append("形成了稳定运动基础")
        if habit_pattern >= 70:
            patterns_identified.append("建立了可持续的生活习惯")

        areas_for_continued_growth = []
        if nutrition_consistency < 1.0:
            areas_for_continued_growth.append("饮食记录需要加强")
        if exercise_pattern < 0.3:
            areas_for_continued_growth.append("可适度增加运动量")
        if habit_pattern < 70:
            areas_for_continued_growth.append("习惯坚持方面可以继续提升")

        # Construct monthly insights
        achievement_text = "🏆 本月成就:\n"
        if achievements:
            achievement_text += chr(10).join(["• " + a for a in achievements])
        else:
            achievement_text += "• 持续的努力本身就是一种成就，保持这份坚持！"

        pattern_text = "\n📈 发现的良好模式:\n"
        if patterns_identified:
            pattern_text += chr(10).join(["• " + p for p in patterns_identified])
        else:
            pattern_text += "• 继续探索适合自己的健康节奏"

        growth_text = "\n🌱 持续成长建议:\n"
        if areas_for_continued_growth:
            growth_text += chr(10).join(["• " + a for a in areas_for_continued_growth])
        else:
            growth_text += "• 继续享受健康生活的每一天"

        reflection = (
            """
        📈 {month}健康回顾
        
        {achievement_txt}
        
        {pattern_txt}
        
        {growth_txt}
        
        🔮 展望下月: 本月的成功为你奠定了坚实的基础，带着这份力量，继续向着健康的目标迈进！
        """.format(
                month=month_str,
                achievement_txt=achievement_text,
                pattern_txt=pattern_text,
                growth_txt=growth_text,
            )
            .replace("  ", "")
            .strip()
        )

        return reflection

    def enhance_report_with_ai_interpretation(
        self, report_data: ReportData, user: UserModel
    ) -> Dict[str, Any]:
        """
        为报告数据增加AI解读

        Args:
            report_data: From ReportDataService
            user: The user whose report is being generated

        Returns:
            Enhanced report with interpretation
        """
        # Prepare user profile from user object
        user_profile = {
            "id": user.id,
            "age": getattr(user, "age", None),
            "gender": getattr(user, "gender", None),
            "height": getattr(user, "height", None),
            "initial_weight": getattr(user, "initial_weight", None),
            "target_weight": getattr(user, "target_weight", None),
            "current_weight": getattr(user, "current_weight", None),
        }

        # Select the right summary function based on report type
        interpretation = ""
        report_type = report_data.period.report_type

        if report_type == "daily":
            interpretation = self.generate_daily_summary(report_data, user_profile)
        elif report_type == "weekly":
            interpretation = self.generate_weekly_summary(report_data, user_profile)
        elif report_type == "monthly":
            interpretation = self.generate_monthly_summary(report_data, user_profile)
        else:
            # Fallback for unknown report_type
            interpretation = (
                "这是本期的健康报告，包含您的营养摄入、运动情况、习惯坚持等方面的数据。"
            )

        # Convert report_data to dictionary for return
        from pydantic import BaseModel

        class EnhancedReport(BaseModel):
            report_data: ReportData
            interpretation: str
            generated_at: datetime

        enhanced_report = EnhancedReport(
            report_data=report_data,
            interpretation=interpretation,
            generated_at=datetime.now(),
        )

        return enhanced_report.dict()
