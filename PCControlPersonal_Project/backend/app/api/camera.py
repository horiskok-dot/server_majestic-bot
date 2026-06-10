from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_current_admin
from ..config import get_settings
from ..database import get_db
from ..models import Agent
from ..services.task_service import create_task


router = APIRouter(tags=["camera"], dependencies=[Depends(get_current_admin)])
settings = get_settings()


@router.post("/api/agents/{agent_id}/camera/photo")
def camera_photo(agent_id: str, db: Session = Depends(get_db)):
    if not settings.enable_camera:
        raise HTTPException(status_code=403, detail="Camera is disabled on server")
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if not agent.camera_enabled:
        raise HTTPException(status_code=403, detail="Camera is disabled on agent")
    return create_task(db, agent, "camera_snapshot", {"save_to_server": True}, "api", confirmed=True)


@router.post("/api/agents/{agent_id}/camera/record")
def record_video(agent_id: str, duration_seconds: int = 5, db: Session = Depends(get_db)):
    if not settings.enable_video_recording:
        raise HTTPException(status_code=403, detail="Video recording is disabled on server")
    duration_seconds = max(1, min(duration_seconds, settings.max_video_seconds))
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if not agent.video_enabled:
        raise HTTPException(status_code=403, detail="Video recording is disabled on agent")
    return create_task(db, agent, "record_video", {"duration_seconds": duration_seconds, "save_to_server": True}, "api", confirmed=True)
