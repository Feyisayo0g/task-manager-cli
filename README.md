# Secure Multi-User Task Manager

A command-line task management system built around one core constraint: **multiple users, one file store, zero data leakage between them.** It implements salted credential hashing, per-user data isolation, full CRUD task operations, and defensive input handling — the same foundational patterns that carry into production ML systems (securing API keys and model endpoints, scoping data per tenant, handling malformed input gracefully).

📓 **[Full write-up + annotated code (Jupyter Notebook)](./task_manager_project.ipynb)** — includes design rationale for every decision below, plus a fully executed demo showing output.

---

## Why this exists

Before a model ever reaches production, the system around it needs to get the fundamentals right — secure credential handling, clean data modeling, and inputs that fail safely instead of crashing. This project is a deliberate, scoped exercise in exactly that, built with the reasoning behind each decision made explicit rather than left implicit. *(Built while deepening my AI/ML engineering skill set through UT Dallas x Fullstack Academy's AI & ML program.)*

## What it does

- **Register / Login** — username + password authentication
- **Add / View / Complete / Delete** tasks, scoped entirely to the logged-in user
- **Persistent storage** — all data survives across sessions via JSON files
- **Graceful failure** — invalid input, duplicate usernames, and wrong passwords are all handled without crashing the program

## Design decisions worth knowing about

| Decision | Why |
|---|---|
| **Salted SHA-256 hashing** (not plaintext) | Even if the storage file leaked, passwords aren't recoverable, and two identical passwords never produce the same hash |
| **`secrets.token_hex`** for salts (not `random`) | Cryptographically secure randomness — matters even in a small system |
| **Per-user nested data structure** (`{username: [tasks]}`) | Same isolation principle multi-tenant SaaS systems use to keep one user's data from ever touching another's |
| **`try/except` around every input path** | Bad input degrades gracefully instead of taking down the whole program |

**What I'd change for real production use:** swap SHA-256 + manual salting for `bcrypt` or `argon2` (intentionally slow, purpose-built for password hashing — fast hashing is actually a liability at scale), replace the JSON files with a proper database to handle concurrent writes safely, and replace `print()` statements with structured logging.

## Tech stack

`Python` · `hashlib` · `secrets` · `json`

## Run it

```bash
git clone https://github.com/<your-username>/task-manager-cli.git
cd task-manager-cli
python task_manager.py
```

Or open `task_manager_project.ipynb` in Jupyter to step through the code, design rationale, and a fully executed demo (register → login → add/complete/delete tasks → view final state) without needing a live terminal.

## Project structure

```
task-manager-cli/
├── task_manager.py              # Standalone script version (run directly)
├── task_manager_project.ipynb   # Annotated notebook: code + design write-up + demo
└── README.md
```

---

**Author:** Feyisayo Ogunmade — Lead Data Analyst (AT&T) transitioning into AI/ML Engineering. More projects and case studies at [feyisayoogunmade.com](https://feyisayoogunmade.com) · [LinkedIn](#)
