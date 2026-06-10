import json
import os
from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
env_file_value = os.environ.get("PCMANAGER_ENV_FILE", "").strip()
if env_file_value:
    DEFAULT_ENV_FILE = Path(env_file_value)
else:
    local_env = BASE_DIR / ".env"
    DEFAULT_ENV_FILE = local_env if local_env.exists() else Path("/etc/pcmanager/pcmanager.env")

DEFAULT_CONFIG_FILE = Path(os.environ.get("PCMANAGER_CONFIG_FILE", "/etc/pcmanager/config.json"))
DEFAULT_DATA_DIR = Path(os.environ.get("PCMANAGER_DATA_DIR", "/var/lib/pcmanager"))
DEFAULT_LOG_DIR = Path(os.environ.get("PCMANAGER_LOG_DIR", "/var/log/pcmanager"))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(DEFAULT_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "PC Control Personal Server"
    app_version: str = "1.0.0"
    latest_agent_version: str = "1.7.0"
    environment: str = "development"
    debug: bool = False

    server_host: str = "0.0.0.0"
    server_port: int = 8765
    base_public_url: str = "http://127.0.0.1:8765"
    trusted_origins: list[str] = Field(default_factory=lambda: ["*"])
    local_only: bool = True

    config_file: str = str(DEFAULT_CONFIG_FILE)
    data_dir: str = str(DEFAULT_DATA_DIR)
    logs_dir: str = str(DEFAULT_LOG_DIR)
    storage_dir: str = str(DEFAULT_DATA_DIR / "storage")
    database_url: str = f"sqlite:///{(DEFAULT_DATA_DIR / 'server.db').as_posix()}"

    admin_token: str = "change-me-admin-token"
    server_access_key: str = "change-me-server-access-key"
    jwt_secret: str = "change-me-jwt-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 10080

    telegram_bot_token: str = ""
    telegram_owner_id: int = 0
    telegram_allowed_user_ids: str = ""
    telegram_bot_enabled: bool = True
    start_telegram_bot_with_server: bool = False

    agent_bootstrap_token: str = "change-me-agent-bootstrap-token"
    enable_screenshot: bool = False
    enable_camera: bool = False
    enable_video_recording: bool = False
    enable_process_kill: bool = False
    enable_server_screenshot: bool = False
    enable_server_webcam: bool = False
    enable_server_webcam_video: bool = False
    max_server_webcam_video_seconds: int = 10
    allow_dangerous_commands: bool = False
    allowed_script_names: str = "cleanup_temp,collect_diagnostics"

    task_timeout_seconds: int = 300
    safe_retry_count: int = 2
    max_result_bytes: int = 512000
    api_rate_limit_per_minute: int = 120
    max_upload_mb: int = 200
    max_video_seconds: int = 30
    allowed_upload_extensions: str = (
        ".jpg,.jpeg,.png,.gif,.webp,"
        ".mp4,.webm,.mov,.avi,.mkv,"
        ".mp3,.wav,.ogg,.m4a,"
        ".txt,.log,.csv,.json,.pdf,"
        ".doc,.docx,.xls,.xlsx,.ppt,.pptx,"
        ".zip,.7z,.rar,.apk,.exe"
    )
    wol_devices: str = ""
    wol_broadcast: str = Field(default="255.255.255.255", validation_alias=AliasChoices("WOL_BROADCAST", "WOL_BROADCAST_IP"))
    wol_port: int = 9
    local_check_notify_ok: bool = False
    temp_warning_c: int = 85
    temp_critical_c: int = 90
    log_retention_days: int = 14
    backup_retention_days: int = 30
    backup_keep_last: int = 5
    metrics_retention_days: int = 30
    metrics_collect_interval_min: int = 5
    network_scan_subnet: str = "192.168.0.0/24"
    telegram_notify_events: bool = True
    telegram_notify_info: bool = False

    @property
    def allowed_scripts(self) -> set[str]:
        return {item.strip() for item in self.allowed_script_names.split(",") if item.strip()}

    @property
    def allowed_upload_exts(self) -> set[str]:
        return {item.strip().lower() for item in self.allowed_upload_extensions.split(",") if item.strip()}

    @property
    def allowed_telegram_ids(self) -> set[int]:
        raw = self.telegram_allowed_user_ids or str(self.telegram_owner_id or "")
        values: set[int] = set()
        for item in raw.split(","):
            item = item.strip()
            if item.isdigit():
                values.add(int(item))
        return values

    @property
    def wol_device_map(self) -> dict[str, str]:
        devices: dict[str, str] = {}
        for item in self.wol_devices.split(","):
            if not item.strip() or "=" not in item:
                continue
            name, mac = item.split("=", 1)
            name = name.strip()
            mac = mac.strip().lower()
            if name and mac:
                devices[name] = mac
        return devices

    def apply_json_config(self) -> "Settings":
        path = Path(self.config_file)
        if not path.exists():
            return self
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return self
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self


@lru_cache
def get_settings() -> Settings:
    settings = Settings().apply_json_config()
    Path(settings.data_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.logs_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.storage_dir).mkdir(parents=True, exist_ok=True)
    return settings
