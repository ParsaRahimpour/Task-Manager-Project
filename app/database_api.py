from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from db import SessionLocal


# -----------------------------
# Helpers
# -----------------------------

USER_COLUMNS = ["id", "name", "email"]

TASK_COLUMNS = [
    "id",
    "title",
    "description",
    "completed",
    "user_id"
]


def row_to_dict(row, columns):
    if row is None:
        return None

    return dict(zip(columns, row))


def success_response(data):
    return {
        "code": 200,
        "data": data
    }


def error_response(code, message):
    return {
        "code": code,
        "message": message
    }


# -----------------------------
# USERS
# -----------------------------

def create_user(name, email):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                INSERT INTO users (name, email)
                VALUES (:name, :email)
                RETURNING *
            """),
            {
                "name": name,
                "email": email
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
            "Email already exists"
        )

    except Exception:
        db.rollback()

        return error_response(
            500,
            "Database error"
        )

    finally:
        db.close()


def get_all_users():
    db = SessionLocal()

    try:
        result = db.execute(
            text("SELECT * FROM users")
        )

        users = [
            row_to_dict(row, USER_COLUMNS)
            for row in result.fetchall()
        ]

        return success_response(users)

    except Exception:
        return error_response(
            500,
            "Database error"
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
                WHERE id = :user_id
            """),
            {
                "user_id": user_id
            }
        )

        row = result.fetchone()

        if row is None:
            return error_response(
                404,
                "User not found"
            )

        return success_response(
            row_to_dict(row, USER_COLUMNS)
        )

    except Exception:
        return error_response(
            500,
            "Database error"
        )

    finally:
        db.close()


def update_user(user_id, name, email):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                UPDATE users
                SET
                    name = :name,
                    email = :email
                WHERE id = :user_id
                RETURNING *
            """),
            {
                "user_id": user_id,
                "name": name,
                "email": email
            }
        )

        row = result.fetchone()

        if row is None:
            db.rollback()

            return error_response(
                404,
                "User not found"
            )

        db.commit()

        return success_response(
            row_to_dict(row, USER_COLUMNS)
        )

    except IntegrityError:
        db.rollback()

        return error_response(
            409,
            "Email already exists"
        )

    except Exception:
        db.rollback()

        return error_response(
            500,
            "Database error"
        )

    finally:
        db.close()


def delete_user(user_id):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                DELETE FROM users
                WHERE id = :user_id
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
                "User not found"
            )

        db.commit()

        return success_response(
            row_to_dict(row, USER_COLUMNS)
        )

    except Exception:
        db.rollback()

        return error_response(
            500,
            "Database error"
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
                WHERE id = :task_id
            """),
            {
                "task_id": task_id
            }
        )

        row = result.fetchone()

        if row is None:
            return error_response(
                404,
                "Task not found"
            )

        return success_response(
            row_to_dict(row, TASK_COLUMNS)
        )

    except Exception:
        return error_response(
            500,
            "Database error"
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
                WHERE id = :task_id
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
                "Task not found"
            )

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


def delete_task(task_id):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                DELETE FROM tasks
                WHERE id = :task_id
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
                "Task not found"
            )

        db.commit()

        return success_response(
            row_to_dict(row, TASK_COLUMNS)
        )

    except Exception:
        db.rollback()

        return error_response(
            500,
            "Database error"
        )

    finally:
        db.close()