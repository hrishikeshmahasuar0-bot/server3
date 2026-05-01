from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

clients = []
usernames = {}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # receive username
    username = await websocket.receive_text()
    clients.append(websocket)
    usernames[websocket] = username

    # notify join
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
        usernames.pop(websocket, None)

        for client in clients:
            await client.send_text(f"🔴 {username} left")
