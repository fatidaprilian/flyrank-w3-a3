import os
from contextlib import contextmanager
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgres://postgres:dev@localhost:5432/tasks"
)


def get_connection():
    # Mengembalikan koneksi baru dengan dict_row factory
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


@contextmanager
def get_db_cursor():
    with get_connection() as conn:
        with conn.cursor() as cur:
            yield cur


def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Buat tabel tasks jika belum ada
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done BOOLEAN NOT NULL DEFAULT FALSE
                );
            """)

            # Periksa apakah tabel kosong
            cur.execute("SELECT COUNT(*) AS count FROM tasks;")
            result = cur.fetchone()
            count = result["count"] if result else 0

            # Seed 3 task contoh jika tabel masih kosong
            if count == 0:
                seed_tasks = [
                    ("Buy groceries", False),
                    ("Read a book", True),
                    ("Write some code", False),
                ]
                cur.executemany(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s);",
                    seed_tasks
                )
        conn.commit()


def get_all_tasks() -> List[Dict[str, Any]]:
    with get_db_cursor() as cur:
        cur.execute("SELECT id, title, done FROM tasks ORDER BY id ASC;")
        return cur.fetchall()


def get_task_by_id(task_id: int) -> Optional[Dict[str, Any]]:
    with get_db_cursor() as cur:
        cur.execute("SELECT id, title, done FROM tasks WHERE id = %s;", (task_id,))
        return cur.fetchone()
