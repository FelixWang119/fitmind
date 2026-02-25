"""通知模板渲染器"""

import logging
from typing import Any, Dict, Optional

from jinja2 import Template, TemplateError
from sqlalchemy.orm import Session

from app.models.notification import NotificationTemplate

logger = logging.getLogger(__name__)


class TemplateRenderer:
    """通知模板渲染器"""

    def __init__(self, db: Session):
        self.db = db

    def render(
        self,
        template_code: str,
        variables: Dict[str, Any],
        language: str = "zh-CN",
    ) -> Optional[Dict[str, Any]]:
        """
        渲染通知模板

        Args:
            template_code: 模板代码（如 'habit_completed'）
            variables: 模板变量（如 {'habit_name': '晨跑', 'streak_days': 7}）
            language: 语言（预留，当前只支持中文）

        Returns:
            {'title': '...', 'content': '...', 'template_id': '...'}
            如果模板不存在或渲染失败，返回 None
        """
        # 1. 查询模板
        template = self._get_template(template_code, language)

        if not template:
            logger.warning(
                f"Template not found: {template_code} (language: {language})"
            )
            return self._get_fallback_content(template_code)

        # 2. 验证模板是否启用
        if not template.is_active:
            logger.warning(f"Template is not active: {template_code}")
            return self._get_fallback_content(template_code)

        # 3. 渲染模板
        try:
            title = self._render_template(template.title_template, variables)
            content = self._render_template(template.content_template, variables)
        except TemplateError as e:
            logger.error(f"Template render failed: {e}")
            return self._get_fallback_content(template_code)
        except Exception as e:
            logger.error(f"Unexpected error rendering template: {e}")
            return self._get_fallback_content(template_code)

        return {
            "title": title,
            "content": content,
            "template_id": template.id,
            "template_code": template_code,
        }

    def _get_template(
        self, template_code: str, language: str
    ) -> Optional[NotificationTemplate]:
        """获取模板"""
        # 当前只支持中文，预留多语言支持
        return (
            self.db.query(NotificationTemplate)
            .filter(
                NotificationTemplate.code == template_code,
                NotificationTemplate.is_active == True,
            )
            .first()
        )

    def _render_template(self, template_str: str, variables: Dict[str, Any]) -> str:
        """渲染单个模板字符串"""
        template = Template(template_str)
        return template.render(**variables)

    def _get_fallback_content(self, template_code: str) -> Dict[str, Any]:
        """兜底内容"""
        return {
            "title": "FitMind 通知",
            "content": "你有一条新的通知",
            "template_id": None,
            "template_code": template_code,
        }

    def validate_template(self, template_code: str, variables: Dict[str, Any]) -> bool:
        """
        验证模板变量是否匹配

        Args:
            template_code: 模板代码
            variables: 提供的变量

        Returns:
            bool: 变量是否匹配
        """
        template = self._get_template(template_code, "zh-CN")
        if not template:
            return False

        if not template.variables:
            # 没有定义变量，任何变量都可以
            return True

        required_vars = {var["name"] for var in template.variables}
        provided_vars = set(variables.keys())

        missing_vars = required_vars - provided_vars
        if missing_vars:
            logger.warning(
                f"Missing variables for template {template_code}: {missing_vars}"
            )
            return False

        return True
