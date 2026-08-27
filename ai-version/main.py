from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel, Field
from typing import Optional
import database


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)
    done: Optional[bool] = False


class TaskUpdate(BaseModel):
    title: str = Field(..., min_length=1)
    done: bool


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield


app = FastAPI(title="AI Task API", lifespan=lifespan)


@app.get("/tasks")
def list_tasks():
    return database.get_all_tasks()


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = database.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Task not found"}
        )
    return task


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    if not payload.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Title is required"}
        )
    return database.create_task(payload.title.strip(), payload.done)


@app.put("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskUpdate):
    if not payload.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Title is required"}
        )
    task = database.update_task(task_id, payload.title.strip(), payload.done)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Task not found"}
        )
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    deleted = database.delete_task(task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Task not found"}
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
