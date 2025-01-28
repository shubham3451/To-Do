from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from src.app import models, crud, schemas, auth, utils
from src.database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import BackgroundTasks
from typing import List

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_by_email_or_username(db: Session, username_or_email: str):
    if '@' in username_or_email:
        return db.query(models.User).filter(models.User.email == username_or_email).first()
    else:
        return db.query(models.User).filter(models.User.username == username_or_email).first()

# Register user (sign up)
@app.post("/signup", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_email_user = db.query(models.User).filter(models.User.username == user.email).first()  # Here email is treated as username temporarily
    if db_email_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = crud.create_user(db=db, user=user)
    return db_user


# Sign in user and obtain JWT token
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# Change user password (must be logged in)
@app.post("/change-password")
def change_password(change_data: schemas.UserChangePassword, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not auth.verify_password(change_data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    current_user.password_hash = auth.hash_password(change_data.new_password)
    db.commit()
    return {"msg": "Password changed successfully"}

# Forgot password
@app.post("/forgot-password")
def forgot_password(email: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = get_user_by_email_or_username(db, email)
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    token = utils.generate_reset_token(user.email)
    reset_link = f"http://localhost:8000/reset-password/{token}"
    subject = "Password Reset Request"
    body = f"Click the link to reset your password: {reset_link}"
    
    background_tasks.add_task(utils.send_email, user.email, subject, body)
    return {"msg": "Password reset email sent"}

#Reset Password
@app.post("/reset-password/{token}")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    try:
        email = utils.verify_reset_token(token)
    except HTTPException:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.password_hash = auth.hash_password(new_password)
    db.commit()
    return {"msg": "Password reset successfully"}


# CRUD Todo operations
@app.post("/todos/", response_model=schemas.Todo)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.create_todo(db=db, todo=todo, user_id=current_user.id)

@app.get("/todos/", response_model=List[schemas.Todo])
def get_todos(db: Session = Depends(get_db), skip: int = 0, limit: int = 100, current_user: models.User = Depends(auth.get_current_user)):
    return crud.get_todos(db=db, skip=skip, limit=limit, user_id=current_user.id)

@app.get("/todos/{todo_id}", response_model=schemas.Todo)
def get_todo_by_id(todo_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.get_todo_by_id(db=db, todo_id=todo_id, user_id=current_user.id)

@app.put("/todos/{todo_id}", response_model=schemas.Todo)
def update_todo(todo_id: int, todo: schemas.TodoCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.update_todo(db=db, todo_id=todo_id, todo=todo, user_id=current_user.id)

@app.delete("/todos/{todo_id}", response_model=schemas.Todo)
def delete_todo(todo_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.delete_todo(db=db, todo_id=todo_id, user_id=current_user.id)
