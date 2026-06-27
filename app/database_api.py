from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from db import SessionLocal


# -----------------------------
# Helpers
# -----------------------------

USER_COLUMNS = [
    "user_id",
    "name",
    "email",
    "password"
]

TASK_COLUMNS = [
    "task_id",
    "title",
    "description",
    "completed",
    "user_id"
]


def row_to_dict(row, columns):
    if row is None:
        return None

    return dict(zip(columns, row))


def success_response(message):
    return {
        "code": 200,
        "message": message
    }


def error_response(code, message):
    return {
        "code": code,
        "message": message
    }


# -----------------------------
# USERS
# -----------------------------

def create_user(name, email, password):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                INSERT INTO users (name, email, password)
                VALUES (:name, :email, :password)
                RETURNING *
            """),
            {
                "name": name,
                "email": email,
                "password": password
            }
        )

        row = result.fetchone()

        db.commit()

        return success_response(
            row_to_dict(row, USER_COLUMNS)
        )

    except IntegrityError:
        db.rollback()

        return error_response(
            409,
            "Email already exists."
        )

    except Exception:
        db.rollback()

        return error_response(
            500,
            "Database error."
        )

    finally:
        db.close()


def get_all_users():
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                SELECT *
                FROM users
            """)
        )

        users = [
            row_to_dict(row, USER_COLUMNS)
            for row in result.fetchall()
        ]

        if not users:
            return error_response(
                404,
                "No users found."
            )

        return success_response(users)

    except Exception:
        return error_response(
            500,
            "Database error."
        )

    finally:
        db.close()


def get_user_by_id(user_id):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                SELECT *
                FROM users
                WHERE user_id = :user_id
            """),
            {
                "user_id": user_id
            }
        )

        row = result.fetchone()

        if row is None:
            return error_response(
                404,
                f"User with user_id {user_id} not found."
            )

        return success_response(
            row_to_dict(row, USER_COLUMNS)
        )

    except Exception:
        return error_response(
            500,
            "Database error."
        )

    finally:
        db.close()
        

def get_user_by_email(email):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                SELECT *
                FROM users
                WHERE email = :email
            """),
            {
                "email": email
            }
        )

        row = result.fetchone()

        if row is None:
            return error_response(
                404,
                f'User with email "{email}" not found.'
            )

        return success_response(
            row_to_dict(row, USER_COLUMNS)
        )

    except Exception:
        return error_response(
            500,
            "Database error."
        )

    finally:
        db.close()        


def update_user(user_id, name, email, password):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                UPDATE users
                SET
                    name = :name,
                    email = :email,
                    password = :password
                WHERE user_id = :user_id
                RETURNING *
            """),
            {
                "user_id": user_id,
                "name": name,
                "email": email,
                "password": password
            }
        )

        row = result.fetchone()

        if row is None:
            db.rollback()

            return error_response(
                404,
                f"User with user_id {user_id} not found."
            )

        db.commit()

        return success_response(
            row_to_dict(row, USER_COLUMNS)
        )

    except IntegrityError:
        db.rollback()

        return error_response(
            409,
            "Email already exists."
        )

    except Exception:
        db.rollback()

        return error_response(
            500,
            "Database error."
        )

    finally:
        db.close()


def delete_user(user_id):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                DELETE FROM users
                WHERE user_id = :user_id
                RETURNING *
            """),
            {
                "user_id": user_id
            }
        )

        row = result.fetchone()

        if row is None:
            db.rollback()

            return error_response(
                404,
                f"User with user_id {user_id} not found."
            )

        db.commit()

        return success_response(
            row_to_dict(row, USER_COLUMNS)
        )

    except Exception:
        db.rollback()

        return error_response(
            500,
            "Database error."
        )

    finally:
        db.close()

# -----------------------------
# TASKS
# -----------------------------

def create_task(title, description, user_id):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                INSERT INTO tasks (
                    title,
                    description,
                    completed,
                    user_id
                )
                VALUES (
                    :title,
                    :description,
                    false,
                    :user_id
                )
                RETURNING *
            """),
            {
                "title": title,
                "description": description,
                "user_id": user_id
            }
        )

        row = result.fetchone()

        db.commit()

        return success_response(
            row_to_dict(row, TASK_COLUMNS)
        )

    except IntegrityError:
        db.rollback()

        return error_response(
            400,
            "Invalid user id"
        )

    except Exception:
        db.rollback()

        return error_response(
            500,
            "Database error"
        )

    finally:
        db.close()


def get_all_tasks():
    db = SessionLocal()

    try:
        result = db.execute(
            text("SELECT * FROM tasks")
        )

        tasks = [
            row_to_dict(row, TASK_COLUMNS)
            for row in result.fetchall()
        ]

        return success_response(tasks)

    except Exception:
        return error_response(
            500,
            "Database error"
        )

    finally:
        db.close()


def get_task_by_id(task_id):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                SELECT *
                FROM tasks
                WHERE task_id = :task_id
            """),
            {
                "task_id": task_id
            }
        )

        row = result.fetchone()

        if row is None:
            return error_response(
                404,
                f"Task with task_id {task_id} not found."
            )

        return success_response(
            row_to_dict(row, TASK_COLUMNS)
        )

    except Exception:
        return error_response(
            500,
            "Database error."
        )

    finally:
        db.close()
        
        
