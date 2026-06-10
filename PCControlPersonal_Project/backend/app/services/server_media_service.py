import logging
import tempfile
import time
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..config import get_settings
from .file_service import create_asset_from_bytes
from .log_service import add_log


settings = get_settings()
logger = logging.getLogger("server-media")


def _write_error(message: str) -> None:
    try:
        path = Path(settings.logs_dir) / "errors.log"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {message}\n")
    except Exception:
        logger.exception("Не удалось записать logs/errors.log")


def create_server_screenshot(db: Session, source: str = "api"):
    if not settings.enable_server_screenshot:
        raise HTTPException(status_code=403, detail="Скрин экрана сервера выключен в .env")
    try:
        from PIL import ImageGrab

        image = ImageGrab.grab()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp_path = Path(tmp.name)
        try:
            image.save(tmp_path)
            asset = create_asset_from_bytes(
                db,
                tmp_path.read_bytes(),
                "server_screen.png",
                "server_screenshot",
                "server",
                description=f"Скрин экрана сервера, источник: {source}",
                mime_type="image/png",
            )
            add_log(
                db,
                "info",
                "server",
                "server_screenshot_created",
                "Создан скрин экрана сервера",
                {"file_id": asset.id, "source": source},
            )
            return asset
        finally:
            tmp_path.unlink(missing_ok=True)
    except HTTPException:
        raise
    except Exception as exc:
        message = "На сервере нет активного графического экрана"
        _write_error(f"{message}: {exc}")
        add_log(db, "error", "server", "server_screenshot_failed", message, {"error": str(exc), "source": source})
        raise HTTPException(status_code=409, detail=message) from exc


def create_server_webcam_photo(db: Session, source: str = "api"):
    if not settings.enable_server_webcam:
        raise HTTPException(status_code=403, detail="Веб-камера сервера выключена в .env")
    try:
        import cv2

        add_log(
            db,
            "warning",
            "server",
            "server_webcam_photo_started",
            "Запрошено фото с веб-камеры сервера",
            {"source": source},
        )
        cap = cv2.VideoCapture(0)
        try:
            if not cap.isOpened():
                raise RuntimeError("Камера не найдена")
            ok, frame = cap.read()
            if not ok:
                raise RuntimeError("Не удалось получить кадр с камеры")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp_path = Path(tmp.name)
            try:
                cv2.imwrite(str(tmp_path), frame)
                asset = create_asset_from_bytes(
                    db,
                    tmp_path.read_bytes(),
                    "server_webcam.jpg",
                    "server_webcam_photo",
                    "server",
                    description=f"Фото с веб-камеры сервера, источник: {source}",
                    mime_type="image/jpeg",
                )
                add_log(
                    db,
                    "info",
                    "server",
                    "server_webcam_photo_created",
                    "Фото с веб-камеры сервера создано",
                    {"file_id": asset.id, "source": source},
                )
                return asset
            finally:
                tmp_path.unlink(missing_ok=True)
        finally:
            cap.release()
    except HTTPException:
        raise
    except Exception as exc:
        message = f"Не удалось сделать фото с веб-камеры сервера: {exc}"
        _write_error(message)
        add_log(db, "error", "server", "server_webcam_photo_failed", message, {"source": source})
        raise HTTPException(status_code=409, detail=message) from exc


def create_server_webcam_video(db: Session, duration_seconds: int = 10, source: str = "api"):
    if not settings.enable_server_webcam_video:
        raise HTTPException(status_code=403, detail="Запись видео с веб-камеры сервера выключена в .env")
    duration_seconds = max(1, min(int(duration_seconds or 10), settings.max_server_webcam_video_seconds))
    try:
        import cv2

        add_log(
            db,
            "warning",
            "server",
            "server_webcam_record_started",
            "Началась запись видео с веб-камеры сервера",
            {"duration": duration_seconds, "source": source},
        )
        cap = cv2.VideoCapture(0)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp_path = Path(tmp.name)
        try:
            if not cap.isOpened():
                raise RuntimeError("Камера не найдена")
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)
            fps = 15.0
            writer = cv2.VideoWriter(str(tmp_path), cv2.VideoWriter_fourcc(*"VP80"), fps, (width, height))
            if not writer.isOpened():
                raise RuntimeError("Не удалось открыть видеокодек WebM/VP8")
            try:
                end_at = time.time() + duration_seconds
                while time.time() < end_at:
                    ok, frame = cap.read()
                    if ok:
                        writer.write(frame)
                    time.sleep(max(0, (1 / fps) - 0.005))
            finally:
                writer.release()
            asset = create_asset_from_bytes(
                db,
                tmp_path.read_bytes(),
                "server_webcam.webm",
                "server_webcam_video",
                "server",
                description=f"Видео с веб-камеры сервера {duration_seconds}s, источник: {source}",
                mime_type="video/webm",
            )
            add_log(
                db,
                "info",
                "server",
                "server_webcam_record_done",
                "Видео с веб-камеры сервера сохранено",
                {"file_id": asset.id, "duration": duration_seconds, "source": source},
            )
            return asset
        finally:
            cap.release()
            tmp_path.unlink(missing_ok=True)
    except HTTPException:
        raise
    except Exception as exc:
        message = f"Не удалось записать видео с веб-камеры сервера: {exc}"
        _write_error(message)
        add_log(db, "error", "server", "server_webcam_record_failed", message, {"source": source})
        raise HTTPException(status_code=409, detail=message) from exc
