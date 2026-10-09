from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse
import json
from datetime import datetime

app = FastAPI()
connected_clients = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        connected_clients.remove(websocket)

@app.post("/webhook")
async def receive_alert(payload: dict):
    """
    Expects JSON payload from MT5:
    {
        "strategy": "SMT_DIVERGENCE" | "DAILY_WEEKLY_SWEEP" | "LONDON_NY_SWEEP",
        "asset": "NAS100" or "US500" or "EURUSD",
        "action": "BUY" | "SELL",
        "price": 18500.25,
        "details": "Swept London High during NY session with rejection"
    }
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload["timestamp"] = timestamp
    
    print(f"[{timestamp}] Strategy Triggered: {payload}")
    
    # Broadcast to all connected tablet dashboards
    for client in connected_clients:
        await client.send_json(payload)
        
    return {"status": "success", "received": payload}

@app.get("/")
async def home():
    return {"status": "Multi-Strategy Trading Webhook Server is Online"}
