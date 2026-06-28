from database_api import (
    create_user,
    get_all_users,
    get_user_by_id,
    get_user_by_email,
    update_user,
    delete_user
)

print("\n========== USERS TEST ==========")

# -----------------------------
# CREATE USER (SUCCESS)
# -----------------------------
print("\nCREATE USER (SUCCESS)")

result = create_user(
    "Test User",
    "test_user@example.com",
    "mypass"
)

print(result)

user_id = None

if result["code"] == 200:
    user_id = result["message"]["user_id"]

# -----------------------------
# CREATE USER (ERROR 409)
# -----------------------------
print("\nCREATE USER (DUPLICATE EMAIL)")

result = create_user(
    "Another User",
    "test_user@example.com",
    "anotherpass"
)

print(result)

# -----------------------------
# GET USER BY ID (SUCCESS)
# -----------------------------
print("\nGET USER BY ID (SUCCESS)")

if user_id:
    result = get_user_by_id(user_id)
    print(result)

# -----------------------------
# GET USER BY ID (ERROR 404)
# -----------------------------
print("\nGET USER BY ID (NOT FOUND)")

result = get_user_by_id(999999)

print(result)

# -----------------------------
# GET USER BY EMAIL (SUCCESS)
# -----------------------------
print("\nGET USER BY EMAIL (SUCCESS)")

result = get_user_by_email(
    "test_user@example.com"
)

print(result)

# -----------------------------
# GET USER BY EMAIL (NOT FOUND)
# -----------------------------
print("\nGET USER BY EMAIL (NOT FOUND)")

result = get_user_by_email(
    "unknown@example.com"
)

print(result)

# -----------------------------
# UPDATE USER (SUCCESS)
# -----------------------------
print("\nUPDATE USER (SUCCESS)")

if user_id:
    result = update_user(
        user_id,
        "Updated User",
        "updated_user@example.com",
        "updatedpass"
    )

    print(result)

# -----------------------------
# UPDATE USER (ERROR 404)
# -----------------------------
print("\nUPDATE USER (NOT FOUND)")

result = update_user(
    999999,
    "Nobody",
    "nobody@example.com",
    "nopass"
)

print(result)

# -----------------------------
# GET ALL USERS (SUCCESS)
# -----------------------------
print("\nGET ALL USERS")

result = get_all_users()

print(result)

# -----------------------------
# DELETE USER (SUCCESS)
# -----------------------------
print("\nDELETE USER (SUCCESS)")

if user_id:
    result = delete_user(user_id)
    print(result)

# -----------------------------
# DELETE USER (ERROR 404)
# -----------------------------
print("\nDELETE USER (NOT FOUND)")

result = delete_user(user_id)

print(result)