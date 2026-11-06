from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import os
import io
import base64
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/web_todo.db')
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TaskDB(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    status = Column(String, default='Новая')

class LogDB(Base):
    __tablename__ = 'activity_log'
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String)
    timestamp = Column(String, default=datetime.now().strftime('%Y-%m-%d'))

Base.metadata.create_all(bind=engine)
app = FastAPI(title='ToDo Web App')
templates = Jinja2Templates(directory='web/templates')

def log_action(db, action):
    log = LogDB(action=action, timestamp=datetime.now().strftime('%Y-%m-%d'))
    db.add(log)
    db.commit()

@app.get('/', response_class=HTMLResponse)
async def read_tasks(request: Request):
    db = SessionLocal()
    tasks = db.query(TaskDB).all()
    logs = db.query(LogDB).all()
    
    stats = {}
    for log in logs:
        stats[log.timestamp] = stats.get(log.timestamp, 0) + 1
        
    img_base64 = ''
    if stats:
        fig, ax = plt.subplots(figsize=(4, 2.5), facecolor='#2b2b2b')
        ax.set_facecolor('#2b2b2b')
        days = list(stats.keys())
        counts = list(stats.values())
        
        bars = ax.bar(days, counts, color='#17a2b8', width=0.4)
        ax.set_title('Активность по дням', color='white')
        ax.tick_params(axis='x', colors='white', rotation=0)
        ax.tick_params(axis='y', colors='white')
        
        max_count = max(counts)
        ax.set_ylim(0, max_count + 2)
        ax.bar_label(bars, color='white', padding=3)
        
        for spine in ax.spines.values():
            spine.set_color('white')
            
        plt.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format='png', facecolor='#2b2b2b')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)

    db.close()
    return templates.TemplateResponse(request=request, name='index.html', context={'tasks': tasks, 'graph': img_base64})

@app.post('/add')
async def add_task(title: str = Form(...), description: str = Form('')):
    db = SessionLocal()
    new_task = TaskDB(title=title, description=description)
    db.add(new_task)
    log_action(db, 'Добавлена задача')
    db.commit()
    db.close()
    return RedirectResponse(url='/', status_code=303)

@app.get('/delete/{task_id}')
async def delete_task(task_id: int):
    db = SessionLocal()
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if task:
        db.delete(task)
        log_action(db, 'Удалена задача')
        db.commit()
    db.close()
    return RedirectResponse(url='/', status_code=303)

@app.post('/update_status/{task_id}')
async def update_status(task_id: int, status: str = Form(...)):
    db = SessionLocal()
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if task:
        task.status = status
        log_action(db, f'Статус изменен на {status}')
        db.commit()
    db.close()
    return RedirectResponse(url='/', status_code=303)
