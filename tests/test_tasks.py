from app.database_api import (
    create_task,
    get_all_tasks,
    get_task_by_id,
    update_task,
    delete_task,
    get_tasks_by_user_id,
    search_tasks_by_title,
    get_completed_tasks_by_user
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
# GET TASK BY ID (SUCCESS)
# -----------------------------
print("\nGET TASK BY ID (SUCCESS)")

if task_id:
    result = get_task_by_id(task_id)
    print(result)

# -----------------------------
# GET TASK BY ID (ERROR 404)
# -----------------------------
print("\nGET TASK BY ID (NOT FOUND)")

result = get_task_by_id(invalid_task_id)

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
# GET ALL TASKS (SUCCESS)
# -----------------------------
print("\nGET ALL TASKS (SUCCESS)")

result = get_all_tasks()

print(result)

# -----------------------------
# GET ALL TASKS BY user_id (SUCCESS)
# -----------------------------
print("\nGET ALL TASKS BY user_id (SUCCESS)")

result = get_tasks_by_user_id(user_id)

print(result)

# -----------------------------
# GET ALL TASKS BY user_id (ERROR)
# -----------------------------
print("\nGET ALL TASKS BY user_id (ERROR)")

result = get_tasks_by_user_id(invalid_user_id)

print(result)

# -----------------------------
# SEARCH TASKS BY TITLE (SUCCESS)
# -----------------------------
print("\nSEARCH TASKS BY TITLE (SUCCESS)")

result = search_tasks_by_title(
    user_id,
    "Learn FastAPI"
)
print(result)

# -----------------------------
# SEARCH TASKS BY TITLE (ERROR)
# -----------------------------
print("\nSEARCH TASKS BY TITLE (ERROR)")

result = search_tasks_by_title(
    user_id,
    "none"
)
print(result)

# -----------------------------
# GET COMPLETED TASKS BY user_id (SUCCESS)
# -----------------------------
print("\nGET COMPLETED TASKS BY USER (SUCCESS)")

result = get_completed_tasks_by_user(user_id)

print(result)

# -----------------------------
# GET COMPLETED TASKS BY user_id (ERROR)
# -----------------------------
print("\nGET COMPLETED TASKS BY USER (ERROR)")

result = get_completed_tasks_by_user(invalid_user_id)

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

