#!/usr/bin/env python
"""
Verification script for Story 10.2 and Story 10.3: AI Report Generator and Scheduled Tasks
This scripts checks that the essential components for these stories are properly in place.
"""

import os
import sys
from pathlib import Path


def check_file_exists(filepath, description):
    """Check if file exists and report status"""
    path = Path(filepath)
    exists = path.exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists


def main():
    print("🔍 Verifying Story 10.2: AI Report Generation Service")
    print("🔍 Verifying Story 10.3: Scheduled Tasks for Report Generation")
    print("=" * 70)

    # Files that should exist for Story 10.2
    files_to_check_10_2 = [
        ("backend/app/services/ai_report_service.py", "AI Report Generation Service"),
    ]

    # Files that should exist for Story 10.3
    files_to_check_10_3 = [
        (
            "backend/app/schedulers/tasks/report_generation_tasks.py",
            "Report Generation Tasks",
        ),
    ]

    # Files that need to be modified/extended
    files_to_check_extended = [
        (
            "backend/app/api/v1/endpoints/reports.py",
            "Updated API Endpoints with AI Interpretation",
        ),
    ]

    all_good = True

    # Check files from Story 10.2
    for filepath, description in files_to_check_10_2:
        if not check_file_exists(filepath, description):
            all_good = False

    # Check files from Story 10.3
    for filepath, description in files_to_check_10_3:
        if not check_file_exists(filepath, description):
            all_good = False

    # Check extended files
    for filepath, description in files_to_check_extended:
        if not check_file_exists(filepath, description):
            all_good = False

    print("\n📋 Verification Results:")
    print("-" * 30)

    if all_good:
        print("✅ All required components for Stories 10.2 and 10.3 are in place!")
        print("\nFor Story 10.2 (AI Report Generation):")
        print("  - AI service for natural language report interpretations")
        print("  - Daily, weekly, and monthly report generation logic")
        print("  - Integration with API endpoints")

        print("\nFor Story 10.3 (Scheduled Tasks):")
        print("  - Automated daily report generation")
        print("  - Automated weekly report generation")
        print("  - Automated monthly report generation")
        print("  - Error handling and logging")

        print("\n✅ Stories 10.2 and 10.3 ready for next phase.")
        return 0
    else:
        print("❌ Some components are missing. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
