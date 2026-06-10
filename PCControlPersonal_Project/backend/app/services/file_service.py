import mimetypes
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import FileAsset
from ..utils.hashing import sha256_file
from ..utils.paths import public_type_dir, safe_filename
from .log_service import add_log


settings = get_settings()


def validate_upload_name(filename: str) -> None:
    ext = Path(filename or "").suffix.lower()
    if ext and ext not in settings.allowed_upload_exts:
        raise HTTPException(status_code=400, detail=f"Extension {ext} is not allowed")


def create_asset_from_bytes(
    db: Session,
    data: bytes,
    original_filename: str,
    public_type: str,
    source: str,
    agent_id: str | None = None,
    description: str = "",
    mime_type: str | None = None,
) -> FileAsset:
    validate_upload_name(original_filename)
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(status_code=413, detail="File is too large")
    filename = safe_filename(original_filename)
    target = public_type_dir(public_type) / filename
    target.write_bytes(data)
    asset = FileAsset(
        filename=filename,
        original_filename=Path(original_filename).name,
        stored_path=str(target),
        public_type=public_type,
        size_bytes=target.stat().st_size,
        sha256=sha256_file(target),
        mime_type=mime_type or mimetypes.guess_type(original_filename)[0] or "application/octet-stream",
        source=source,
        agent_id=agent_id,
        description=description,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    add_log(db, "info", "files", "file_uploaded", f"Stored file {asset.filename}", {"file_id": asset.id, "type": public_type, "agent_id": agent_id})
    return asset


async def create_asset_from_upload(
    db: Session,
    upload: UploadFile,
    public_type: str,
    source: str,
    agent_id: str | None = None,
    description: str = "",
) -> FileAsset:
    data = await upload.read(settings.max_upload_mb * 1024 * 1024 + 1)
    return create_asset_from_bytes(db, data, upload.filename or "upload.bin", public_type, source, agent_id, description, upload.content_type)


def get_asset_or_404(db: Session, file_id: int) -> FileAsset:
    asset = db.query(FileAsset).filter(FileAsset.id == file_id, FileAsset.is_active == True).first()  # noqa: E712
    if not asset:
        raise HTTPException(status_code=404, detail="File not found")
    return asset


def asset_path(asset: FileAsset) -> Path:
    path = Path(asset.stored_path).resolve()
    root = Path(settings.storage_dir).resolve()
    if not str(path).startswith(str(root)) or not path.exists():
        raise HTTPException(status_code=404, detail="Stored file not found")
    return path
