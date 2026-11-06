import pytest
import os
from app.models import Task, EmptyTitleError, TaskError
from app.database import Database

@pytest.fixture
def db():
    # Создаем тестовую БД в памяти (чтобы не засорять основную)
    database = Database(":memory:")
    yield database
    database.conn.close()

def test_task_creation():
    task = Task("Купить хлеб", "В магазине")
    assert task.title == "Купить хлеб"
    assert task.status == "Новая"

def test_empty_title_raises_error():
    # Проверяем, что наше кастомное исключение срабатывает
    with pytest.raises(EmptyTitleError):
        Task("")

def test_db_add_and_get_task(db):
    task = Task("Тестовая задача")
    db.add_task(task)
    
    tasks = db.get_tasks()
    assert len(tasks) == 1
    assert tasks[0].title == "Тестовая задача"

def test_db_delete_task(db):
    task = Task("Удалить меня")
    task_id = db.add_task(task)
    
    db.delete_task(task_id)
    assert len(db.get_tasks()) == 0

def test_db_update_status(db):
    task = Task("Обновить меня")
    task_id = db.add_task(task)
    
    db.update_status(task_id, "Выполнена")
    tasks = db.get_tasks()
    assert tasks[0].status == "Выполнена"

def test_activity_logging(db):
    # При добавлении задачи должна записаться активность
    task = Task("Задача для графика")
    db.add_task(task)
    
    stats = db.get_activity_stats()
    assert len(stats) == 1 # Один день с активностью
    assert list(stats.values())[0] == 1 # Одно действие