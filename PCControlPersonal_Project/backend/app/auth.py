from datetime import datetime, timedelta, timezone

from fastapi import Depends, Header, HTTPException, Query, WebSocket, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db
from .models import Agent


settings = get_settings()


def create_access_token(subject: str) -> tuple[str, int]:
    expires = timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": subject, "exp": datetime.now(timezone.utc) + expires}
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, int(expires.total_seconds())


def decode_jwt(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return str(payload.get("sub") or "")
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


class CurrentUser:
    def __init__(self, user_id: int | None, is_admin: bool):
        self.user_id = user_id
        self.is_admin = is_admin


def verify_admin_token(token: str) -> bool:
    return token == settings.admin_token


def verify_server_access_key(token: str) -> bool:
    if not token:
        return False
    if token in {settings.server_access_key, settings.admin_token}:
        return True
    try:
        user_id = find_user_by_activation_key(token)
        return user_id is not None
    except Exception:
        return False


def get_access_key_admin(
    authorization: str = Header(default=""),
    x_pcmanager_key: str = Header(default="", alias="X-PCManager-Key"),
    x_server_access_key: str = Header(default="", alias="X-Server-Access-Key"),
    access_key: str = Query(default=""),
    token: str = Query(default=""),
) -> CurrentUser:
    raw_token = x_server_access_key or x_pcmanager_key or access_key or token
    
    # 1. Bearer Token Auth
    if authorization.lower().startswith("bearer "):
        bearer_token = authorization.split(" ", 1)[1].strip()
        try:
            subject = decode_jwt(bearer_token)
            if subject == "admin":
                return CurrentUser(user_id=None, is_admin=True)
            elif subject.startswith("user:"):
                user_id = int(subject.split(":", 1)[1])
                return CurrentUser(user_id=user_id, is_admin=False)
        except Exception:
            pass

    # 2. Check if raw token is JWT
    if raw_token:
        try:
            subject = decode_jwt(raw_token)
            if subject == "admin":
                return CurrentUser(user_id=None, is_admin=True)
            elif subject.startswith("user:"):
                user_id = int(subject.split(":", 1)[1])
                return CurrentUser(user_id=user_id, is_admin=False)
        except Exception:
            pass

    # 3. Check if raw token is Admin/Global key
    if raw_token in {settings.server_access_key, settings.admin_token}:
        return CurrentUser(user_id=None, is_admin=True)

    # 4. Check database activation key
    if raw_token:
        user_id = find_user_by_activation_key(raw_token)
        if user_id is not None:
            return CurrentUser(user_id=user_id, is_admin=False)

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access key invalid")


def get_admin_or_access_key(
    user: CurrentUser = Depends(get_access_key_admin)
) -> CurrentUser:
    return user


def get_current_admin(authorization: str = Header(default="")) -> str:
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    subject = decode_jwt(authorization.split(" ", 1)[1].strip())
    if subject != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return subject


async def get_current_admin_ws(websocket: WebSocket) -> str:
    authorization = websocket.headers.get("authorization", "")
    token = authorization.split(" ", 1)[1].strip() if authorization.lower().startswith("bearer ") else str(websocket.query_params.get("token") or "")
    if not token:
        await websocket.close(code=4401)
        raise HTTPException(status_code=401, detail="Missing websocket token")
    try:
        subject = decode_jwt(token)
    except Exception as exc:
        await websocket.close(code=4401)
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    if subject != "admin" and not subject.startswith("user:"):
        await websocket.close(code=4403)
        raise HTTPException(status_code=403, detail="Admin access required")
    return subject


def get_agent_from_token(
    db: Session = Depends(get_db),
    x_agent_token: str = Header(default="", alias="X-Agent-Token"),
    x_pcmanager_key: str = Header(default="", alias="X-PCManager-Key"),
    x_server_access_key: str = Header(default="", alias="X-Server-Access-Key"),
) -> Agent:
    token = x_agent_token or x_pcmanager_key or x_server_access_key
    agent = db.query(Agent).filter(Agent.agent_token == token).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agent token invalid")
    return agent


def find_user_by_activation_key(key_str: str) -> int | None:
    from .database import db_session
    from .models import ActivationKey
    with db_session() as db:
        key_entry = db.query(ActivationKey).filter(ActivationKey.key == key_str.strip()).first()
        if key_entry:
            return key_entry.user_id
    return None

def get_current_user(authorization: str = Header(default="")) -> CurrentUser:
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    subject = decode_jwt(authorization.split(" ", 1)[1].strip())
    if subject == "admin":
        return CurrentUser(user_id=None, is_admin=True)
    elif subject.startswith("user:"):
        try:
            user_id = int(subject.split(":", 1)[1])
            return CurrentUser(user_id=user_id, is_admin=False)
        except ValueError:
            pass
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
