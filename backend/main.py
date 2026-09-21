from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pyodbc
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://130.131.226.76"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_connection():
    connection_string = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={os.environ['DB_SERVER']},1433;"
        f"DATABASE={os.environ['DB_NAME']};"
        f"UID={os.environ['DB_USER']};"
        f"PWD={os.environ['DB_PASSWORD']};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )
    return pyodbc.connect(connection_string)


@app.get("/tasks")
def get_tasks():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, description
        FROM dbo.Tasks
        ORDER BY id
    """)

    tasks = [
        {
            "id": row.id,
            "title": row.title,
            "description": row.description
        }
        for row in cursor.fetchall()
    ]

    cursor.close()
    conn.close()

    return tasks


@app.post("/tasks")
def create_task(task: dict):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO dbo.Tasks (title, description)
        OUTPUT INSERTED.id
        VALUES (?, ?)
        """,
        task.get("title"),
        task.get("description")
    )

    task_id = cursor.fetchone()[0]

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "id": task_id,
        "title": task.get("title"),
        "description": task.get("description")
    }


@app.get("/")
def root():
    return {"message": "Todo Backend is running"}
