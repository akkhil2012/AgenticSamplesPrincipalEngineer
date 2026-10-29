from fastapi import APIRouter, Request
from src.contracts.schemas import Query

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


@router.post("/query")
async def query(body: Query, request: Request):
    return await request.app.state.chatbot.query(body.message)
