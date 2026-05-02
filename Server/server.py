from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import os

app = FastAPI()

@app.get("/")
def home():
    return {"status": "WORKING"}

clients = []
usernames = {}

async def broadcast(message: str):
    disconnected = []
    for client in clients:
        try:
            await client.send_text(message)
        except:
            disconnected.append(client)

    # remove disconnected clients
    for client in disconnected:
        if client in clients:
            clients.remove(client)
            usernames.pop(client, None)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        # receive username
        username = await websocket.receive_text()

        clients.append(websocket)
        usernames[websocket] = username

        # join message
        await broadcast(f"🟢 {username} joined")

        while True:
            data = await websocket.receive_text()

            if data == "__typing__":
                for client in clients:
                    if client != websocket:
                        await client.send_text(f"✏️ {username} is typing...")
            else:
                await broadcast(f"{username}: {data}")

    except WebSocketDisconnect:
        if websocket in clients:
            clients.remove(websocket)

        username = usernames.pop(websocket, "Unknown")
        await broadcast(f"🔴 {username} left")

    except Exception as e:
        print("Error:", e)


# 👇 THIS PART IS IMPORTANT FOR RENDER
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
