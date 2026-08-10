#  Student Management System — Tkinter + SQLite

A desktop GUI application for managing student records — add, update, delete, and search —
built entirely with **Tkinter** (GUI) and **SQLite3** (storage), both part of the Python
standard library. No installation or external server required.

This document is the single source of truth for setup, features, and the database schema.

---

## 1. Tech stack & versions
[#1-tech-stack--versions](#1-tech-stack--versions)

| Layer      | Technology                          |
| ---------- | ------------------------------------ |
| Language   | Python 3                            |
| GUI        | Tkinter + `ttk` (Treeview widget)   |
| Database   | SQLite 3 (`students.db`, file-based) |

**Verified compatible with:** Python 3.8+. `tkinter` and `sqlite3` ship with standard Python —
no `pip install` needed at all.

---

## 2. Project structure
[#2-project-structure](#2-project-structure)

```
StudentDataUsingTkinter/
├── student_project.py       # Full app: database layer + GUI layer + entry point
├── students.db               # SQLite database file (auto-created on first run)
└── README.md                 # (this file)
```

### Application layers
[#application-layers](#application-layers)

```
┌───────────────────────┐        ┌───────────────────────┐        ┌──────────────┐
│   GUI Layer            │  calls │   Database Layer       │  reads │  SQLite DB   │
│   (StudentApp class)   │───────►│   (connect/insert/     │───────►│  students.db │
│   forms, table, search │◄───────│    update/delete/fetch)│◄───────│  (students)  │
└───────────────────────┘        └───────────────────────┘        └──────────────┘
```

- **Database layer** (`connect_db`, `create_table`, `insert_student`, `fetch_all_students`,
`update_student`, `delete_student`, `search_students`) — all SQLite interaction lives here,
kept separate from the GUI so each can be understood and extended independently.
- **GUI layer** (`StudentApp` class) — builds the form, action buttons, search bar, and a
`ttk.Treeview` table; wires button clicks to the database functions above.
- **Entry point** — `create_table()` runs first to make sure `students.db` and its table
exist, then the Tkinter main loop starts.

---

## 3. Features
[#3-features](#3-features)

| Feature          | How it works                                                          |
| ----------------- | ------------------------------------------------------------------------ |
| Add student       | Fill the form → **Add Student** → inserts a new row                    |
| Update student    | Click a row (auto-fills form) → edit fields → **Update Selected**      |
| Delete student    | Click a row → **Delete Selected** → confirmation prompt → row removed  |
| Search            | Type a name or roll number (partial match) → **Search**                |
| Show all          | **Show All** clears the search filter and reloads every record         |
| Clear form        | **Clear Form** empties all input fields and deselects the current row  |
| Duplicate roll no  | Blocked at insert time via a `UNIQUE` constraint + friendly error popup |
| CGPA validation    | Rejects non-numeric CGPA input with an error popup before saving       |

---

## 4. Database schema
[#4-database-schema](#4-database-schema)

### students

[#students](#students)

```sql
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    roll_no TEXT NOT NULL UNIQUE,
    branch TEXT,
    cgpa REAL
)
```

- `id` — auto-incrementing primary key, used internally to target update/delete operations.
- `roll_no` — required and unique; duplicate roll numbers are caught and reported to the user
rather than silently failing.
- `branch` and `cgpa` are optional; `cgpa` is stored as `NULL` if left blank.

---

## 5. Running the project locally
[#5-running-the-project-locally](#5-running-the-project-locally)

### Prerequisites
[#prerequisites](#prerequisites)

- Python 3.8+ (Tkinter is included in standard Windows/macOS installers; on Linux you may
need `sudo apt install python3-tk` if it's missing)

### Step-by-step
[#step-by-step](#step-by-step)

```bash
# 1. Clone the repository
git clone https://github.com/meghanacheppulla/StudentDataUsingTkinter.git
cd StudentDataUsingTkinter

# 2. Run the app — no dependencies to install
python student_project.py
```

A window titled **"Student Management System"** opens. `students.db` is created
automatically in the same folder the first time you run it, and reused on every run after
that.

---

## 6. Design notes
[#6-design-notes](#6-design-notes)

- **Why separate the database layer from the GUI class?** Each database function
(`insert_student`, `update_student`, etc.) opens and closes its own connection and takes
plain arguments — this keeps them easy to test or reuse outside the GUI (e.g. from a script
or a future CLI) without touching Tkinter code at all.
- **Why `ttk.Treeview` for the record list?** It's the standard Tkinter widget for tabular
data with sortable, resizable columns, and it supports row selection out of the box —
exactly what's needed to click a row and load it back into the edit form.
- **Why validate CGPA as a float before inserting?** Catching bad input (e.g. text in the
CGPA field) at the GUI layer with a clear popup avoids a raw SQLite error reaching the user.

---

## 7. Git workflow conventions
[#7-git-workflow-conventions](#7-git-workflow-conventions)

- **Branching:** `main` (always runnable) ← feature branches named
`feature/<short-description>`, `fix/<short-description>`.
- **Commits:** [Conventional Commits](https://www.conventionalcommits.org/) style —
`feat: add search bar`, `fix: prevent duplicate roll numbers`, `docs: update README`.
- **`.gitignore`:** consider excluding `students.db` if you don't want sample/test data
committed — it regenerates automatically on first run.

---

## 8. Roadmap
[#8-roadmap](#8-roadmap)

### ✅ Phase 1 — Core CRUD (this deliverable)
[#-phase-1--core-crud-this-deliverable](#-phase-1--core-crud-this-deliverable)

- Add / update / delete / search students
- Auto-created database and table on first run
- Duplicate roll number and invalid CGPA handling

### 🔜 Phase 2 — Enhancements
[#-phase-2--enhancements](#-phase-2--enhancements)

- Export records to CSV/Excel
- Sort table by clicking column headers
- Confirm-on-clear if the form has unsaved edits
- Basic input length limits / stricter validation on `name` and `branch`
- Package as a standalone `.exe` (e.g. with PyInstaller) for easier distribution

---

## 9. Known MVP-scope trade-offs (intentional, documented)
[#9-known-mvp-scope-trade-offs-intentional-documented](#9-known-mvp-scope-trade-offs-intentional-documented)

- No pagination — `fetch_all_students()` loads every row into the table at once, which is
fine for classroom-scale data but wouldn't scale to a very large student list.
- No confirmation before overwriting the form when clicking a different row mid-edit — any
unsaved changes in the form are silently replaced.
- The database file (`students.db`) is a fixed relative path (`DB_NAME = "students.db"`), so
the app must always be run from its own folder.

---

B.Tech CSE, Aditya University
