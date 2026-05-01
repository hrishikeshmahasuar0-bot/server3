from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

app = FastAPI()

clients: List[WebSocket] = []
usernames = {}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # receive username first
    username = await websocket.receive_text()
    clients.append(websocket)
    usernames[websocket] = username

    # join message
    for client in clients:
        await client.send_text(f"🟢 {username} joined")

    try:
        while True:
            data = await websocket.receive_text()

            # typing indicator
            if data == "__typing__":
                for client in clients:
                    if client != websocket:
                        await client.send_text(f"✏️ {username} is typing...")
            else:
                for client in clients:
                    await client.send_text(f"{username}: {data}")

    except WebSocketDisconnect:
        clients.remove(websocket)
        for client in clients:
            await client.send_text(f"🔴 {username} left")