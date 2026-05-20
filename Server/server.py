from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
from typing import List, Dict

app = FastAPI()

# Add CORS middleware for browser client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store connected clients and their usernames
clients: List[WebSocket] = []
usernames: Dict[WebSocket, str] = {}

@app.get("/")
async def home():
    return {
        "status": "WORKING",
        "message": "WebSocket chat server is running",
        "active_connections": len(clients)
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "active_connections": len(clients),
        "connections": list(usernames.values())
    }

async def broadcast(message: str, exclude: WebSocket = None):
    """Send message to all connected clients except the excluded one"""
    disconnected = []
    
    for client in clients:
        if client == exclude:
            continue
            
        try:
            await client.send_text(message)
        except:
            disconnected.append(client)

    # Remove disconnected clients
    for client in disconnected:
        if client in clients:
            clients.remove(client)
            if client in usernames:
                del usernames[client]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        # Receive username first
        username = await websocket.receive_text()
        
        # Store client
        clients.append(websocket)
        usernames[websocket] = username
        
        # Broadcast join message
        await broadcast(f"🟢 {username} joined the chat")
        
        # Send welcome message to the new user
        await websocket.send_text(f"✅ Welcome to the chat, {username}!")
        await websocket.send_text(f"📊 {len(clients)} active users online")
        
        # Main message loop
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            # Handle different message types
            if data == "__ping__":
                # Respond to ping to keep connection alive
                await websocket.send_text("__pong__")
                continue
                
            elif data == "__typing__":
                # Broadcast typing indicator to everyone except sender
                await broadcast(f"✏️ {username} is typing...", exclude=websocket)
                
            elif data.startswith("/"):
                # Handle commands
                if data == "/users":
                    active_users = ", ".join(usernames.values())
                    await websocket.send_text(f"📋 Active users ({len(clients)}): {active_users}")
                elif data == "/help":
                    help_text = """📖 Available Commands:
                    /users - Show active users
                    /help - Show this help message
                    /quit - Leave the chat"""
                    await websocket.send_text(help_text)
                else:
                    await websocket.send_text(f"❌ Unknown command: {data}. Type /help for available commands")
                    
            else:
                # Regular message - broadcast to everyone
                await broadcast(f"{username}: {data}")
                
    except WebSocketDisconnect:
        # Handle disconnection
        if websocket in clients:
            clients.remove(websocket)
        username = usernames.pop(websocket, "Unknown")
        await broadcast(f"🔴 {username} left the chat")
        
    except Exception as e:
        print(f"Error in websocket: {e}")
        if websocket in clients:
            clients.remove(websocket)
        usernames.pop(websocket, None)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=False  # Set to True for development only
    )
