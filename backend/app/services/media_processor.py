from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from PIL import Image, ExifTags

logger = logging.getLogger(__name__)


def generate_image_thumbnail(
    input_path: Path, output_path: Path, max_size: int = 400, quality: int = 85
) -> bool:
    """生成图片缩略图：先修正 EXIF 旋转方向，缩放至 max_size 以内，以 JPEG 格式保存。

    RGBA/P 模式先转 RGB 以兼容 JPEG 编码；成功返回 True，失败返回 False。
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(input_path) as img:
            img = _apply_exif_orientation(img)
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(output_path, "JPEG", quality=quality)
        return True
    except Exception:
        logger.exception("Failed to generate image thumbnail for %s", input_path)
        return False


def convert_heic_to_jpeg(input_path: Path, output_path: Path) -> bool:
    """将 HEIC/HEIF 文件转换为高质量 JPEG（质量 95），依赖 pillow-heif 插件。"""
    try:
        import pillow_heif

        pillow_heif.register_heif_opener()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(input_path) as img:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(output_path, "JPEG", quality=95)
        return True
    except Exception:
        logger.exception("Failed to convert HEIC to JPEG for %s", input_path)
        return False


def extract_exif_date(file_path: Path) -> Optional[str]:
    """从图片 EXIF 中提取 DateTimeOriginal 字段（相机拍摄时间），不存在则返回 None。"""
    try:
        with Image.open(file_path) as img:
            exif_data = img._getexif()
            if not exif_data:
                return None
            for tag_id, value in exif_data.items():
                tag = ExifTags.TAGS.get(tag_id, "")
                if tag == "DateTimeOriginal":
                    return str(value)
        return None
    except Exception:
        logger.debug("No EXIF data in %s", file_path)
        return None


def generate_video_thumbnail(input_path: Path, output_path: Path) -> bool:
    """截取视频第 1 秒处的帧作为缩略图，宽度缩放为 400px，依赖 ffmpeg-python。"""
    try:
        import ffmpeg

        output_path.parent.mkdir(parents=True, exist_ok=True)
        (
            ffmpeg.input(str(input_path), ss=1)
            .filter("scale", 400, -1)
            .output(str(output_path), vframes=1)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        return output_path.exists()
    except Exception:
        logger.exception("Failed to generate video thumbnail for %s", input_path)
        return False


def _apply_exif_orientation(img: Image.Image) -> Image.Image:
    """读取图片 EXIF Orientation 字段，将图片旋转/翻转至正确方向后返回。

    处理常见的 8 种旋转方向（3/6/8 纯旋转，2/4/5/7 含镜像翻转）；
    读取失败时静默返回原始图片对象。
    """
    try:
        exif = img._getexif()
        if not exif:
            return img
        orientation_key = None
        for k, v in ExifTags.TAGS.items():
            if v == "Orientation":
                orientation_key = k
                break
        if orientation_key and orientation_key in exif:
            orientation = exif[orientation_key]
            rotations = {3: 180, 6: 270, 8: 90}
            if orientation in rotations:
                img = img.rotate(rotations[orientation], expand=True)
            elif orientation in (2, 4, 5, 7):
                img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                if orientation in (5, 7):
                    remaining = {5: 270, 7: 90}
                    img = img.rotate(remaining[orientation], expand=True)
    except Exception:
        pass
    return img
