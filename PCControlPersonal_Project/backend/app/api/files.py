from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..auth import get_access_key_admin, get_current_admin, get_agent_from_token
from ..database import get_db
from ..models import Agent, FileAsset
from ..schemas import FileAssetRead
from ..services.file_service import asset_path, create_asset_from_upload, get_asset_or_404
from ..services.log_service import add_log


router = APIRouter(tags=["files"])


def _auth(_: str = Depends(get_current_admin)) -> None:
    return None


@router.post("/api/files/upload", response_model=FileAssetRead, dependencies=[Depends(_auth)])
async def upload_file(
    public_type: str = Query(default="upload"),
    description: str = Query(default=""),
    upload: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return await create_asset_from_upload(db, upload, public_type, "web", description=description)


@router.post("/api/agents/files/upload", response_model=FileAssetRead)
async def upload_agent_file(
    public_type: str = Query(default="upload"),
    description: str = Query(default=""),
    upload: UploadFile = File(...),
    agent: Agent = Depends(get_agent_from_token),
    db: Session = Depends(get_db),
):
    return await create_asset_from_upload(db, upload, public_type, "agent", agent.agent_id, description)


@router.get("/api/files", response_model=list[FileAssetRead], dependencies=[Depends(get_access_key_admin)])
def list_files(public_type: str | None = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(FileAsset).filter(FileAsset.is_active == True).order_by(FileAsset.created_at.desc())  # noqa: E712
    if public_type:
        query = query.filter(FileAsset.public_type == public_type)
    return query.limit(300).all()


@router.get("/api/files/categories", dependencies=[Depends(get_access_key_admin)])
def categories():
    return [
        "upload",
        "telegram_file",
        "server_screenshot",
        "agent_screenshot",
        "server_webcam_photo",
        "agent_camera_photo",
        "server_webcam_video",
        "agent_camera_video",
    ]


@router.get("/api/files/photos", response_model=list[FileAssetRead], dependencies=[Depends(get_access_key_admin)])
def photos(db: Session = Depends(get_db)):
    return db.query(FileAsset).filter(FileAsset.public_type.in_(["server_webcam_photo", "agent_camera_photo", "photo"]), FileAsset.is_active == True).order_by(FileAsset.created_at.desc()).limit(300).all()  # noqa: E712


@router.get("/api/files/screenshots", response_model=list[FileAssetRead], dependencies=[Depends(get_access_key_admin)])
def screenshots(db: Session = Depends(get_db)):
    return db.query(FileAsset).filter(FileAsset.public_type.in_(["server_screenshot", "agent_screenshot", "screenshot"]), FileAsset.is_active == True).order_by(FileAsset.created_at.desc()).limit(300).all()  # noqa: E712


@router.get("/api/files/videos", response_model=list[FileAssetRead], dependencies=[Depends(get_access_key_admin)])
def videos(db: Session = Depends(get_db)):
    return db.query(FileAsset).filter(FileAsset.public_type.in_(["server_webcam_video", "agent_camera_video", "video"]), FileAsset.is_active == True).order_by(FileAsset.created_at.desc()).limit(300).all()  # noqa: E712


@router.get("/api/files/telegram", response_model=list[FileAssetRead], dependencies=[Depends(get_access_key_admin)])
def telegram_files(db: Session = Depends(get_db)):
    return list_files("telegram_file", db)


@router.get("/api/files/{file_id}", response_model=FileAssetRead, dependencies=[Depends(get_access_key_admin)])
def file_details(file_id: int, db: Session = Depends(get_db)):
    return get_asset_or_404(db, file_id)


@router.get("/api/files/{file_id}/download", dependencies=[Depends(get_access_key_admin)])
def download_file(file_id: int, db: Session = Depends(get_db)):
    asset = get_asset_or_404(db, file_id)
    add_log(db, "info", "files", "file_downloaded", f"Downloaded {asset.filename}", {"file_id": asset.id})
    return FileResponse(asset_path(asset), media_type=asset.mime_type, filename=asset.original_filename or asset.filename)


@router.delete("/api/files/{file_id}", dependencies=[Depends(get_current_admin)])
def delete_file(file_id: int, db: Session = Depends(get_db)):
    asset = get_asset_or_404(db, file_id)
    asset.is_active = False
    db.add(asset)
    db.commit()
    add_log(db, "warning", "files", "file_deleted", f"Deleted {asset.filename}", {"file_id": asset.id})
    return {"ok": True}
