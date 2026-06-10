from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..auth import get_access_key_admin, get_current_admin
from ..config import get_settings
from ..database import get_db
from ..models import Agent, FileAsset
from ..services.file_service import asset_path, get_asset_or_404
from ..services.task_service import create_task


router = APIRouter(tags=["screenshots"])
settings = get_settings()


@router.post("/api/agents/{agent_id}/screenshot", dependencies=[Depends(get_current_admin)])
def take_screenshot(agent_id: str, db: Session = Depends(get_db)):
    if not settings.enable_screenshot:
        raise HTTPException(status_code=403, detail="Screenshots are disabled on server")
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if not agent.screenshot_enabled:
        raise HTTPException(status_code=403, detail="Screenshots are disabled on agent")
    return create_task(db, agent, "take_screenshot", {"save_to_server": True, "quality": 80}, "api")


@router.get("/api/screenshots", dependencies=[Depends(get_access_key_admin)])
def screenshots(db: Session = Depends(get_db)):
    return db.query(FileAsset).filter(FileAsset.public_type == "screenshot", FileAsset.is_active == True).order_by(FileAsset.created_at.desc()).limit(200).all()  # noqa: E712


@router.get("/api/screenshots/{file_id}/download", dependencies=[Depends(get_access_key_admin)])
def download_screenshot(file_id: int, db: Session = Depends(get_db)):
    asset = get_asset_or_404(db, file_id)
    if asset.public_type != "screenshot":
        raise HTTPException(status_code=400, detail="File is not a screenshot")
    return FileResponse(asset_path(asset), media_type=asset.mime_type, filename=asset.original_filename or asset.filename)
