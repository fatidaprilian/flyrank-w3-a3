# Task Management API (Assignment A3 - Containerize Your Stack)

Aplikasi Task Management CRUD API yang dikontainerisasi menggunakan FastAPI, PostgreSQL, dan Docker.

## Menjalankan Database (Stage 0)

Untuk menjalankan PostgreSQL secara mandiri menggunakan Docker dengan persistent volume:

```bash
docker run --name taskdb -e POSTGRES_PASSWORD=dev -e POSTGRES_DB=tasks -p 5432:5432 -v taskdata:/var/lib/postgresql/data -d postgres
```

Untuk memeriksa database via psql di dalam container:

```bash
docker exec -it taskdb psql -U postgres -d tasks
```
