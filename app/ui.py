import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QTableWidget, QTableWidgetItem, 
                               QPushButton, QLineEdit, QLabel, QMessageBox, 
                               QComboBox, QMenuBar)
from PySide6.QtCore import Qt
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from app.database import Database
from app.models import Task, EmptyTitleError

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("ToDo Менеджер - Вариант 15")
        self.resize(900, 600)

        # Главный виджет и макет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Верхняя часть: Ввод данных ---
        input_layout = QHBoxLayout()
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Название задачи...")
        
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Описание (необязательно)...")

        self.add_btn = QPushButton("Добавить задачу")
        self.add_btn.clicked.connect(self.add_task)

        input_layout.addWidget(QLabel("Задача:"))
        input_layout.addWidget(self.title_input)
        input_layout.addWidget(QLabel("Описание:"))
        input_layout.addWidget(self.desc_input)
        input_layout.addWidget(self.add_btn)
        
        main_layout.addLayout(input_layout)

        # --- Средняя часть: Таблица ---
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Задача", "Описание", "Статус"])
        self.table.horizontalHeader().setSectionResizeMode(1, self.table.horizontalHeader().ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, self.table.horizontalHeader().ResizeMode.Stretch)
        main_layout.addWidget(self.table)

        # --- Нижняя часть: Кнопки управления и график ---
        bottom_layout = QHBoxLayout()

        # Кнопки
        btn_layout = QVBoxLayout()
        self.delete_btn = QPushButton("Удалить выбранную")
        self.delete_btn.clicked.connect(self.delete_task)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Новая", "В процессе", "Выполнена"])
        self.update_status_btn = QPushButton("Обновить статус")
        self.update_status_btn.clicked.connect(self.update_status)

        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(QLabel("Изменить статус на:"))
        btn_layout.addWidget(self.status_combo)
        btn_layout.addWidget(self.update_status_btn)
        btn_layout.addStretch()

        bottom_layout.addLayout(btn_layout)

        # График активности (matplotlib)
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        bottom_layout.addWidget(self.canvas)

        main_layout.addLayout(bottom_layout)

        # --- Меню ---
        self.create_menu()

        # Загрузка данных
        self.load_data()

    def create_menu(self):
        menubar = self.menuBar()
        
        # Меню Файл
        file_menu = menubar.addMenu("Файл")
        exit_action = file_menu.addAction("Выход")
        exit_action.triggered.connect(self.close)

        # Меню Справка
        help_menu = menubar.addMenu("Справка")
        about_action = help_menu.addAction("О программе")
        about_action.triggered.connect(self.show_about)

    def show_about(self):
        QMessageBox.information(self, "О программе", "ToDo Менеджер (Вариант 15)\nРазработано в рамках ЛР №3\nСтудент: Павлов Д.И.")

    def load_data(self):
        # Загрузка таблицы
        tasks = self.db.get_tasks()
        self.table.setRowCount(0)
        for row_idx, task in enumerate(tasks):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(task.id)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(task.title))
            self.table.setItem(row_idx, 2, QTableWidgetItem(task.description))
            self.table.setItem(row_idx, 3, QTableWidgetItem(task.status))

        # Отрисовка графика
        self.plot_activity()

    def plot_activity(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        stats = self.db.get_activity_stats()
        if stats:
            days = list(stats.keys())
            counts = list(stats.values())
            ax.bar(days, counts, color='skyblue')
            ax.set_title("Активность по дням")
            ax.set_ylabel("Кол-во действий")
            # Поворот подписей дат для красоты
            for label in ax.get_xticklabels():
                label.set_rotation(45)
        else:
            ax.text(0.5, 0.5, 'Нет данных для графика', ha='center', va='center')

        self.figure.tight_layout()
        self.canvas.draw()

    def add_task(self):
        title = self.title_input.text()
        desc = self.desc_input.text()
        
        try:
            # Используем наше собственное исключение
            task = Task(title, desc)
            self.db.add_task(task)
            
            # Очищаем поля и обновляем данные
            self.title_input.clear()
            self.desc_input.clear()
            self.load_data()
        except EmptyTitleError as e:
            # Отлавливаем исключение и показываем ошибку
            QMessageBox.warning(self, "Ошибка ввода", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неизвестная ошибка: {e}")

    def delete_task(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите задачу для удаления!")
            return

        task_id = int(self.table.item(selected_row, 0).text())
        reply = QMessageBox.question(self, 'Подтверждение', 'Вы уверены, что хотите удалить задачу?', 
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.db.delete_task(task_id)
            self.load_data()

    def update_status(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите задачу для изменения статуса!")
            return

        task_id = int(self.table.item(selected_row, 0).text())
        new_status = self.status_combo.currentText()
        
        self.db.update_status(task_id, new_status)
        self.load_data()


def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())