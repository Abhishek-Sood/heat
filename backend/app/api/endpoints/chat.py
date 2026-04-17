from fastapi import APIRouter

router = APIRouter()

@router.websocket("/chat")
async def chat_websocket(websocket):
    await websocket.accept()
    await websocket.send_text("Chat started. (Demo)")
    await websocket.close()
