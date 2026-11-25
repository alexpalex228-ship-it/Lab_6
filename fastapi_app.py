import sqlite3
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

DB_PATH = "lab6_items.db"

app = FastAPI(title="Лабораторная работа № 6 — FastAPI")


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


class ItemCreate(BaseModel):
    title: str
    description: str


@app.get("/api/info")
def get_json_info():
    return {
        "lab": 6,
        "variant": 2,
        "status": "ok",
        "topics": ["Flask", "FastAPI", "SQLite", "WebSocket"],
    }


@app.post("/items")
def create_item(item: ItemCreate):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO items (title, description) VALUES (?, ?)",
        (item.title, item.description),
    )
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    return {"id": item_id, "title": item.title, "description": item.description}


@app.get("/items")
def list_items():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description FROM items")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": row[0], "title": row[1], "description": row[2]}
        for row in rows
    ]


CHAT_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>WebSocket Чат — FastAPI</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; max-width: 600px; }
        #messages { border: 1px solid #ccc; height: 240px; overflow-y: auto; padding: 10px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <h2>WebSocket Чат</h2>
    <div id="messages"></div>
    <input type="text" id="msgInput" placeholder="Введите сообщение..." autocomplete="off">
    <button onclick="sendMessage()">Отправить</button>

    <script>
        const ws = new WebSocket(`ws://${window.location.host}/ws/chat`);
        const messagesDiv = document.getElementById("messages");
        const input = document.getElementById("msgInput");

        ws.onmessage = function(event) {
            const p = document.createElement("p");
            p.textContent = event.data;
            messagesDiv.appendChild(p);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        };

        function sendMessage() {
            if (input.value.trim() !== "") {
                ws.send(input.value);
                input.value = "";
            }
        }

        input.addEventListener("keydown", function(e) {
            if (e.key === "Enter") sendMessage();
        });
    </script>
</body>
</html>
"""


@app.get("/chat", response_class=HTMLResponse)
def chat_page():
    return CHAT_HTML


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str) -> None:
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Участник: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)