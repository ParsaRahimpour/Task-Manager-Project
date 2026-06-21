from sqlalchemy import text

from db import SessionLocal


#----------users-------------


def create_user(name, email):
    db = SessionLocal()

    try:
        query = text("""
            INSERT INTO users (name, email)
            VALUES (:name, :email)
            RETURNING *
        """)

        result = db.execute(
            query,
            {
                "name": name,
                "email": email
            }
        )

        db.commit()

        return result.fetchone()

    except Exception as e:
        db.rollback()
        return e

    finally:
        db.close()


def get_all_users():
    db = SessionLocal()

    try:
        result = db.execute(
            text("SELECT * FROM users")
        )

        return result.fetchall()

    except Exception as e:
        return e

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

        return result.fetchone()

    except Exception as e:
        return e

    finally:
        db.close()


def update_user(user_id, name, email):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                UPDATE users
                SET name = :name,
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

        db.commit()

        return result.fetchone()

    except Exception as e:
        db.rollback()
        return e

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

        db.commit()

        return result.fetchone()

    except Exception as e:
        db.rollback()
        return e

    finally:
        db.close()   
        
        
#---------tasks-------------


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

        db.commit()

        return result.fetchone()

    except Exception as e:
        db.rollback()
        return e

    finally:
        db.close()


def get_all_tasks():
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                SELECT *
                FROM tasks
            """)
        )

        return result.fetchall()

    except Exception as e:
        return e

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

        return result.fetchone()

    except Exception as e:
        return e

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
                SET title = :title,
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

        db.commit()

        return result.fetchone()

    except Exception as e:
        db.rollback()
        return e

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

        db.commit()

        return result.fetchone()

    except Exception as e:
        db.rollback()
        return e

    finally:
        db.close()             