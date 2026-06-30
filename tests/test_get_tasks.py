import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database_api import get_tasks


def print_result(title, result):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    print(result)


# ======================================================
# 1. SUCCESS CASES
# ======================================================

def test_get_all_tasks_success():
    result = get_tasks()
    print_result("GET ALL TASKS (SUCCESS)", result)


def test_get_task_by_id_success():
    result = get_tasks(task_id=1)
    print_result("GET TASK BY ID (SUCCESS)", result)


def test_get_tasks_by_user_success():
    result = get_tasks(user_id=2)
    print_result("GET TASKS BY USER ID (SUCCESS)", result)


def test_get_completed_tasks_success():
    result = get_tasks(completed=False)
    print_result("GET COMPLETED TASKS (SUCCESS)", result)


def test_search_tasks_by_title_success():
    result = get_tasks(title="test")
    print_result("SEARCH TASKS BY TITLE (SUCCESS)", result)
    
    
def test_search_tasks_by_all_success():
    result = get_tasks(title="test", user_id=2)
    print_result("GET ALL (SUCCESS)", result)

# ======================================================
# 2. FAILURE CASES
# ======================================================

def test_get_task_by_id_not_found():
    result = get_tasks(task_id=999999)
    print_result("GET TASK BY ID (NOT FOUND)", result)


def test_get_tasks_by_user_not_found():
    result = get_tasks(user_id=999999)
    print_result("GET TASKS BY USER (NOT FOUND)", result)


def test_search_tasks_no_match():
    result = get_tasks(title="this_should_not_exist_12345")
    print_result("SEARCH TASKS (NO MATCH)", result)


def test_filter_combination_no_match():
    result = get_tasks(
        user_id=1,
        title="impossible_match_text_999"
    )
    print_result("FILTER COMBINATION (NO MATCH)", result)


# ======================================================
# RUN ALL TESTS
# ======================================================

if __name__ == "__main__":
    test_get_all_tasks_success()
    test_get_task_by_id_success()
    test_get_tasks_by_user_success()
    test_get_completed_tasks_success()
    test_search_tasks_by_title_success()
    test_search_tasks_by_all_success()

    test_get_task_by_id_not_found()
    test_get_tasks_by_user_not_found()
    test_search_tasks_no_match()
    test_filter_combination_no_match()