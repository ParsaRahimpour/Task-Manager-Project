from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from typing import Optional
from .db import SessionLocal


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


def get_users(
    user_id: Optional[int] = None,
    name: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None
):
    db = SessionLocal()

    try:
        conditions = []
        params = {}

        # Build dynamic filters
        if user_id is not None:
            conditions.append("user_id = :user_id")
            params["user_id"] = user_id

        if name is not None:
            conditions.append("name = :name")
            params["name"] = name

        if email is not None:
            conditions.append("email = :email")
            params["email"] = email

        if password is not None:
            conditions.append("password = :password")
            params["password"] = password

        query = "SELECT * FROM users"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        result = db.execute(text(query), params)
        rows = result.fetchall()

        users = [row_to_dict(row, USER_COLUMNS) for row in rows]


        if not users:
            if not conditions:
                return error_response(
                    404,
                    "No users found."
                )
            else:
                return error_response(
                    404,
                    "No users match the provided filters."
                )

        return success_response(users)

    except Exception:
        return error_response(
            500,
            "Database error"
        )

    finally:
        db.close()
               

def update_user(
    user_id: int,
    name: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None
):
    db = SessionLocal()

    try:
        fields = {}
        params = {"user_id": user_id}

        if name is not None:
            fields["name"] = name

        if email is not None:
            fields["email"] = email

        if password is not None:
            fields["password"] = password

        if not fields:
            return error_response(
                400,
                "No data provided to update."
            )
            
        set_clause = ", ".join(
            f"{key} = :{key}" for key in fields.keys()
        )

        params.update(fields)

        query = f"""
            UPDATE users
            SET {set_clause}
            WHERE user_id = :user_id
            RETURNING *
        """

        result = db.execute(text(query), params)
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

    except IntegrityError as e:
        db.rollback()

        error_msg = str(e.orig).lower()

        if "unique_email" in error_msg:
            return error_response(
                409,
                "Email already exists. Please use a different email."
            )

        if "unique_password" in error_msg:
            return error_response(
                409,
                "Password already exists. Please choose a different password."
            )

        return error_response(
            409,
            "Duplicate value error."
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

    except IntegrityError as e:
        db.rollback()

        constraint = getattr(e.orig.diag, "constraint_name", None)

        if constraint == "uq_user_id_title":
            return error_response(
                409,
                "A task with this title already exists for this user."
            )

        if constraint == "fk_user_id":
            return error_response(
                400,
                "Invalid user id."
            )

        return error_response(
            400,
            "Database integrity error."
        )

    except Exception:
        db.rollback()

        return error_response(
            500,
            "Database error."
        )

    finally:
        db.close()


def get_tasks(
    task_id: Optional[int] = None,
    user_id: Optional[int] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    completed: Optional[bool] = None
):
    db = SessionLocal()

    try:
        conditions = []
        params = {}


        if task_id is not None:
            conditions.append("task_id = :task_id")
            params["task_id"] = task_id

        if user_id is not None:
            conditions.append("user_id = :user_id")
            params["user_id"] = user_id

        if title is not None:
            conditions.append("title ILIKE :title")
            params["title"] = f"%{title}%"

        if description is not None:
            conditions.append("description ILIKE :description")
            params["description"] = f"%{description}%"

        if completed is not None:
            conditions.append("completed = :completed")
            params["completed"] = completed


        query = "SELECT * FROM tasks"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        result = db.execute(text(query), params)
        rows = result.fetchall()

        tasks = [row_to_dict(row, TASK_COLUMNS) for row in rows]

        if not tasks:
            if not conditions:
                return error_response(
                    404,
                    "No tasks found."
                )
            else:
                return error_response(
                    404,
                    "No tasks match the provided filters."
                )

        return success_response(tasks)

    except Exception:
        return error_response(
            500,
            "Database error"
        )

    finally:
        db.close()



def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    completed: Optional[bool] = None,
    user_id: Optional[int] = None
):
    db = SessionLocal()

    try:
        fields = {}
        params = {"task_id": task_id}

        if title is not None:
            fields["title"] = title

        if description is not None:
            fields["description"] = description

        if completed is not None:
            fields["completed"] = completed

        if user_id is not None:
            fields["user_id"] = user_id

        if not fields:
            return error_response(
                400,
                "No data provided to update."
            )

        set_clause = ", ".join(
            f"{key} = :{key}" for key in fields.keys()
        )

        params.update(fields)

        query = f"""
            UPDATE tasks
            SET {set_clause}
            WHERE task_id = :task_id
            RETURNING *
        """

        result = db.execute(text(query), params)
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

    except IntegrityError as e:
        db.rollback()

        constraint = getattr(e.orig.diag, "constraint_name", None)

        if constraint == "uq_user_id_title":
            return error_response(
                409,
                "A task with this title already exists for this user."
            )

        if constraint == "fk_user_id":
            return error_response(
                400,
                "Invalid user_id. User does not exist."
            )

        return error_response(
            400,
            "Database integrity error "
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