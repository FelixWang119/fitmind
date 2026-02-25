"""APScheduler 调度器配置"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

# 全局调度器实例
scheduler: AsyncIOScheduler = None


def init_scheduler() -> AsyncIOScheduler:
    """初始化调度器"""
    global scheduler

    if scheduler is not None:
        logger.warning("Scheduler already initialized")
        return scheduler

    scheduler = AsyncIOScheduler(
        timezone="Asia/Shanghai",  # 使用北京时间
        job_defaults={
            "coalesce": True,  # 合并错过的执行
            "max_instances": 1,  # 每个任务最多一个实例
            "misfire_grace_time": 60,  # 错过执行的容忍时间
        },
    )

    logger.info("Scheduler initialized")
    return scheduler


def start_scheduler():
    """启动调度器"""
    global scheduler

    if scheduler is None:
        scheduler = init_scheduler()

    scheduler.start()
    logger.info("Scheduler started")


async def shutdown_scheduler():
    """关闭调度器"""
    global scheduler

    if scheduler is not None:
        await scheduler.shutdown()
        logger.info("Scheduler shutdown complete")


def register_notification_jobs():
    """注册通知相关定时任务"""
    from app.schedulers.tasks.notification_tasks import (
        habit_reminder_task,
        milestone_detection_task,
        process_event_logs_task,
        morning_care_task,
        inactive_user_care_task,
    )

    if scheduler is None:
        logger.error("Scheduler not initialized")
        return

    # 1. 习惯提醒轮询 - 每分钟执行
    scheduler.add_job(
        habit_reminder_task,
        trigger=IntervalTrigger(seconds=60),
        id="habit_reminder",
        name="习惯提醒轮询",
        replace_existing=True,
    )
    logger.info("Registered job: habit_reminder (every 60 seconds)")

    # 2. 里程碑检测轮询 - 每 5 分钟执行
    scheduler.add_job(
        milestone_detection_task,
        trigger=IntervalTrigger(minutes=5),
        id="milestone_detection",
        name="里程碑检测轮询",
        replace_existing=True,
    )
    logger.info("Registered job: milestone_detection (every 5 minutes)")

    # 3. 事件日志处理 - 每 30 秒执行
    scheduler.add_job(
        process_event_logs_task,
        trigger=IntervalTrigger(seconds=30),
        id="process_event_logs",
        name="事件日志处理",
        replace_existing=True,
    )
    logger.info("Registered job: process_event_logs (every 30 seconds)")

    # 4. 早安关怀 - 每天早上 8:00 执行
    scheduler.add_job(
        morning_care_task,
        trigger=CronTrigger(hour=8, minute=0),
        id="morning_care",
        name="早安关怀",
        replace_existing=True,
    )
    logger.info("Registered job: morning_care (daily at 08:00)")

    # 5. 未登录关怀 - 每天下午 2 点执行
    scheduler.add_job(
        inactive_user_care_task,
        trigger=CronTrigger(hour=14, minute=0),
        id="inactive_user_care",
        name="未登录关怀",
        replace_existing=True,
    )
    logger.info("Registered job: inactive_user_care (daily at 14:00)")

    logger.info("All notification jobs registered")


def get_scheduler_status() -> dict:
    """获取调度器状态"""
    if scheduler is None:
        return {"status": "not_initialized"}

    jobs = []
    for job in scheduler.get_jobs():
        jobs.append(
            {
                "id": job.id,
                "name": job.name,
                "next_run_time": str(job.next_run_time),
            }
        )

    return {
        "status": "running" if scheduler.running else "stopped",
        "jobs": jobs,
    }
