import io
import os
import uuid
from datetime import date
from typing import Optional
from pathlib import Path

import structlog
from PIL import Image

from app.core.config import settings

logger = structlog.get_logger(__name__)


class ImageService:
    """图片处理服务"""

    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.max_size = settings.IMAGE_MAX_SIZE  # 10MB
        self.compress_quality = settings.IMAGE_COMPRESS_QUALITY  # 70

    def _ensure_upload_dir(self, user_id: int) -> Path:
        """确保用户上传目录存在"""
        # 按照 年/月 组织目录
        today = date.today()
        user_dir = (
            self.upload_dir / str(user_id) / str(today.year) / f"{today.month:02d}"
        )
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    def _generate_filename(self, original_filename: str) -> str:
        """生成唯一文件名"""
        ext = Path(original_filename).suffix.lower()
        # 限制扩展名
        if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            ext = ".jpg"
        unique_id = str(uuid.uuid4())[:8]
        return f"{unique_id}{ext}"

    async def save_image(
        self, user_id: int, file_content: bytes, original_filename: str
    ) -> str:
        """
        保存用户上传的图片

        Args:
            user_id: 用户ID
            file_content: 图片二进制内容
            original_filename: 原始文件名

        Returns:
            保存后的文件路径（相对于上传目录）
        """
        # 检查文件大小
        if len(file_content) > self.max_size:
            # 先压缩再保存
            file_content = self._compress_image(file_content)

        # 生成唯一文件名
        filename = self._generate_filename(original_filename)

        # 确保目录存在
        user_dir = self._ensure_upload_dir(user_id)
        file_path = user_dir / filename

        # 保存文件
        with open(file_path, "wb") as f:
            f.write(file_content)

        logger.info(
            "Image saved", user_id=user_id, filename=filename, size=len(file_content)
        )

        # 返回相对路径
        relative_path = (
            f"{user_id}/{date.today().year}/{date.today().month:02d}/{filename}"
        )
        return relative_path

    def _compress_image(self, image_content: bytes) -> bytes:
        """
        压缩图片

        Args:
            image_content: 原始图片二进制

        Returns:
            压缩后的图片二进制
        """
        try:
            img = Image.open(io.BytesIO(image_content))

            # 转换为 RGB 模式（如果需要）
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # 压缩
            output = io.BytesIO()
            img.save(
                output, format="JPEG", quality=self.compress_quality, optimize=True
            )
            compressed = output.getvalue()

            logger.info(
                "Image compressed",
                original_size=len(image_content),
                compressed_size=len(compressed),
            )
            return compressed

        except Exception as e:
            logger.warning("Image compression failed, using original", error=str(e))
            return image_content

    def get_image_path(self, relative_path: str) -> Optional[Path]:
        """获取图片完整路径"""
        full_path = self.upload_dir / relative_path
        if full_path.exists():
            return full_path
        return None

    def get_image_url(self, relative_path: str) -> str:
        """获取图片访问URL"""
        # 这里返回相对路径，前端需要配置静态文件服务
        return f"/uploads/meal_photos/{relative_path}"

    async def compress_old_images(self) -> int:
        """
        压缩超过指定大小的旧图片

        Returns:
            压缩的图片数量
        """
        compressed_count = 0
        threshold_size = 1024 * 1024  # 1MB

        try:
            for user_dir in self.upload_dir.iterdir():
                if not user_dir.is_dir():
                    continue

                for file_path in user_dir.rglob("*.jpg"):
                    if file_path.stat().st_size > threshold_size:
                        try:
                            with open(file_path, "rb") as f:
                                content = f.read()

                            compressed = self._compress_image(content)

                            with open(file_path, "wb") as f:
                                f.write(compressed)

                            compressed_count += 1
                            logger.info("Old image compressed", path=str(file_path))

                        except Exception as e:
                            logger.warning(
                                "Failed to compress old image",
                                path=str(file_path),
                                error=str(e),
                            )

        except Exception as e:
            logger.error("Error iterating upload directory", error=str(e))

        logger.info("Old images compression completed", count=compressed_count)
        return compressed_count


# 全局服务实例
_image_service: Optional[ImageService] = None


def get_image_service() -> ImageService:
    """获取图片服务实例"""
    global _image_service
    if _image_service is None:
        _image_service = ImageService()
    return _image_service
