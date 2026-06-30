import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))


from app.database_api import (
    create_user,
    update_user,
    delete_user
)

print("\n========== USERS TEST ==========")

valid_password='123'
invalid_password='aaa'

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
# UPDATE admin (ERROR 500)
# -----------------------------
print("\nUPDATE admin (ERROR 500)")


result = update_user(
    1,
    "Updated admin",
    "updated_admin@admin.com",
    "updatedAdminPass"
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