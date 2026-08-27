# Task Management API (Assignment A3 - Containerize Your Stack)

Task Management RESTful API backend yang dibangun menggunakan FastAPI, PostgreSQL 16, dan diorkestrasi menggunakan Docker Compose. Seluruh akses basis data diisolasi dalam repository layer `database.py` dengan kueri berparameter (*parameterized queries*).

---

## 1. Quickstart (One-Command Run)

Jalankan seluruh stack (API + PostgreSQL) dalam satu perintah:

```bash
cp .env.example .env && docker compose up -d --build
```

Setelah container berjalan:
- API dapat diakses di: `http://localhost:3000`
- Dokumentasi Swagger interaktif di: `http://localhost:3000/docs`

Untuk menghentikan stack:
```bash
docker compose down
```

---

## 2. Environment Variables

Konfigurasi koneksi basis data dikelola melalui variabel lingkungan:

| Variabel | Contoh Nilai (Docker Compose) | Contoh Nilai (Lokal) | Deskripsi |
|---|---|---|---|
| `DATABASE_URL` | `postgres://postgres:dev@db:5432/tasks` | `postgres://postgres:dev@localhost:5432/tasks` | URI koneksi PostgreSQL |

File `.env` diabaikan oleh Git via `.gitignore`. Template variabel tersedia pada file `.env.example`.

---

## 3. Endpoints Table

| Method | Endpoint | Request Body | Response Code | Deskripsi |
|---|---|---|---|---|
| `GET` | `/tasks` | None | `200 OK` | Mengambil seluruh daftar task |
| `GET` | `/tasks/{id}` | None | `200 OK` / `404 Not Found` | Mengambil task spesifik berdasarkan ID |
| `POST` | `/tasks` | `{"title": string, "done"?: boolean}` | `201 Created` / `400 Bad Request` | Membuat task baru |
| `PUT` | `/tasks/{id}` | `{"title": string, "done": boolean}` | `200 OK` / `400 Bad Request` / `404 Not Found` | Memperbarui task yang ada |
| `DELETE` | `/tasks/{id}` | None | `204 No Content` / `404 Not Found` | Menghapus task |

---

## 4. Contoh Interaksi API (curl -i)

### GET /tasks
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

### POST /tasks (Sukses)
```bash
curl -i -X POST http://localhost:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Deploy to production", "done": false}'
```

Output:
```http
HTTP/1.1 201 Created
date: Thu, 27 Aug 2026 13:08:15 GMT
server: uvicorn
content-length: 53
content-type: application/json

{"id": 5, "title": "Deploy to production", "done": false}
```

### POST /tasks (Validasi Error 400)
```bash
curl -i -X POST http://localhost:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": ""}'
```

Output:
```http
HTTP/1.1 400 Bad Request
date: Thu, 27 Aug 2026 13:08:20 GMT
server: uvicorn
content-length: 30
content-type: application/json

{"error": "Title is required"}
```

---

## 5. Pemeriksaan Database Langsung

Memeriksa tabel dan relasi di dalam container PostgreSQL via `psql`:

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

Melihat isi data tabel:
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

## 6. Penjelasan Persistensi Data (Docker Volume)

Container bersifat *ephemeral*, yang berarti seluruh file di dalam container akan terhapus ketika container dihancurkan. Untuk memastikan data basis data tidak hilang saat restart atau update container, digunakan Docker Named Volume `taskdata` yang dipetakan ke `/var/lib/postgresql/data`. 

Saat menjalankan `docker compose down` dan `docker compose up -d`, volume `taskdata` tetap tersimpan di host machine sehingga data tugas tetap utuh dan persisten.
