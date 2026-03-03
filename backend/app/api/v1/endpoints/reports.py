"""Health Report API endpoints - provides daily, weekly, monthly health reports using AI interpretation"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db, get_current_active_user
from app.models.user import UserModel
from app.services.report_data_service import ReportDataService
from app.services.ai_report_service import AIReportGenerator
from app.schemas.report_data import ReportData, ReportType
from datetime import date
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any


class EnhancedReport(BaseModel):
    """Enhanced report with AI interpretation"""

    report_data: ReportData
    interpretation: str
    generated_at: datetime


router = APIRouter()


@router.get("/reports/today", response_model=EnhancedReport)
def get_today_report(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    """
    获取今天的健康报告

    返回今日的健康报告，使用AI语言解释用户当前的健康状况。
    """
    # Get report data
    service = ReportDataService(db)
    report_data = service.get_report_data(current_user, ReportType.DAILY)

    # Enhance with AI interpretation
    generator = AIReportGenerator(service)
    enhanced_report = generator.enhance_report_with_ai_interpretation(
        report_data, current_user
    )

    return EnhancedReport(**enhanced_report)


@router.get("/reports/weekly", response_model=EnhancedReport)
def get_weekly_report(
    target_date: date = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    """
    获取本周的健康报告

    返回本周的健康报告，使用AI语言解释用户本周的健康趋势。
    """
    if target_date is None:
        target_date = date.today()

    # Get report data
    service = ReportDataService(db)
    report_data = service.get_report_data(current_user, ReportType.WEEKLY, target_date)

    # Enhance with AI interpretation
    generator = AIReportGenerator(service)
    enhanced_report = generator.enhance_report_with_ai_interpretation(
        report_data, current_user
    )

    return EnhancedReport(**enhanced_report)


@router.get("/reports/monthly", response_model=EnhancedReport)
def get_monthly_report(
    target_date: date = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    """
    获取本月的健康报告

    返回本月的健康报告，使用AI语言解释用户本月的健康趋势。
    """
    if target_date is None:
        target_date = date.today()

    # Get report data
    service = ReportDataService(db)
    report_data = service.get_report_data(current_user, ReportType.MONTHLY, target_date)

    # Enhance with AI interpretation
    generator = AIReportGenerator(service)
    enhanced_report = generator.enhance_report_with_ai_interpretation(
        report_data, current_user
    )

    return EnhancedReport(**enhanced_report)


@router.get("/reports", response_model=List[EnhancedReport])
def get_reports_list(
    report_type: ReportType = ReportType.DAILY,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    """
    获取报告列表

    根据指定的日期范围和报告类型获取多个健康报告。
    """
    if start_date is None or end_date is None:
        # 如果没有指定日期，则返回最近的3个报告
        service = ReportDataService(db)
        generator = AIReportGenerator(service)
        reports = []

        # 根据类型生成最近的3个报告
        import datetime
        from datetime import date as dt

        if report_type == ReportType.DAILY:
            for i in range(3):
                date_offset = date.today() - datetime.timedelta(days=i)
                report_data = service.get_report_data(
                    current_user, report_type, date_offset
                )
                enhanced_report = generator.enhance_report_with_ai_interpretation(
                    report_data, current_user
                )
                reports.append(EnhancedReport(**enhanced_report))
        elif report_type == ReportType.WEEKLY:
            # 每周获取一次报告
            current_week = date.today()
            for i in range(3):
                date_offset = current_week - datetime.timedelta(weeks=i)
                report_data = service.get_report_data(
                    current_user, report_type, date_offset
                )
                enhanced_report = generator.enhance_report_with_ai_interpretation(
                    report_data, current_user
                )
                reports.append(EnhancedReport(**enhanced_report))
        elif report_type == ReportType.MONTHLY:
            # 每月获取一次报告
            current_month = date.today()
            for i in range(3):
                # 简化计算，每个月取一号的数据
                year = current_month.year
                month = current_month.month - i
                if month <= 0:
                    month = 12 + month
                    year -= 1
                date_offset = dt(year, month, 1)
                report_data = service.get_report_data(
                    current_user, report_type, date_offset
                )
                enhanced_report = generator.enhance_report_with_ai_interpretation(
                    report_data, current_user
                )
                reports.append(EnhancedReport(**enhanced_report))

        return reports

    # 如果指定了日期范围和类型，后续可以实现特定日期范围的查询
    raise HTTPException(
        status_code=501, detail="Specified date range functionality not yet implemented"
    )


@router.get("/reports/{report_type}/{target_date}", response_model=EnhancedReport)
def get_report_by_type_and_date(
    report_type: ReportType,
    target_date: date,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    """
    根据类型和日期获取特定报告
    """
    # Get report data
    service = ReportDataService(db)
    report_data = service.get_report_data(current_user, report_type, target_date)

    # Enhance with AI interpretation
    generator = AIReportGenerator(service)
    enhanced_report = generator.enhance_report_with_ai_interpretation(
        report_data, current_user
    )

    return EnhancedReport(**enhanced_report)


@router.get("/reports/weekly", response_model=ReportData)
def get_weekly_report(
    target_date: date = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    """
    获取本周的健康报告

    返回本周的健康报告，使用AI语言解释用户本周的健康趋势。
    """
    if target_date is None:
        target_date = date.today()

    service = ReportDataService(db)
    report_data = service.get_report_data(current_user, ReportType.WEEKLY, target_date)
    return report_data


@router.get("/reports/monthly", response_model=ReportData)
def get_monthly_report(
    target_date: date = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    """
    获取本月的健康报告

    返回本月的健康报告，使用AI语言解释用户本月的健康趋势。
    """
    if target_date is None:
        target_date = date.today()

    service = ReportDataService(db)
    report_data = service.get_report_data(current_user, ReportType.MONTHLY, target_date)
    return report_data


@router.get("/reports", response_model=List[ReportData])
def get_reports_list(
    report_type: ReportType = ReportType.DAILY,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    """
    获取报告列表

    根据指定的日期范围和报告类型获取多个健康报告。
    """
    if start_date is None or end_date is None:
        # 如果没有指定日期，则返回最近的3个报告
        service = ReportDataService(db)
        reports = []

        # 根据类型生成最近的3个报告
        import datetime

        if report_type == ReportType.DAILY:
            for i in range(3):
                date_offset = date.today() - datetime.timedelta(days=i)
                report_data = service.get_report_data(
                    current_user, report_type, date_offset
                )
                reports.append(report_data)
        elif report_type == ReportType.WEEKLY:
            # 每周获取一次报告
            current_week = date.today()
            for i in range(3):
                date_offset = current_week - datetime.timedelta(weeks=i)
                report_data = service.get_report_data(
                    current_user, report_type, date_offset
                )
                reports.append(report_data)
        elif report_type == ReportType.MONTHLY:
            # 每月获取一次报告
            current_month = date.today()
            for i in range(3):
                # 简化计算，每个月取一号的数据
                year = current_month.year
                month = current_month.month - i
                if month <= 0:
                    month = 12 + month
                    year -= 1
                date_offset = date(year, month, 1)
                report_data = service.get_report_data(
                    current_user, report_type, date_offset
                )
                reports.append(report_data)

        return reports

    # 如果指定了日期范围和类型，后续可以实现特定日期范围的查询
    raise HTTPException(
        status_code=501, detail="Specified date range functionality not yet implemented"
    )


@router.get("/reports/{report_type}/{target_date}", response_model=ReportData)
def get_report_by_type_and_date(
    report_type: ReportType,
    target_date: date,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    """
    根据类型和日期获取特定报告
    """
    service = ReportDataService(db)
    report_data = service.get_report_data(current_user, report_type, target_date)
    return report_data
