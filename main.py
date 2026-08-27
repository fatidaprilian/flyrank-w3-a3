from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inisialisasi database dan seeding saat startup
    init_db()
    yield


app = FastAPI(
    title="Task API",
    lifespan=lifespan
)


@app.get("/")
def read_root():
    return {"message": "Task API is running"}
