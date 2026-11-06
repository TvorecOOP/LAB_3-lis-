class TaskError(Exception):
    """Базовое исключение для нашего приложения"""
    pass

class EmptyTitleError(TaskError):
    """Исключение: пустое название задачи"""
    pass

class Task:
    def __init__(self, title, description="", status="Новая", task_id=None):
        if not title.strip():
            raise EmptyTitleError("Название задачи не может быть пустым!")
        self.id = task_id
        self.title = title.strip()
        self.description = description.strip()
        self.status = status

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status
        }

    def __str__(self):
        return f"[{self.status}] {self.title}"