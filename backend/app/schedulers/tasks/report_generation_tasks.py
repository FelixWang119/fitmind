"""
Scheduled Tasks for Health Report Generation
These tasks will run at configured intervals to generate daily, weekly, and monthly reports for all users
"""

import asyncio
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import UserModel
from app.services.report_data_service import ReportDataService
from app.services.ai_report_service import AIReportGenerator
from app.schemas.report_data import ReportType
from app.models.health_assessment import (
    HealthAssessment,
)  # Re-use existing table or create new one for reports
from app.core.logger import setup_logger
from typing import List, Optional
import traceback


logger = setup_logger(__name__)


async def generate_daily_reports():
    """
    Generate daily health reports for all active users
    Scheduled to run daily at 02:00 AM
    """
    logger.info("Starting daily report generation task")

    db = SessionLocal()
    try:
        # Get all active users
        users = db.query(UserModel).filter(UserModel.is_active == True).all()

        successful_generations = 0
        failed_generations = 0
        errors = []

        for user in users:
            try:
                # Get report data
                report_service = ReportDataService(db)
                report_data = report_service.get_report_data(user, ReportType.DAILY)

                # Add AI interpretation
                ai_generator = AIReportGenerator(report_service)
                enhanced_report = ai_generator.enhance_report_with_ai_interpretation(
                    report_data, user
                )

                # Store report in database (could create a new table or use existing HealthAssessment)
                _store_report(
                    db,
                    user.id,
                    enhanced_report["report_data"],
                    enhanced_report["interpretation"],
                    ReportType.DAILY,
                )

                successful_generations += 1
                logger.debug(f"Successfully generated daily report for user {user.id}")

            except Exception as e:
                failed_generations += 1
                error_msg = f"Failed to generate report for user {user.id}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
                logger.debug(traceback.format_exc())

        logger.info(
            f"Daily report generation completed: {successful_generations} successful, {failed_generations} failed"
        )

        if errors:
            logger.warning(
                f"Errors occurred during daily report generation: {errors[:5]}..."
            )  # Log first 5 errors

    except Exception as e:
        logger.error(f"Critical error in daily reports generation task: {str(e)}")
        logger.debug(traceback.format_exc())
    finally:
        db.close()


async def generate_weekly_reports():
    """
    Generate weekly health reports for all active users
    Scheduled to run weekly on Sundays at 02:00 AM
    """
    logger.info("Starting weekly report generation task")

    db = SessionLocal()
    try:
        # Get all active users
        users = db.query(UserModel).filter(UserModel.is_active == True).all()

        successful_generations = 0
        failed_generations = 0
        errors = []

        for user in users:
            try:
                # Get report data - for weekly report
                report_service = ReportDataService(db)
                # Use end of last week as the reference date
                last_sunday = date.today() - timedelta(
                    days=date.today().weekday() + 1
                )  # Last Sunday
                report_data = report_service.get_report_data(
                    user, ReportType.WEEKLY, last_sunday
                )

                # Add AI interpretation
                ai_generator = AIReportGenerator(report_service)
                enhanced_report = ai_generator.enhance_report_with_ai_interpretation(
                    report_data, user
                )

                # Store report in database
                _store_report(
                    db,
                    user.id,
                    enhanced_report["report_data"],
                    enhanced_report["interpretation"],
                    ReportType.WEEKLY,
                )

                successful_generations += 1
                logger.debug(f"Successfully generated weekly report for user {user.id}")

            except Exception as e:
                failed_generations += 1
                error_msg = (
                    f"Failed to generate weekly report for user {user.id}: {str(e)}"
                )
                errors.append(error_msg)
                logger.error(error_msg)
                logger.debug(traceback.format_exc())

        logger.info(
            f"Weekly report generation completed: {successful_generations} successful, {failed_generations} failed"
        )

        if errors:
            logger.warning(
                f"Errors occurred during weekly report generation: {errors[:5]}..."
            )

    except Exception as e:
        logger.error(f"Critical error in weekly reports generation task: {str(e)}")
        logger.debug(traceback.format_exc())
    finally:
        db.close()


async def generate_monthly_reports():
    """
    Generate monthly health reports for all active users
    Scheduled to run monthly on the 1st at 02:00 AM
    """
    logger.info("Starting monthly report generation task")

    db = SessionLocal()
    try:
        # Get all active users
        users = db.query(UserModel).filter(UserModel.is_active == True).all()

        successful_generations = 0
        failed_generations = 0
        errors = []

        for user in users:
            try:
                # Get report data - for monthly report
                report_service = ReportDataService(db)
                # Use start of current month as the reference date
                first_of_month = date.today().replace(day=1)
                report_data = report_service.get_report_data(
                    user, ReportType.MONTHLY, first_of_month
                )

                # Add AI interpretation
                ai_generator = AIReportGenerator(report_service)
                enhanced_report = ai_generator.enhance_report_with_ai_interpretation(
                    report_data, user
                )

                # Store report in database
                _store_report(
                    db,
                    user.id,
                    enhanced_report["report_data"],
                    enhanced_report["interpretation"],
                    ReportType.MONTHLY,
                )

                successful_generations += 1
                logger.debug(
                    f"Successfully generated monthly report for user {user.id}"
                )

            except Exception as e:
                failed_generations += 1
                error_msg = (
                    f"Failed to generate monthly report for user {user.id}: {str(e)}"
                )
                errors.append(error_msg)
                logger.error(error_msg)
                logger.debug(traceback.format_exc())

        logger.info(
            f"Monthly report generation completed: {successful_generations} successful, {failed_generations} failed"
        )

        if errors:
            logger.warning(
                f"Errors occurred during monthly report generation: {errors[:5]}..."
            )

    except Exception as e:
        logger.error(f"Critical error in monthly reports generation task: {str(e)}")
        logger.debug(traceback.format_exc())
    finally:
        db.close()


def _store_report(
    db: Session,
    user_id: int,
    report_data,
    ai_interpretation: str,
    report_type: ReportType,
):
    """
    Store the generated report in database
    Could create a new table or use HealthAssessment table depending on structure needed
    """
    try:
        # Create report record (could be custom table or use existing HealthAssessment)
        # For now, we are importing the HealthAssessment model
        from app.models.user import health_assessments

        # Create a new assessment record to store the aggregated data
        from app.models.health_assessment import HealthAssessment
        from sqlalchemy.dialects.postgresql import JSON

        assessment = HealthAssessment(
            user_id=user_id,
            assessment_date=datetime.now().date(),
            overall_score=None,  # We don't have scores in auto reports
            overall_grade=None,
            nutrition_score=None,
            behavior_score=None,
            emotion_score=None,
            overall_summary=ai_interpretation,
            additional_data={
                "report_type": report_type,
                "report_data": report_data.dict(),  # Convert Pydantic model to dict
            },
        )

        db.add(assessment)
        db.commit()
        db.refresh(assessment)

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to store report data for user {user_id}: {str(e)}")
        raise
