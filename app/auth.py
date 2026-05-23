import bcrypt
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse

ALL_ROLES    = {"user", "support", "admin"}
ADMIN_ROLES  = {"support", "admin"}


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def current_user(request: Request) -> dict | None:
    return request.session.get("user")


def require_login(request: Request) -> RedirectResponse | None:
    if not current_user(request):
        return RedirectResponse(f"/login?next={request.url.path}", status_code=302)
    return None


def require_roles(request: Request, roles: set) -> RedirectResponse | None:
    user = current_user(request)
    if not user:
        return RedirectResponse(f"/login?next={request.url.path}", status_code=302)
    if user["role"] not in roles:
        return RedirectResponse("/support", status_code=302)
    return None


def api_require_roles(request: Request, roles: set):
    user = current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Nicht angemeldet")
    if user["role"] not in roles:
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
