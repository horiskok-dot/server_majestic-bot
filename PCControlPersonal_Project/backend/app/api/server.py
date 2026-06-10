from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..auth import get_admin_or_access_key
from ..database import get_db
from ..models import Agent, FileAsset
from ..services.agent_service import agent_to_mobile, compute_agent_status
from ..services.file_service import asset_path, get_asset_or_404
from ..services.network_service import server_info
from ..services.server_media_service import create_server_screenshot, create_server_webcam_photo, create_server_webcam_video


router = APIRouter(tags=["server"], dependencies=[Depends(get_admin_or_access_key)])


@router.get("/api/server/info")
def info():
    return server_info()


@router.get("/api/server/network")
def network():
    data = server_info()
    return {
        "local_ip": data["local_ip"],
        "public_url": data["public_url"],
        "base_url": data["base_url"],
        "websocket_url": data["websocket_url"],
    }


@router.get("/api/agents/{agent_id}")
def agent_details(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Агент не найден")
    return agent_to_mobile(agent)


@router.get("/api/agents/{agent_id}/network")
def agent_network(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Агент не найден")
    return {
        "agent_id": agent.agent_id,
        "status": compute_agent_status(agent),
        "local_ip": agent.local_ip,
        "public_ip": agent.public_ip,
        "connection_ip": agent.connection_ip,
        "network_info": agent.network_info,
    }


@router.post("/api/server/screenshot")
def server_screenshot(db: Session = Depends(get_db)):
    return create_server_screenshot(db, "api")


@router.get("/api/server/screenshots")
def server_screenshots(db: Session = Depends(get_db)):
    return (
        db.query(FileAsset)
        .filter(FileAsset.public_type == "server_screenshot", FileAsset.is_active == True)  # noqa: E712
        .order_by(FileAsset.created_at.desc())
        .limit(100)
        .all()
    )


@router.get("/api/server/screenshots/{file_id}/download")
def download_server_screenshot(file_id: int, db: Session = Depends(get_db)):
    asset = get_asset_or_404(db, file_id)
    if asset.public_type != "server_screenshot":
        raise HTTPException(status_code=400, detail="Это не скрин экрана сервера")
    return FileResponse(asset_path(asset), media_type=asset.mime_type, filename=asset.original_filename or asset.filename)


@router.post("/api/server/webcam/photo")
def server_webcam_photo(confirmed: bool = Query(default=False), db: Session = Depends(get_db)):
    if not confirmed:
        raise HTTPException(status_code=400, detail="Для фото с веб-камеры сервера нужно подтверждение")
    return create_server_webcam_photo(db, "api")


@router.get("/api/server/webcam/photos")
def server_webcam_photos(db: Session = Depends(get_db)):
    return (
        db.query(FileAsset)
        .filter(FileAsset.public_type == "server_webcam_photo", FileAsset.is_active == True)  # noqa: E712
        .order_by(FileAsset.created_at.desc())
        .limit(100)
        .all()
    )


@router.get("/api/server/webcam/photos/{file_id}/download")
def download_server_webcam_photo(file_id: int, db: Session = Depends(get_db)):
    asset = get_asset_or_404(db, file_id)
    if asset.public_type != "server_webcam_photo":
        raise HTTPException(status_code=400, detail="Это не фото с веб-камеры сервера")
    return FileResponse(asset_path(asset), media_type=asset.mime_type, filename=asset.original_filename or asset.filename)


@router.post("/api/server/webcam/record")
def server_webcam_record(duration_seconds: int = Query(default=10), confirmed: bool = Query(default=False), db: Session = Depends(get_db)):
    if not confirmed:
        raise HTTPException(status_code=400, detail="Для записи видео с веб-камеры сервера нужно подтверждение")
    return create_server_webcam_video(db, duration_seconds, "api")
