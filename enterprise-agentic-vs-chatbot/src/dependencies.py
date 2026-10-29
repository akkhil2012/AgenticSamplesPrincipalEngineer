from fastapi import Request, Header
from src.governance.identity import authenticate


def identity(request: Request, authorization: str | None = Header(default=None)):
    return authenticate(authorization, request.app.state.settings.demo_auth)
