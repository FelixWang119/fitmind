"""软删除 Mixin

为模型提供软删除功能，包括：
- deleted_at: 删除时间戳（NULL 表示未删除）
- is_deleted: 布尔标记
- deleted_by: 删除者 ID（可选）
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, Boolean, Integer
from sqlalchemy.orm import Query
from typing import TypeVar, Type

Base = TypeVar("Base")


class SoftDeleteMixin:
    """软删除 Mixin 类

    使用示例:
        class User(SoftDeleteMixin, Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            # ... 其他字段
    """

    deleted_at = Column(DateTime, nullable=True, default=None)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_by = Column(Integer, nullable=True)  # 可选：删除者 ID

    @classmethod
    def filter_not_deleted(cls, query: Query) -> Query:
        """过滤掉已删除的记录

        使用示例:
            query = db.query(User)
            query = User.filter_not_deleted(query)
            users = query.all()
        """
        return query.filter(cls.is_deleted == False, cls.deleted_at == None)

    def soft_delete(self, user_id: int = None) -> None:
        """软删除当前记录

        Args:
            user_id: 执行删除操作的用户 ID（可选）

        使用示例:
            user = db.query(User).first()
            user.soft_delete(user_id=current_user.id)
            db.commit()
        """
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        if user_id is not None:
            self.deleted_by = user_id

    def restore(self) -> None:
        """恢复已删除的记录

        使用示例:
            user = db.query(User).filter(User.is_deleted == True).first()
            user.restore()
            db.commit()
        """
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None

    @classmethod
    def hard_delete(cls, db, id_value: int) -> bool:
        """物理删除记录（慎用！）

        Args:
            db: 数据库会话
            id_value: 记录 ID

        Returns:
            bool: 是否删除成功

        使用示例:
            User.hard_delete(db, user_id)
            db.commit()
        """
        obj = db.query(cls).filter(cls.id == id_value).first()
        if obj:
            db.delete(obj)
            return True
        return False
