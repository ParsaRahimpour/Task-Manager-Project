from app.database_api import (
    create_task,
    get_tasks,
    update_task,
    delete_task
)

print("\n========== TASKS TEST ==========")

user_id = 3
invalid_user_id = 99999
invalid_task_id = 99999

# -----------------------------
# CREATE TASK (SUCCESS)
# -----------------------------
print("\nCREATE TASK (SUCCESS)")

result = create_task(
    "Learn SQLAlchemy",
    "Complete tutorial",
    user_id
)

print(result)

task_id = None


if result["code"] == 200:
    task_id = result["message"]["task_id"]

# -----------------------------
# CREATE TASK (ERROR 400)
# -----------------------------
print("\nCREATE TASK (INVALID USER_ID)")

result = create_task(
    "Broken Task",
    "Should fail",
    invalid_user_id
)

print(result)

# -----------------------------
# UPDATE TASK (SUCCESS)
# -----------------------------
print("\nUPDATE TASK (SUCCESS)")

if task_id:
    result = update_task(
        task_id,
        "Learn FastAPI",
        "Build APIs",
        True,
        user_id
    )

    print(result)

# -----------------------------
# UPDATE TASK (ERROR 404)
# -----------------------------
print("\nUPDATE TASK (NOT FOUND)")

result = update_task(
    invalid_task_id,
    "Nothing",
    "Nothing",
    False,
    user_id
)

print(result)

# -----------------------------
# UPDATE TASK (ERROR 400)
# -----------------------------
print("\nUPDATE TASK (INVALID USER_ID)")

if task_id:
    result = update_task(
        task_id,
        "Test",
        "Test",
        False,
        invalid_user_id
    )

    print(result)

# -----------------------------
# DELETE TASK (SUCCESS)
# -----------------------------
print("\nDELETE TASK (SUCCESS)")

if task_id:
    result = delete_task(task_id)
    print(result)

# -----------------------------
# DELETE TASK (Same user_id -> ERROR 404)
# -----------------------------
print("\nDELETE TASK (NOT FOUND)")

result = delete_task(task_id)

print(result)

# -----------------------------
# DELETE TASK (ERROR 404)
# -----------------------------
print("\nDELETE TASK (NOT FOUND)")

result = delete_task(invalid_task_id)

print(result)

