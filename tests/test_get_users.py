import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database_api import get_users  


def print_result(title, result):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    print(result)


# ======================================================
# 1. SUCCESS CASES
# ======================================================

def test_get_all_users_success():
    result = get_users()
    print_result("GET ALL USERS (SUCCESS)", result)


def test_get_user_by_id_success():
    result = get_users(user_id=1)
    print_result("GET USER BY ID (SUCCESS)", result)


def test_get_user_by_email_success():
    result = get_users(email="admin@admin.com")
    print_result("GET USER BY EMAIL (SUCCESS)", result)
    
def test_get_user_by_password_success():
    result = get_users(password='admin_p@ss')
    print_result("GET USER BY PASSWORD (SUCCESS)", result)
    
def test_get_user_by_all_success():
    result = get_users(user_id=1,
                       name='admin',
                       email="admin@admin.com",
                       password='admin_p@ss'
                       )
    print_result("GET USER BY ALL (SUCCESS)", result)        


# ======================================================
# 2. FAILURE CASES
# ======================================================

def test_get_user_by_id_not_found():
    result = get_users(user_id=999999)
    print_result("GET USER BY ID (NOT FOUND)", result)


def test_get_user_by_email_not_found():
    result = get_users(email="fake@email.com")
    print_result("GET USER BY EMAIL (NOT FOUND)", result)


def test_get_users_no_match_multiple_filters():
    result = get_users(
        user_id=1,
        email="wrong@email.com"
    )
    print_result("GET USERS MULTI FILTER (NO MATCH)", result)


# ======================================================
# RUN ALL TESTS
# ======================================================

if __name__ == "__main__":
    test_get_all_users_success()
    test_get_user_by_id_success()
    test_get_user_by_email_success()
    test_get_user_by_password_success()
    test_get_user_by_all_success()

    test_get_user_by_id_not_found()
    test_get_user_by_email_not_found()
    test_get_users_no_match_multiple_filters()