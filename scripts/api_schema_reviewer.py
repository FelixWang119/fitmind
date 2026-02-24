#!/usr/bin/env python3
"""
API Schema 完整性审查工具

检查项目:
1. Update Schema 是否包含所有可更新字段
2. Create/Update Schema 是否包含嵌套对象 (items, children 等)
3. 响应 Schema 的字段名是否与前端期望一致
4. 是否使用了可能导致字段名不一致的 serialization_alias
5. Endpoint 的 update 函数是否正确处理嵌套对象
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

# 项目根目录
PROJECT_ROOT = Path("/Users/felix/bmad/backend")
SCHEMAS_DIR = PROJECT_ROOT / "app" / "schemas"
ENDPOINTS_DIR = PROJECT_ROOT / "app" / "api" / "v1" / "endpoints"
MODELS_DIR = PROJECT_ROOT / "app" / "models"


@dataclass
class SchemaField:
    name: str
    field_type: str
    is_optional: bool
    has_default: bool
    is_nested_list: bool
    nested_type: Optional[str] = None
    alias: Optional[str] = None
    serialization_alias: Optional[str] = None


@dataclass
class SchemaInfo:
    file: str
    class_name: str
    schema_type: str  # Create, Update, Response, Base
    fields: List[SchemaField] = field(default_factory=list)
    parent_class: Optional[str] = None


@dataclass
class EndpointInfo:
    file: str
    function_name: str
    method: str  # GET, POST, PUT, DELETE
    path: str
    has_update_logic: bool
    handles_nested_objects: bool
    nested_field_name: Optional[str] = None


@dataclass
class Issue:
    severity: str  # ERROR, WARNING, INFO
    module: str
    category: str
    message: str
    file: str
    line: Optional[int] = None
    suggestion: Optional[str] = None


class APISchemaReviewer:
    def __init__(self):
        self.schemas: Dict[str, List[SchemaInfo]] = {}
        self.endpoints: Dict[str, List[EndpointInfo]] = {}
        self.issues: List[Issue] = []
        self.models_relations: Dict[str, List[str]] = {}

    def scan_all(self):
        """扫描所有 schema 和 endpoint 文件"""
        print("🔍 扫描 Schema 文件...")
        self.scan_schemas()

        print("🔍 扫描 Endpoint 文件...")
        self.scan_endpoints()

        print("🔍 扫描 Models 关系...")
        self.scan_model_relations()

    def scan_schemas(self):
        """扫描所有 schema 文件"""
        for schema_file in SCHEMAS_DIR.glob("*.py"):
            if schema_file.name.startswith("__"):
                continue

            module_name = schema_file.stem
            self.schemas[module_name] = []

            with open(schema_file, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            # 查找所有 class 定义
            class_pattern = r"class\s+(\w+)(?:\(([^)]+)\))?:"
            for match in re.finditer(class_pattern, content):
                class_name = match.group(1)
                parent_class = match.group(2) if match.group(2) else None

                # 判断 schema 类型
                schema_type = self.classify_schema(class_name, parent_class)

                schema_info = SchemaInfo(
                    file=str(schema_file),
                    class_name=class_name,
                    schema_type=schema_type,
                    parent_class=parent_class,
                )

                # 提取字段
                self.extract_fields(schema_info, content, match.end())
                self.schemas[module_name].append(schema_info)

    def classify_schema(self, class_name: str, parent_class: Optional[str]) -> str:
        """分类 schema 类型"""
        name_lower = class_name.lower()

        if "create" in name_lower:
            return "Create"
        elif "update" in name_lower:
            return "Update"
        elif "response" in name_lower or "out" in name_lower:
            return "Response"
        elif "base" in name_lower:
            return "Base"
        else:
            # 根据 parent 类判断
            if parent_class:
                parent_lower = parent_class.lower()
                if "create" in parent_lower:
                    return "Create"
                elif "update" in parent_lower:
                    return "Update"
            return "Response"

    def extract_fields(self, schema_info: SchemaInfo, content: str, start_pos: int):
        """提取 schema 字段"""
        # 找到 class 的结束位置
        class_content = content[start_pos:]

        # 提取 Field 定义
        field_pattern = (
            r"(\w+):\s*(?:Optional\[)?([^=\]]+)(?:\])?\s*=\s*Field\(([^)]+)\)"
        )

        for match in re.finditer(field_pattern, class_content):
            field_name = match.group(1)
            field_type = match.group(2).strip()
            field_args = match.group(3)

            is_optional = "Optional" in match.group(0)
            has_default = "default=" in field_args or "=None" in match.group(0)

            # 检查是否是嵌套列表
            is_nested_list = "List[" in field_type or "List[" in match.group(0)
            nested_type = None
            if is_nested_list:
                nested_match = re.search(r"List\[(\w+)\]", field_type)
                if nested_match:
                    nested_type = nested_match.group(1)

            # 检查 alias
            alias = None
            alias_match = re.search(r'alias=["\'](\w+)["\']', field_args)
            if alias_match:
                alias = alias_match.group(1)

            # 检查 serialization_alias
            serial_alias = None
            serial_match = re.search(r'serialization_alias=["\'](\w+)["\']', field_args)
            if serial_match:
                serial_alias = serial_match.group(1)

            schema_info.fields.append(
                SchemaField(
                    name=field_name,
                    field_type=field_type,
                    is_optional=is_optional,
                    has_default=has_default,
                    is_nested_list=is_nested_list,
                    nested_type=nested_type,
                    alias=alias,
                    serialization_alias=serial_alias,
                )
            )

    def scan_endpoints(self):
        """扫描所有 endpoint 文件"""
        for endpoint_file in ENDPOINTS_DIR.glob("*.py"):
            if endpoint_file.name.startswith("__"):
                continue

            module_name = endpoint_file.stem
            self.endpoints[module_name] = []

            with open(endpoint_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 查找 router 装饰器
            route_methods = [
                "@router.get",
                "@router.post",
                "@router.put",
                "@router.delete",
                "@router.patch",
            ]

            for method in route_methods:
                http_method = method.split(".")[1].upper()

                # 查找所有使用该装饰器的函数
                pattern = (
                    rf'{method}\(["\']([^"\']+)["\'][^)]*\)\s*async\s+def\s+(\w+)\('
                )

                for match in re.finditer(pattern, content):
                    path = match.group(1)
                    func_name = match.group(2)

                    # 获取函数内容
                    func_start = match.end()
                    func_content = self.extract_function_body(content[func_start:])

                    # 检查是否处理嵌套对象
                    has_nested = False
                    nested_field = None

                    if http_method in ["PUT", "POST", "PATCH"]:
                        # 检查是否有 items 或类似字段处理
                        nested_patterns = [
                            r'\.pop\([\'"]items[\'"]',
                            r"items_data\s*=",
                            r"for\s+\w+\s+in\s+.*\.items",
                            r"meal_items.*create",
                            r"habit_completions.*create",
                        ]

                        for pattern in nested_patterns:
                            if re.search(pattern, func_content, re.IGNORECASE):
                                has_nested = True
                                # 尝试找出字段名
                                items_match = re.search(r"(\w+)_data\s*=", func_content)
                                if items_match:
                                    nested_field = items_match.group(1)
                                break

                    endpoint_info = EndpointInfo(
                        file=str(endpoint_file),
                        function_name=func_name,
                        method=http_method,
                        path=path,
                        has_update_logic=http_method in ["PUT", "PATCH"],
                        handles_nested_objects=has_nested,
                        nested_field_name=nested_field,
                    )

                    self.endpoints[module_name].append(endpoint_info)

    def extract_function_body(self, content: str) -> str:
        """提取函数体（简单实现）"""
        # 找到下一个函数定义或文件结束
        match = re.search(r"\n(?:async\s+)?def\s+\w+\(", content)
        if match:
            return content[: match.start()]
        return content[:2000]  # 限制长度

    def scan_model_relations(self):
        """扫描 Model 中的关系字段"""
        for model_file in MODELS_DIR.glob("*.py"):
            if model_file.name.startswith("__"):
                continue

            with open(model_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 查找 relationship 定义
            rel_pattern = r"(\w+)\s*=\s*relationship\(([^)]+)\)"

            for match in re.finditer(rel_pattern, content):
                rel_name = match.group(1)
                model_name = model_file.stem

                if model_name not in self.models_relations:
                    self.models_relations[model_name] = []
                self.models_relations[model_name].append(rel_name)

    def analyze(self):
        """执行分析并生成问题报告"""
        print("\n🔍 分析问题...\n")

        self.check_update_schemas()
        self.check_serialization_aliases()
        self.check_nested_object_handling()
        self.check_field_consistency()

    def check_update_schemas(self):
        """检查 Update Schema 是否完整"""
        for module_name, schemas in self.schemas.items():
            # 查找 Update schema
            update_schema = None
            create_schema = None
            response_schema = None

            for schema in schemas:
                if schema.schema_type == "Update":
                    update_schema = schema
                elif schema.schema_type == "Create":
                    create_schema = schema
                elif schema.schema_type == "Response":
                    response_schema = schema

            if not update_schema:
                continue

            # 检查 Update 是否缺少 Create 中的字段
            if create_schema:
                create_fields = {f.name: f for f in create_schema.fields}
                update_fields = {f.name: f for f in update_schema.fields}

                for field_name, create_field in create_fields.items():
                    if field_name not in update_fields and field_name != "id":
                        # 这是一个潜在问题
                        if create_field.is_nested_list:
                            self.issues.append(
                                Issue(
                                    severity="ERROR",
                                    module=module_name,
                                    category="Update Schema 完整性",
                                    message=f"Update schema '{update_schema.class_name}' 缺少嵌套字段 '{field_name}'",
                                    file=update_schema.file,
                                    suggestion=f"添加字段：{field_name}: Optional[List[{create_field.nested_type}]] = None",
                                )
                            )
                        elif not field_name.endswith("_id"):
                            self.issues.append(
                                Issue(
                                    severity="WARNING",
                                    module=module_name,
                                    category="Update Schema 完整性",
                                    message=f"Update schema '{update_schema.class_name}' 缺少字段 '{field_name}'",
                                    file=update_schema.file,
                                    suggestion=f"考虑添加字段：{field_name}: Optional[{create_field.field_type}] = None",
                                )
                            )

    def check_serialization_aliases(self):
        """检查 serialization_alias 使用"""
        for module_name, schemas in self.schemas.items():
            for schema in schemas:
                for field in schema.fields:
                    if field.serialization_alias:
                        # 检查是否导致前后端不一致
                        if field.name != field.serialization_alias:
                            self.issues.append(
                                Issue(
                                    severity="WARNING",
                                    module=module_name,
                                    category="字段名一致性",
                                    message=f"Schema '{schema.class_name}.{field.name}' 使用 serialization_alias='{field.serialization_alias}'",
                                    file=schema.file,
                                    suggestion="确保前端使用正确的字段名，或考虑使用 alias 代替",
                                )
                            )

    def check_nested_object_handling(self):
        """检查 Endpoint 是否正确处理嵌套对象"""
        for module_name, endpoints in self.endpoints.items():
            for endpoint in endpoints:
                if endpoint.has_update_logic and not endpoint.handles_nested_objects:
                    # 检查对应的 schema 是否有嵌套字段
                    if module_name in self.schemas:
                        for schema in self.schemas[module_name]:
                            if schema.schema_type == "Update":
                                nested_fields = [
                                    f for f in schema.fields if f.is_nested_list
                                ]
                                if nested_fields:
                                    # 检查 schema 中是否定义了嵌套字段但 endpoint 未处理
                                    self.issues.append(
                                        Issue(
                                            severity="ERROR",
                                            module=module_name,
                                            category="嵌套对象处理",
                                            message=f"Endpoint '{endpoint.function_name}' 可能未处理嵌套字段: {', '.join([f.name for f in nested_fields])}",
                                            file=endpoint.file,
                                            suggestion="在 endpoint 中添加嵌套对象的创建/更新/删除逻辑",
                                        )
                                    )

    def check_field_consistency(self):
        """检查字段名一致性"""
        for module_name, schemas in self.schemas.items():
            response_schemas = [s for s in schemas if s.schema_type == "Response"]

            for schema in response_schemas:
                for field in schema.fields:
                    # 检查是否有 alias
                    if field.alias and field.alias != field.name:
                        self.issues.append(
                            Issue(
                                severity="INFO",
                                module=module_name,
                                category="字段映射",
                                message=f"Schema '{schema.class_name}.{field.name}' 使用 alias='{field.alias}'",
                                file=schema.file,
                                suggestion=f"前端将收到字段名 '{field.alias}' 而非 '{field.name}'",
                            )
                        )

    def print_report(self):
        """打印审查报告"""
        print("\n" + "=" * 80)
        print("📊 API Schema 审查报告")
        print("=" * 80 + "\n")

        # 按严重程度分组
        errors = [i for i in self.issues if i.severity == "ERROR"]
        warnings = [i for i in self.issues if i.severity == "WARNING"]
        infos = [i for i in self.issues if i.severity == "INFO"]

        print(f"📈 统计:")
        print(f"  - ERROR:   {len(errors)}")
        print(f"  - WARNING: {len(warnings)}")
        print(f"  - INFO:    {len(infos)}")
        print(f"  - 总计：   {len(self.issues)}")
        print()

        if errors:
            print("\n" + "=" * 80)
            print("❌ ERROR (需要立即修复)")
            print("=" * 80)
            for i, issue in enumerate(errors, 1):
                print(f"\n{i}. {issue.message}")
                print(f"   模块：{issue.module}")
                print(f"   分类：{issue.category}")
                print(f"   文件：{issue.file}")
                if issue.line:
                    print(f"   行号：{issue.line}")
                if issue.suggestion:
                    print(f"   💡 建议：{issue.suggestion}")

        if warnings:
            print("\n" + "=" * 80)
            print("⚠️  WARNING (建议修复)")
            print("=" * 80)
            for i, issue in enumerate(warnings, 1):
                print(f"\n{i}. {issue.message}")
                print(f"   模块：{issue.module}")
                print(f"   分类：{issue.category}")
                print(f"   文件：{issue.file}")
                if issue.suggestion:
                    print(f"   💡 建议：{issue.suggestion}")

        if infos:
            print("\n" + "=" * 80)
            print("ℹ️  INFO (信息)")
            print("=" * 80)
            for i, issue in enumerate(infos, 1):
                print(f"\n{i}. {issue.message}")
                print(f"   模块：{issue.module}")
                print(f"   文件：{issue.file}")
                if issue.suggestion:
                    print(f"   💡 提示：{issue.suggestion}")

        print("\n" + "=" * 80)
        print("审查完成")
        print("=" * 80 + "\n")


def main():
    reviewer = APISchemaReviewer()

    print("=" * 80)
    print("🔍 API Schema 完整性审查工具")
    print("=" * 80)
    print()

    # 扫描
    reviewer.scan_all()

    # 分析
    reviewer.analyze()

    # 打印报告
    reviewer.print_report()

    # 返回退出码
    errors = len([i for i in reviewer.issues if i.severity == "ERROR"])
    return 1 if errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
