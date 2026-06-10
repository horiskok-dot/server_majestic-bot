import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_current_admin
from ..database import get_db
from ..models import Agent, Task
from ..services.task_service import create_task


router = APIRouter(tags=["processes"], dependencies=[Depends(get_current_admin)])


@router.get("/api/agents/{agent_id}/processes")
def get_processes(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    task = db.query(Task).filter(Task.agent_id == agent_id, Task.action == "get_process_list", Task.status.in_(["success", "done"])).order_by(Task.finished_at.desc(), Task.created_at.desc()).first()
    if task and task.result:
        try:
            return json.loads(task.result)
        except Exception:
            return []
    return agent.process_info.get("items", []) if isinstance(agent.process_info, dict) else []


@router.post("/api/agents/{agent_id}/processes/refresh")
def refresh_processes(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return create_task(db, agent, "get_process_list", {}, "api")
