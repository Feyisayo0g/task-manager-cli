"""
Secure Multi-User Task Manager
------------------------------
A command-line task manager with user authentication (salted password
hashing), per-user data isolation, and defensive input handling.

Run directly:
    python task_manager.py

Data is persisted to users.json and tasks.json in the current directory.

Full design write-up and an executed demo are available in
task_manager_project.ipynb in this same repo.
"""

import json
import os
import hashlib
import secrets

USERS_FILE = "users.json"
TASKS_FILE = "tasks.json"


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def load_json(filepath):
    """Load a JSON file into a dict. Returns an empty dict if the file
    doesn't exist yet (first run) or is corrupted (defensive fallback)."""
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        print(f"Warning: could not read {filepath}, starting fresh.")
        return {}


def save_json(filepath, data):
    """Persist a dict to disk as JSON."""
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def hash_password(password: str, salt: str) -> str:
    """Combine password + salt and hash with SHA-256."""
    return hashlib.sha256((salt + password).encode()).hexdigest()


def register_user(username: str, password: str) -> bool:
    """
    Register a new user. Returns True on success, False if the
    username is already taken.
    """
    users = load_json(USERS_FILE)

    if username in users:
        print(f"Username '{username}' is already taken. Please choose another.")
        return False

    salt = secrets.token_hex(16)
    hashed = hash_password(password, salt)

    users[username] = {"salt": salt, "password_hash": hashed}
    save_json(USERS_FILE, users)

    # Initialize an empty task list for the new user
    tasks = load_json(TASKS_FILE)
    tasks[username] = []
    save_json(TASKS_FILE, tasks)

    print(f"User '{username}' registered successfully.")
    return True


def login_user(username: str, password: str) -> bool:
    """
    Validate credentials against stored (salted, hashed) password.
    Returns True if credentials are valid, False otherwise.
    """
    users = load_json(USERS_FILE)

    if username not in users:
        print("Username not found.")
        return False

    salt = users[username]["salt"]
    hashed_attempt = hash_password(password, salt)

    if hashed_attempt == users[username]["password_hash"]:
        print(f"Welcome back, {username}!")
        return True
    else:
        print("Incorrect password.")
        return False


# ---------------------------------------------------------------------------
# Task management (per-user isolation)
# ---------------------------------------------------------------------------

def _next_task_id(user_tasks: list) -> int:
    """Generate the next unique task ID for a user (max existing ID + 1)."""
    if not user_tasks:
        return 1
    return max(task["id"] for task in user_tasks) + 1


def add_task(username: str, description: str) -> dict:
    """Add a new Pending task for the given user and persist it."""
    tasks = load_json(TASKS_FILE)
    user_tasks = tasks.get(username, [])

    new_task = {
        "id": _next_task_id(user_tasks),
        "description": description,
        "status": "Pending",
    }
    user_tasks.append(new_task)
    tasks[username] = user_tasks
    save_json(TASKS_FILE, tasks)

    print(f"Task added: [{new_task['id']}] {description}")
    return new_task


def view_tasks(username: str) -> list:
    """Print and return all tasks belonging to the given user."""
    tasks = load_json(TASKS_FILE)
    user_tasks = tasks.get(username, [])

    if not user_tasks:
        print("No tasks found. Add one to get started!")
        return []

    print(f"\n--- Tasks for {username} ---")
    for task in user_tasks:
        print(f"[{task['id']}] {task['description']} - {task['status']}")
    print("-" * 28)
    return user_tasks


def complete_task(username: str, task_id: int) -> bool:
    """Mark a task as Completed by ID. Returns True if found and updated."""
    tasks = load_json(TASKS_FILE)
    user_tasks = tasks.get(username, [])

    for task in user_tasks:
        if task["id"] == task_id:
            task["status"] = "Completed"
            tasks[username] = user_tasks
            save_json(TASKS_FILE, tasks)
            print(f"Task {task_id} marked as Completed.")
            return True

    print(f"Task ID {task_id} not found.")
    return False


def delete_task(username: str, task_id: int) -> bool:
    """Delete a task by ID. Returns True if found and removed."""
    tasks = load_json(TASKS_FILE)
    user_tasks = tasks.get(username, [])

    for task in user_tasks:
        if task["id"] == task_id:
            user_tasks.remove(task)
            tasks[username] = user_tasks
            save_json(TASKS_FILE, tasks)
            print(f"Task {task_id} deleted.")
            return True

    print(f"Task ID {task_id} not found.")
    return False


# ---------------------------------------------------------------------------
# Interactive menu-driven interface
# ---------------------------------------------------------------------------

def main():
    print("=== Welcome to Task Manager ===")

    while True:
        choice = input("Do you want to (L)ogin or (R)egister? [L/R]: ").strip().lower()

        if choice == "r":
            username = input("Choose a username: ").strip()
            password = input("Choose a password: ").strip()
            if register_user(username, password):
                break
        elif choice == "l":
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            if login_user(username, password):
                break
        else:
            print("Invalid choice. Please enter 'L' or 'R'.")

    # Task management loop
    while True:
        print("\n1. Add Task\n2. View Tasks\n3. Mark Task Completed\n4. Delete Task\n5. Logout")
        try:
            option = input("Choose an option (1-5): ").strip()

            if option == "1":
                description = input("Task description: ").strip()
                add_task(username, description)

            elif option == "2":
                view_tasks(username)

            elif option == "3":
                task_id = int(input("Task ID to mark completed: ").strip())
                complete_task(username, task_id)

            elif option == "4":
                task_id = int(input("Task ID to delete: ").strip())
                delete_task(username, task_id)

            elif option == "5":
                print(f"Goodbye, {username}!")
                break

            else:
                print("Invalid option. Please choose 1-5.")

        except ValueError:
            print("That doesn't look like a valid number. Please try again.")
        except Exception as e:
            print(f"Unexpected error: {e}. Please try again.")


if __name__ == "__main__":
    main()
