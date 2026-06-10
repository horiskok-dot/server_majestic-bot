from fastapi import APIRouter, HTTPException

from ..auth import create_access_token, verify_admin_token
from ..schemas import TokenRequest, TokenResponse


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: TokenRequest):
    # 1. Check global admin token
    if verify_admin_token(payload.admin_token):
        token, expires_in = create_access_token("admin")
        return TokenResponse(access_token=token, expires_in=expires_in)
        
    # 2. Check SaaS Activation Key
    from ..auth import find_user_by_activation_key
    user_id = find_user_by_activation_key(payload.admin_token)
    if user_id is not None:
        token, expires_in = create_access_token(f"user:{user_id}")
        return TokenResponse(access_token=token, expires_in=expires_in)
        
    raise HTTPException(status_code=403, detail="Activation key or Admin token invalid")