def get_tasks_by_user_id(user_id):
    db = SessionLocal()

    try:
        user = db.execute(
            text("""
                SELECT user_id
                FROM users
                WHERE user_id = :user_id
            """),
            {
                "user_id": user_id
            }
        ).fetchone()

        if user is None:
            return error_response(
                404,
                f"User with user_id {user_id} not found."
            )

        result = db.execute(
            text("""
                SELECT *
                FROM tasks
                WHERE user_id = :user_id
            """),
            {
                "user_id": user_id
            }
        )

        tasks = [
            row_to_dict(row, TASK_COLUMNS)
            for row in result.fetchall()
        ]

        if not tasks:
            return error_response(
                404,
                f"User with user_id {user_id} has no tasks."
            )

        return success_response(tasks)

    except Exception:
        return error_response(
            500,
            "Database error."
        )

    finally:
        db.close()        


def update_task(
    task_id,
    title,
    description,
    completed,
    user_id
):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                UPDATE tasks
                SET
                    title = :title,
                    description = :description,
                    completed = :completed,
                    user_id = :user_id
                WHERE task_id = :task_id
                RETURNING *
            """),
            {
                "task_id": task_id,
                "title": title,
                "description": description,
                "completed": completed,
                "user_id": user_id
            }
        )

        row = result.fetchone()

        if row is None:
            db.rollback()

            return error_response(
                404,
                f"Task with task_id {task_id} not found."
            )

        db.commit()

        return success_response(
            row_to_dict(row, TASK_COLUMNS)
        )

    except IntegrityError:
        db.rollback()

        return error_response(
            400,
            "Invalid user_id."
        )

    except Exception:
        db.rollback()

        return error_response(
            500,
            "Database error."
        )

    finally:
        db.close()


def delete_task(task_id):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                DELETE FROM tasks
                WHERE task_id = :task_id
                RETURNING *
            """),
            {
                "task_id": task_id
            }
        )

        row = result.fetchone()

        if row is None:
            db.rollback()

            return error_response(
                404,
                f"Task with task_id {task_id} not found."
            )

        db.commit()

        return success_response(
            row_to_dict(row, TASK_COLUMNS)
        )

    except Exception:
        db.rollback()

        return error_response(
            500,
            "Database error."
        )

    finally:
        db.close()
        
        
def get_completed_tasks_by_user(user_id):
    db = SessionLocal()

    try:
        user = db.execute(
            text("""
                SELECT user_id
                FROM users
                WHERE user_id = :user_id
            """),
            {
                "user_id": user_id
            }
        ).fetchone()

        if user is None:
            return error_response(
                404,
                f"User with user_id {user_id} not found."
            )

        result = db.execute(
            text("""
                SELECT *
                FROM tasks
                WHERE user_id = :user_id
                  AND completed = true
            """),
            {
                "user_id": user_id
            }
        )

        tasks = [
            row_to_dict(row, TASK_COLUMNS)
            for row in result.fetchall()
        ]

        if not tasks:
            return error_response(
                404,
                f"User with user_id {user_id} has no completed tasks."
            )

        return success_response(tasks)

    except Exception:
        return error_response(
            500,
            "Database error."
        )

    finally:
        db.close()
        
        
def search_tasks_by_title(user_id, title):
    db = SessionLocal()

    try:
        user = db.execute(
            text("""
                SELECT user_id
                FROM users
                WHERE user_id = :user_id
            """),
            {
                "user_id": user_id
            }
        ).fetchone()

        if user is None:
            return error_response(
                404,
                f"User with user_id {user_id} not found."
            )

        result = db.execute(
            text("""
                SELECT *
                FROM tasks
                WHERE user_id = :user_id
                  AND title ILIKE :title
            """),
            {
                "user_id": user_id,
                "title": f"%{title}%"
            }
        )

        tasks = [
            row_to_dict(row, TASK_COLUMNS)
            for row in result.fetchall()
        ]

        if not tasks:
            return error_response(
                404,
                f'No tasks found for user_id {user_id} with title containing "{title}".'
            )

        return success_response(tasks)

    except Exception:
        return error_response(
            500,
            "Database error."
        )

    finally:
        db.close()