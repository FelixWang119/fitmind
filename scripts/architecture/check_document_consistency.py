#!/usr/bin/env python3
"""
文档一致性检查工具

检查代码实现与架构文档的一致性，确保开发遵循已记录的架构决策。
"""

import os
import re
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class CheckStatus(Enum):
    """检查状态"""

    PASS = "✅"
    WARNING = "⚠️"
    FAIL = "❌"
    SKIP = "⏭️"


@dataclass
class ConsistencyCheck:
    """一致性检查结果"""

    check_id: str
    description: str
    status: CheckStatus
    details: str = ""
    file_path: str = ""
    line_number: int = 0
    suggestion: str = ""


@dataclass
class ArchitectureRule:
    """架构规则定义"""

    rule_id: str
    description: str
    pattern: str
    required: bool = True
    files: List[str] = field(default_factory=list)
    exclude_files: List[str] = field(default_factory=list)
    adr_reference: str = ""


class DocumentConsistencyChecker:
    """文档一致性检查器"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.architecture_dir = self.project_root / "docs" / "architecture"
        self.backend_dir = self.project_root / "backend"
        self.results: List[ConsistencyCheck] = []

        # 加载架构规则
        self.rules = self._load_architecture_rules()

    def _load_architecture_rules(self) -> List[ArchitectureRule]:
        """加载架构规则"""
        rules = [
            # ADR-001 相关规则 (v2.0 更新) - 这些是强制性的
            ArchitectureRule(
                rule_id="ADR-001-01",
                description="SQLite队列必须存在",
                pattern=r"class SQLiteQueue",
                required=True,
                files=["**/sqlite_queue.py"],
                adr_reference="ADR-001",
            ),
            ArchitectureRule(
                rule_id="ADR-001-02",
                description="短期记忆服务必须存在",
                pattern=r"class ShortTermMemoryService",
                required=True,
                files=["**/short_term_memory.py"],
                adr_reference="ADR-001",
            ),
            ArchitectureRule(
                rule_id="ADR-001-03",
                description="记忆索引必须使用SQLite队列",
                pattern=r"sqlite.*queue|queue.*sqlite|SQLiteQueue",
                required=True,
                files=["**/short_term_memory.py", "**/sqlite_queue.py"],
                adr_reference="ADR-001",
            ),
            ArchitectureRule(
                rule_id="ADR-001-04",
                description="索引触发必须基于溢出机制",
                pattern=r"current_size.*>.*max_size|overflow.*item|溢出",
                required=True,
                files=["**/sqlite_queue.py"],
                adr_reference="ADR-001",
            ),
            ArchitectureRule(
                rule_id="ADR-001-05",
                description="不应存在定期索引管道文件",
                pattern=r"memory_index_pipeline",
                required=False,  # 应该不存在
                files=["**/memory_index_pipeline.py"],
                adr_reference="ADR-001",
            ),
            ArchitectureRule(
                rule_id="ADR-001-06",
                description="调度器不应包含索引任务",
                pattern=r"memory_indexing_task|索引任务",
                required=False,  # 应该不存在
                files=["**/schedulers/*.py"],
                adr_reference="ADR-001",
            ),
            # 通用架构规则 - 这些是建议性的，不会导致CI失败
            ArchitectureRule(
                rule_id="ARCH-001",
                description="服务类应该遵循命名规范",
                pattern=r"class \w+Service\b",
                required=False,  # 建议性，非强制
                files=["**/services/*.py"],
                exclude_files=["**/tests/**", "**/test_*.py"],
            ),
            ArchitectureRule(
                rule_id="ARCH-002",
                description="API端点应该包含版本前缀",
                pattern=r"@router\.(get|post|put|delete).*v\d",
                required=False,  # 建议性，非强制
                files=["**/endpoints/*.py", "**/api/*.py"],
            ),
            ArchitectureRule(
                rule_id="ARCH-003",
                description="数据库模型应该继承Base",
                pattern=r"class \w+\(Base\)",
                required=False,  # 建议性，非强制
                files=["**/models/*.py"],
            ),
        ]
        return rules

    def check_file(
        self, file_path: Path, rule: ArchitectureRule
    ) -> Optional[ConsistencyCheck]:
        """检查单个文件是否符合规则"""
        try:
            content = file_path.read_text(encoding="utf-8")

            # 检查文件是否匹配规则
            if rule.files and not any(
                file_path.match(pattern) for pattern in rule.files
            ):
                return None

            if rule.exclude_files and any(
                file_path.match(pattern) for pattern in rule.exclude_files
            ):
                return None

            # 搜索模式
            matches = list(
                re.finditer(rule.pattern, content, re.IGNORECASE | re.MULTILINE)
            )

            if matches:
                # 找到匹配
                first_match = matches[0]
                return ConsistencyCheck(
                    check_id=rule.rule_id,
                    description=rule.description,
                    status=CheckStatus.PASS,
                    details=f"在 {file_path.relative_to(self.project_root)} 中找到匹配",
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=content[: first_match.start()].count("\n") + 1,
                    suggestion="",
                )
            elif rule.required:
                # 未找到但要求必须存在
                return ConsistencyCheck(
                    check_id=rule.rule_id,
                    description=rule.description,
                    status=CheckStatus.FAIL,
                    details=f"在 {file_path.relative_to(self.project_root)} 中未找到匹配",
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=0,
                    suggestion=f"请确保实现符合 {rule.adr_reference} 架构决策",
                )
            else:
                # 未找到但不要求必须存在
                return ConsistencyCheck(
                    check_id=rule.rule_id,
                    description=rule.description,
                    status=CheckStatus.WARNING,
                    details=f"在 {file_path.relative_to(self.project_root)} 中未找到匹配（可选规则）",
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=0,
                    suggestion="考虑实现此功能以提升架构一致性",
                )

        except UnicodeDecodeError:
            # 跳过二进制文件
            return None
        except Exception as e:
            return ConsistencyCheck(
                check_id=rule.rule_id,
                description=rule.description,
                status=CheckStatus.FAIL,
                details=f"检查文件时出错: {str(e)}",
                file_path=str(file_path.relative_to(self.project_root)),
                line_number=0,
                suggestion="请检查文件格式和权限",
            )

    def check_adr_implementation(self, adr_number: str) -> List[ConsistencyCheck]:
        """检查特定ADR的实现情况"""
        adr_rules = [rule for rule in self.rules if rule.adr_reference == adr_number]
        results = []

        for rule in adr_rules:
            # 查找相关文件
            for pattern in rule.files:
                for file_path in self.project_root.glob(pattern):
                    if file_path.is_file():
                        check_result = self.check_file(file_path, rule)
                        if check_result:
                            results.append(check_result)

            # 如果没有找到文件但规则是必须的
            if rule.required and not any(r.check_id == rule.rule_id for r in results):
                results.append(
                    ConsistencyCheck(
                        check_id=rule.rule_id,
                        description=rule.description,
                        status=CheckStatus.FAIL,
                        details=f"未找到符合规则 {rule.rule_id} 的文件",
                        file_path="",
                        line_number=0,
                        suggestion=f"请创建实现文件或检查文件路径: {', '.join(rule.files)}",
                    )
                )

        return results

    def check_all(self) -> List[ConsistencyCheck]:
        """执行所有检查"""
        all_results = []

        # 检查所有规则
        for rule in self.rules:
            rule_results = []

            # 查找相关文件
            for pattern in rule.files:
                for file_path in self.project_root.glob(pattern):
                    if file_path.is_file():
                        check_result = self.check_file(file_path, rule)
                        if check_result:
                            rule_results.append(check_result)

            # 如果没有找到文件但规则是必须的
            if rule.required and not rule_results:
                all_results.append(
                    ConsistencyCheck(
                        check_id=rule.rule_id,
                        description=rule.description,
                        status=CheckStatus.FAIL,
                        details=f"未找到符合规则 {rule.rule_id} 的文件",
                        file_path="",
                        line_number=0,
                        suggestion=f"请创建实现文件或检查文件路径: {', '.join(rule.files)}",
                    )
                )
            else:
                all_results.extend(rule_results)

        return all_results

    def generate_report(
        self, results: List[ConsistencyCheck], output_format: str = "text"
    ) -> str:
        """生成检查报告"""
        if output_format == "json":
            return self._generate_json_report(results)
        else:
            return self._generate_text_report(results)

    def _generate_text_report(self, results: List[ConsistencyCheck]) -> str:
        """生成文本报告"""
        report = []
        report.append("=" * 80)
        report.append("文档一致性检查报告")
        report.append("=" * 80)
        report.append("")

        # 按状态分组
        by_status = {}
        for result in results:
            by_status.setdefault(result.status, []).append(result)

        # 统计
        total = len(results)
        passed = len(by_status.get(CheckStatus.PASS, []))
        warnings = len(by_status.get(CheckStatus.WARNING, []))
        failed = len(by_status.get(CheckStatus.FAIL, []))

        report.append(f"检查总数: {total}")
        report.append(f"通过: {passed} {CheckStatus.PASS.value}")
        report.append(f"警告: {warnings} {CheckStatus.WARNING.value}")
        report.append(f"失败: {failed} {CheckStatus.FAIL.value}")
        report.append("")

        # 详细结果
        for status in [CheckStatus.FAIL, CheckStatus.WARNING, CheckStatus.PASS]:
            if status in by_status:
                report.append(f"{status.value} {status.name}")
                report.append("-" * 40)

                for result in by_status[status]:
                    if result.file_path:
                        location = f"{result.file_path}:{result.line_number}"
                    else:
                        location = "N/A"

                    report.append(f"  [{result.check_id}] {result.description}")
                    report.append(f"      位置: {location}")
                    report.append(f"      详情: {result.details}")
                    if result.suggestion:
                        report.append(f"      建议: {result.suggestion}")
                    report.append("")

        # ADR实施情况摘要
        adr_results = {}
        for result in results:
            for rule in self.rules:
                if rule.rule_id == result.check_id and rule.adr_reference:
                    adr_results.setdefault(rule.adr_reference, []).append(result)

        if adr_results:
            report.append("ADR实施情况")
            report.append("-" * 40)
            for adr, adr_checks in adr_results.items():
                adr_passed = sum(1 for c in adr_checks if c.status == CheckStatus.PASS)
                adr_total = len(adr_checks)
                report.append(f"  {adr}: {adr_passed}/{adr_total} 通过")

        return "\n".join(report)

    def _generate_json_report(self, results: List[ConsistencyCheck]) -> str:
        """生成JSON报告"""
        report_data = {
            "summary": {
                "total": len(results),
                "passed": sum(1 for r in results if r.status == CheckStatus.PASS),
                "warnings": sum(1 for r in results if r.status == CheckStatus.WARNING),
                "failed": sum(1 for r in results if r.status == CheckStatus.FAIL),
            },
            "checks": [
                {
                    "id": r.check_id,
                    "description": r.description,
                    "status": r.status.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "details": r.details,
                    "suggestion": r.suggestion,
                }
                for r in results
            ],
        }
        return json.dumps(report_data, indent=2, ensure_ascii=False)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="文档一致性检查工具")
    parser.add_argument("--adr", help="检查特定ADR的实现情况，如 ADR-001")
    parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="输出格式"
    )
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--project-root", default=".", help="项目根目录")

    args = parser.parse_args()

    # 创建检查器
    checker = DocumentConsistencyChecker(args.project_root)

    # 执行检查
    if args.adr:
        print(f"检查 {args.adr} 的实现情况...")
        results = checker.check_adr_implementation(args.adr)
    else:
        print("执行所有架构一致性检查...")
        results = checker.check_all()

    # 生成报告
    report = checker.generate_report(results, args.format)

    # 输出报告
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"报告已保存到: {args.output}")
    else:
        print(report)

    # 返回退出码 - 只对ADR相关失败返回错误
    adr_failed_count = sum(
        1
        for r in results
        if r.status == CheckStatus.FAIL and r.check_id.startswith("ADR-")
    )
    sys.exit(1 if adr_failed_count > 0 else 0)


if __name__ == "__main__":
    main()
