import sqlite3
import os
from datetime import datetime
from app.models import Task

class Database:
    def __init__(self, db_path='data/todo.db'):
        if os.path.dirname(db_path):
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        with self.conn:
            self.conn.executescript('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT
                );
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT,
                    timestamp TEXT
                );
            ''')

    def add_task(self, task: Task):
        with self.conn:
            cursor = self.conn.execute(
                "INSERT INTO tasks (title, description, status) VALUES (?, ?, ?)",
                (task.title, task.description, task.status)
            )
            self.log_activity("Добавлена задача")
        return cursor.lastrowid

    def get_tasks(self):
        rows = self.conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
        return [Task(r["title"], r["description"], r["status"], r["id"]) for r in rows]

    def delete_task(self, task_id):
        with self.conn:
            self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            self.log_activity("Удалена задача")

    def update_status(self, task_id, new_status):
        with self.conn:
            self.conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
            self.log_activity(f"Изменен статус на {new_status}")

    def log_activity(self, action):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.conn:
            self.conn.execute("INSERT INTO activity_log (action, timestamp) VALUES (?, ?)", (action, now))

    def get_activity_stats(self):
        rows = self.conn.execute(
            "SELECT substr(timestamp, 1, 10) as day, COUNT(*) as count FROM activity_log GROUP BY day ORDER BY day"
        ).fetchall()
        return {r["day"]: r["count"] for r in rows}