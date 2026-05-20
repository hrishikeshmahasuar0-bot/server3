from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# THIS IS IMPORTANT - ADD THIS ROUTE
@app.get("/")
def home():
    return {"status": "WORKING", "message": "Chat server is running"}

@app.get("/test")
def test():
    return {"message": "Test endpoint works"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("New client connected!")
    
    try:
        username = await websocket.receive_text()
        print(f"Username: {username}")
        
        while True:
            data = await websocket.receive_text()
            print(f"Message: {data}")
            
            if data == "__ping__":
                await websocket.send_text("__pong__")
            elif data == "__typing__":
                # Handle typing indicator
                pass
            else:
                # Echo for testing (remove this later)
                await websocket.send_text(f"Server received: {data}")
                
    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)
