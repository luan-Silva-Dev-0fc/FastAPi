import os
import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

app = FastAPI()

# Permite que o Front-end acesse a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Mensagem(BaseModel):
    conteudo: str

def get_connection():
    return psycopg2.connect(DB_URL)

@app.on_event("startup")
def setup_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS mensagens (id SERIAL PRIMARY KEY, conteudo TEXT NOT NULL);")
    conn.commit()
    cur.close()
    conn.close()

@app.get("/mensagens")
def get_mensagens():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM mensagens ORDER BY id DESC;")
    dados = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": m[0], "conteudo": m[1]} for m in dados]

@app.post("/mensagens")
def post_mensagem(msg: Mensagem):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO mensagens (conteudo) VALUES (%s) RETURNING id;", (msg.conteudo,))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"id": new_id, "status": "criado"}

@app.delete("/mensagens/{id_msg}")
def delete_mensagem(id_msg: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM mensagens WHERE id = %s;", (id_msg,))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "deletado"}