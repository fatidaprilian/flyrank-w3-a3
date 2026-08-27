from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
import database


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield


app = FastAPI(
    title="Task API",
    lifespan=lifespan
)


@app.get("/tasks")
def list_tasks():
    return database.get_all_tasks()


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = database.get_task_by_id(task_id)
    if task is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Task not found"}
        )
    return task


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_new_task(request: Request):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Title is required"}
        )

    if not isinstance(data, dict):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Title is required"}
        )

    title = data.get("title")
    if title is None or not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Title is required"}
        )

    done = bool(data.get("done", False))
    task = database.create_task(title.strip(), done)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=task
    )


@app.put("/tasks/{task_id}")
async def update_existing_task(task_id: int, request: Request):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Title is required"}
        )

    if not isinstance(data, dict):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Title is required"}
        )

    title = data.get("title")
    if title is None or not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Title is required"}
        )

    done = bool(data.get("done", False))
    updated_task = database.update_task(task_id, title.strip(), done)
    if updated_task is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Task not found"}
        )

    return updated_task


@app.delete("/tasks/{task_id}")
def delete_existing_task(task_id: int):
    deleted = database.delete_task(task_id)
    if not deleted:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Task not found"}
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
