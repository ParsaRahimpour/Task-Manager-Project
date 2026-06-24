from database_api import (
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

# برای تست باید user با id=1 وجود داشته باشد

# -----------------------------
# CREATE TASK (SUCCESS)
# -----------------------------
print("\nCREATE TASK (SUCCESS)")

result = create_task(
    "Learn SQLAlchemy",
    "Complete tutorial",
    1
)

print(result)

task_id = None
user_id = 1

if result["code"] == 200:
    task_id = result["data"]["id"]

# -----------------------------
# CREATE TASK (ERROR 400)
# -----------------------------
print("\nCREATE TASK (INVALID USER_ID)")

result = create_task(
    "Broken Task",
    "Should fail",
    999999
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

result = get_task_by_id(999999)

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
        1
    )

    print(result)

# -----------------------------
# UPDATE TASK (ERROR 404)
# -----------------------------
print("\nUPDATE TASK (NOT FOUND)")

result = update_task(
    999999,
    "Nothing",
    "Nothing",
    False,
    1
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
        999999
    )

    print(result)

# -----------------------------
# GET ALL TASKS (SUCCESS)
# -----------------------------
print("\nGET ALL TASKS")

result = get_all_tasks()

print(result)

# -----------------------------
# DELETE TASK (SUCCESS)
# -----------------------------
print("\nDELETE TASK (SUCCESS)")

if task_id:
    result = delete_task(task_id)
    print(result)

# -----------------------------
# DELETE TASK (ERROR 404)
# -----------------------------
print("\nDELETE TASK (NOT FOUND)")

result = delete_task(task_id)

print(result)

# -----------------------------
# DELETE TASK (ERROR 404)
# -----------------------------
print("\nDELETE TASK (NOT FOUND)")

result = delete_task(9999)

print(result)

# -----------------------------
# GET ALL TASKS(user_id)
# -----------------------------
print("\nGET ALL TASKS BY user_id")

result = get_tasks_by_user_id(user_id)

print(result)

# -----------------------------
# SEARCH TASKS BY TITLE
# -----------------------------
print("\nSEARCH TASKS BY TITLE")

result = search_tasks_by_title(
    1,
    "docker"
)
print(result)

# -----------------------------
# GET COMPLETED TASKS BY USER
# -----------------------------
print("\nGET COMPLETED TASKS BY USER")

result = get_completed_tasks_by_user(user_id)

print(result)