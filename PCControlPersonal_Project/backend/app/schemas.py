from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TokenRequest(BaseModel):
    admin_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    time: datetime


class AgentRegisterRequest(BaseModel):
    agent_id: str
    name: str
    version: str = "unknown"
    platform: str = "Windows"
    hostname: str = ""
    username: str = ""
    os_name: str = ""
    local_ip: str = ""
    public_ip: str = ""
    screenshot_enabled: bool = False
    camera_enabled: bool = False
    video_enabled: bool = False


class AgentHeartbeatRequest(BaseModel):
    status: str = "online"
    latency_ms: int = 0
    current_task: str = ""
    system_info: dict[str, Any] = Field(default_factory=dict)
    disk_info: dict[str, Any] = Field(default_factory=dict)
    network_info: dict[str, Any] = Field(default_factory=dict)
    process_info: dict[str, Any] = Field(default_factory=dict)
    last_error: str = ""


class TaskCreate(BaseModel):
    agent_id: str
    action: str | None = None
    task_type: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    confirmed: bool = False
    request_id: str | None = None
    timeout_seconds: int | None = None


class FileAssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    original_filename: str
    public_type: str
    size_bytes: int
    sha256: str
    mime_type: str
    source: str
    agent_id: str | None = None
    description: str = ""
    is_active: bool
    created_at: datetime


class TaskResultUpdate(BaseModel):
    status: str
    result: str = ""
    error: str = ""


class DashboardResponse(BaseModel):
    server_status: str
    uptime: str
    agents_total: int
    agents_online: int
    active_tasks: int
    last_errors: list[str]


class AgentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    agent_id: str
    name: str
    status: str
    version: str
    platform: str
    local_ip: str
    latency_ms: int
    current_task: str
    last_error: str
    screenshot_enabled: bool
    last_seen_at: datetime | None


class AgentActivateRequest(BaseModel):
    activation_key: str
    hostname: str = ""
    username: str = ""
    platform: str = "Windows"
    os_name: str = ""
    local_ip: str = ""
