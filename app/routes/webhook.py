from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from app.logic.webhook_logic import verify_webhook, process_incoming_message

router = APIRouter()


@router.get("/webhook")
def verify(request: Request):
   return(verify_webhook(request))

@router.post("/webhook")
async def webhook(request:Request):
    body = await request.json()
    return await process_incoming_message(body)


