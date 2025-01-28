from sqlalchemy.orm import Session
from src.app import models, schemas
from passlib.context import CryptContext
import uuid
from datetime import datetime, timedelta
from src.app.utils import send_email

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = hash_password(user.password)
    db_user = models.User(username=user.username, email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Create Todo
def create_todo(db: Session, todo: schemas.TodoCreate, user_id: int):
    db_todo = models.Todo(
        title=todo.title, description=todo.description, done=todo.done, user_id=user_id
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

# Get Todos for a user
def get_todos(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Todo).filter(models.Todo.user_id == user_id).offset(skip).limit(limit).all()

# Get Todo by ID for a user
def get_todo_by_id(db: Session, todo_id: int, user_id: int):
    return db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.user_id == user_id).first()

# Update Todo
def update_todo(db: Session, todo_id: int, todo: schemas.TodoCreate, user_id: int):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.user_id == user_id).first()
    if db_todo:
        db_todo.title = todo.title
        db_todo.description = todo.description
        db_todo.done = todo.done
        db.commit()
        db.refresh(db_todo)
        return db_todo
    return None

# Delete Todo
def delete_todo(db: Session, todo_id: int, user_id: int):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.user_id == user_id).first()
    if db_todo:
        db.delete(db_todo)
        db.commit()
        return db_todo
    return None

# Forgot Password (Send reset link to user's email)
def forgot_password(db: Session, email: str):
    db_user = db.query(models.User).filter(models.User.email == email).first()
    if db_user:
        reset_token = str(uuid.uuid4())
        reset_token_expiry = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
        
        db_user.reset_token = reset_token
        db_user.reset_token_expiry = reset_token_expiry
        db.commit()
        
        send_email(db_user.email, reset_token)
        return True
    return False

def reset_password(db: Session, reset_token: str, new_password: str):
    db_user = db.query(models.User).filter(models.User.reset_token == reset_token).first()
    if db_user and db_user.reset_token_expiry > datetime.utcnow():
        hashed_password = hash_password(new_password)
        db_user.password_hash = hashed_password
        db_user.reset_token = None
        db_user.reset_token_expiry = None
        db.commit()
        return db_user
    return None
