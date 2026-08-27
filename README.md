# Task Management API (Assignment A3 - Containerize Your Stack)

A containerized Task Management RESTful API built with FastAPI, PostgreSQL 16, and Docker Compose. All database queries and operations are isolated within a dedicated repository layer (`database.py`) using parameterized SQL queries.

---

## 1. Quickstart (One-Command Run)

Start the entire stack (API + PostgreSQL database) with a single command:

```bash
cp .env.example .env && docker compose up -d --build
```

Once the containers are running:
- API Base URL: `http://localhost:3000`
- Interactive OpenAPI / Swagger Docs: `http://localhost:3000/docs`

To stop the entire stack:
```bash
docker compose down
```

---

## 2. Environment Variables

Database connection configuration is managed through environment variables:

| Variable | Docker Compose Default | Local Default | Description |
|---|---|---|---|
| `DATABASE_URL` | `postgres://postgres:dev@db:5432/tasks` | `postgres://postgres:dev@localhost:5432/tasks` | PostgreSQL connection URI |

The `.env` file contains sensitive credentials and is strictly ignored by Git via `.gitignore`. A `.env.example` template is provided for quick setup.

---

## 3. Endpoints Specification

| Method | Endpoint | Request Body | Status Codes | Description |
|---|---|---|---|---|
| `GET` | `/tasks` | None | `200 OK` | Retrieves all tasks |
| `GET` | `/tasks/{id}` | None | `200 OK`, `404 Not Found` | Retrieves a specific task by ID |
| `POST` | `/tasks` | `{"title": string, "done"?: boolean}` | `201 Created`, `400 Bad Request` | Creates a new task |
| `PUT` | `/tasks/{id}` | `{"title": string, "done": boolean}` | `200 OK`, `400 Bad Request`, `404 Not Found` | Updates an existing task |
| `DELETE` | `/tasks/{id}` | None | `204 No Content`, `404 Not Found` | Deletes a task by ID |

---

## 4. API Interaction Examples (curl -i)

### GET /tasks
```bash
curl -i http://localhost:3000/tasks
```

Response:
```http
HTTP/1.1 200 OK
date: Thu, 27 Aug 2026 13:08:04 GMT
server: uvicorn
content-length: 192
content-type: application/json

[
  {"id": 1, "title": "Buy groceries", "done": false},
  {"id": 2, "title": "Read a book", "done": true},
  {"id": 3, "title": "Write some code", "done": false},
  {"id": 4, "title": "Persistence Test Task", "done": false}
]
```

### POST /tasks (Success)
```bash
curl -i -X POST http://localhost:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Deploy to production", "done": false}'
```

Response:
```http
HTTP/1.1 201 Created
date: Thu, 27 Aug 2026 13:08:15 GMT
server: uvicorn
content-length: 53
content-type: application/json

{"id": 5, "title": "Deploy to production", "done": false}
```

### POST /tasks (Validation Error - Missing or Empty Title)
```bash
curl -i -X POST http://localhost:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": ""}'
```

Response:
```http
HTTP/1.1 400 Bad Request
date: Thu, 27 Aug 2026 13:08:20 GMT
server: uvicorn
content-length: 30
content-type: application/json

{"error": "Title is required"}
```

---

## 5. Direct Database Inspection

Inspect database relations and schemas inside the running PostgreSQL container via `psql`:

```bash
docker compose exec db psql -U postgres -d tasks -c "\dt"
```

Output:
```text
         List of relations
 Schema | Name  | Type  |  Owner   
--------+-------+-------+----------
 public | tasks | table | postgres
(1 row)
```

Query task records directly:
```bash
docker compose exec db psql -U postgres -d tasks -c "SELECT * FROM tasks;"
```

Output:
```text
 id |         title         | done 
----+-----------------------+------
  1 | Buy groceries         | f
  2 | Read a book           | t
  3 | Write some code       | f
  4 | Persistence Test Task | f
  5 | Deploy to production  | f
(5 rows)
```

---

## 6. Data Persistence via Docker Named Volumes

Docker containers are ephemeral by default, meaning all internal filesystem modifications are lost when a container is removed. To ensure database durability across container lifecycles, a named Docker volume (`taskdata`) is mounted to `/var/lib/postgresql/data`.

When executing `docker compose down` followed by `docker compose up -d`, the database state persists intact on the host storage without data loss.

---

## 7. AI vs Me (Stage 6 — The AI Rematch)

In this bonus stage, an isolated version of the containerized stack was generated in quarantine under `ai-version/` and evaluated against the primary hand-built implementation (Stages 0–5).

### Specification Prompt Used
```text
Build a containerized task management REST API in Python using FastAPI, psycopg 3, and PostgreSQL.
Requirements:
1. PostgreSQL running on port 5432 with database 'tasks', credentials configured via DATABASE_URL from .env file (never hardcoded).
2. A 'tasks' table with columns (id serial primary key, title text not null, done boolean not null default false).
3. On startup, initialize the table if not present, and seed exactly 3 sample tasks ONLY when the table is empty.
4. Five CRUD endpoints: GET /tasks, GET /tasks/{id}, POST /tasks, PUT /tasks/{id}, DELETE /tasks/{id} maintaining consistent status codes (200, 201, 204, 400, 404).
5. All queries must use parameterized SQL placeholders (%s) in a dedicated database module.
6. Containerization: Dockerfile for the API and compose.yaml orchestrating 'api' and 'db' services with a persistent named volume for /var/lib/postgresql/data.
```

### Concrete Differences Analysis

1. **Exact Error Response Formatting**:
   - *AI Version*: Used default FastAPI `HTTPException(detail={"error": ...})`, which nests the response inside a `{"detail": {"error": "..."}}` root key.
   - *Hand-built Version*: Used direct `JSONResponse` objects, ensuring the error schema strictly matches `{"error": "Task not found"}` and `{"error": "Title is required"}` without unwanted wrapper keys.

2. **Database Startup Race Condition Handling**:
   - *AI Version*: Relied solely on `depends_on: [db]` without container health checks or connection retry handling in Python. When PostgreSQL took several seconds to initialize on a clean volume, the API container crashed on startup due to connection refused errors.
   - *Hand-built Version*: Configured Docker health checks with `pg_isready` (`condition: service_healthy`) in `compose.yaml` and implemented an exponential/linear retry loop inside `database.py:init_db()`.

3. **Connection and Cursor Lifecycle Management**:
   - *AI Version*: Opened raw connections inside each endpoint function without centralized cursor context managers or automatic rollback handling.
   - *Hand-built Version*: Provided a structured `get_db_cursor()` context manager ensuring proper transaction scoping and connection closure.

### Prompt Engineering Evaluation
The initial prompt omitted explicit requirements regarding:
- Exact JSON error payload structure without default framework nesting.
- Explicit healthcheck conditions and startup retry strategies for multi-container orchestration.

Refining the prompt with these constraints yields a more resilient containerized architecture.
