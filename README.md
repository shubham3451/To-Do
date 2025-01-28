# ToDo Application

A simple ToDo application built with FastAPI, SQLAlchemy, and PostgreSQL. It allows users to manage their tasks, reset passwords, and authenticate using JWT tokens.

## Features

- **User Authentication**: Sign up, login, and change passwords.
- **Task Management**: Create, read, update, and delete tasks.
- **Password Reset**: Users can reset their password via email.
- **JWT Token Authentication**: Secure the endpoints with JWT tokens.
- **Background Task**: Sends email notifications in the background using SMTP.

## Technologies Used

- **Backend Framework**: FastAPI
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **Authentication**: JWT (JSON Web Token)
- **SMTP for Email**: Gmail SMTP server for sending password reset emails

## Setup and Installation

Follow these steps to set up the project locally:

### 1. Clone the repository

```bash
git clone https://github.com/your-username/todo-app.git
cd todo-app
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the root directory of the project and add the following environment variables:

```bash
DATABASE_URL=postgresql://<your_db_user>:<your_db_password>@<your_db_host>/<your_db_name>?sslmode=require
SECRET_KEY=<your_secret_key>
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=<your_smtp_user>
SMTP_PASSWORD=<your_smtp_password>
EMAIL_SENDER=<your_email_sender>
```

- Replace `<your_db_user>`, `<your_db_password>`, `<your_db_host>`, `<your_db_name>`, `<your_secret_key>`, and the SMTP credentials with your actual configuration.

### 5. Apply database migrations

Run the following command to initialize the database schema:

```bash
uvicorn main:app --reload
```

The tables will be created automatically on the first run, as `models.Base.metadata.create_all(bind=engine)` is called during the startup of the application.

### 6. Running the application

Start the FastAPI development server:

```bash
uvicorn main:app --reload
```

The application will be running at `http://localhost:8000`.

### 7. API Documentation

Once the server is running, you can access the automatic Swagger documentation at:

[http://localhost:8000/docs](http://localhost:8000/docs)

You can also use the alternative ReDoc documentation at:

[http://localhost:8000/redoc](http://localhost:8000/redoc)

## Endpoints

### Authentication Endpoints

- **POST /signup**: Sign up a new user (requires `username` and `password`).
- **POST /token**: Login with username and password to get a JWT token.
- **POST /change-password**: Change the user's password (requires old password and new password).
- **POST /forgot-password**: Request a password reset email (requires the user's email).
- **POST /reset-password/{token}**: Reset password using a valid token and new password.

### Task Management Endpoints

- **POST /todos/**: Create a new task (requires JWT token).
- **GET /todos/**: Get the list of tasks.
- **GET /todos/{todo_id}**: Get a task by its ID.
- **PUT /todos/{todo_id}**: Update a task (requires JWT token).
- **DELETE /todos/{todo_id}**: Delete a task (requires JWT token).

