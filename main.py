from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")
socks = []


@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    socks.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for s in socks:
                await s.send_text(f"Message from {websocket.scope['client']}: {data}")
    except WebSocketDisconnect:
        socks.remove(websocket)
        for s in socks:
            await s.send_text(f"Leaved: {websocket.scope['client']}")
