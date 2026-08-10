"""
STUDENT MANAGEMENT SYSTEM
--------------------------
A desktop GUI application built with:
  - Tkinter  -> for the graphical user interface (built into Python)
  - SQLite3  -> for the database (built into Python, no server needed)

HOW TO RUN:
  1. Save this file as student_management_system.py
  2. Open it in IDLE (or double-click it, or run: python student_management_system.py)
  3. Press F5 in IDLE (or Run > Run Module) to start the app
  4. A window will open. A file called "students.db" will be created
     automatically in the same folder the first time you run it.

No installation needed - tkinter and sqlite3 come with standard Python.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


# ======================================================================
# 1. DATABASE LAYER
#    All functions that talk to the SQLite database live here.
#    Keeping this separate from the GUI code makes the project easy
#    to explain and easy to extend later.
# ======================================================================

DB_NAME = "students.db"


def connect_db():
    """Opens (or creates) the database file and returns a connection."""
    conn = sqlite3.connect(DB_NAME)
    return conn


def create_table():
    """Creates the 'students' table the first time the app runs."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT NOT NULL UNIQUE,
            branch TEXT,
            cgpa REAL
        )
    """)
    conn.commit()
    conn.close()


def insert_student(name, roll_no, branch, cgpa):
    """Adds a new student record to the database."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO students (name, roll_no, branch, cgpa) VALUES (?, ?, ?, ?)",
        (name, roll_no, branch, cgpa)
    )
    conn.commit()
    conn.close()


def fetch_all_students():
    """Returns every row in the students table."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_student(record_id, name, roll_no, branch, cgpa):
    """Updates an existing student record by its id."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE students
        SET name = ?, roll_no = ?, branch = ?, cgpa = ?
        WHERE id = ?
    """, (name, roll_no, branch, cgpa, record_id))
    conn.commit()
    conn.close()


def delete_student(record_id):
    """Deletes a student record by its id."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()


def search_students(keyword):
    """Searches students by name or roll number (partial match)."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM students
        WHERE name LIKE ? OR roll_no LIKE ?
    """, (f"%{keyword}%", f"%{keyword}%"))
    rows = cursor.fetchall()
    conn.close()
    return rows


# ======================================================================
# 2. GUI LAYER
#    Everything the user sees and clicks lives in this class.
# ======================================================================

class StudentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("750x520")
        self.root.resizable(False, False)

        self.selected_id = None  # tracks which row is selected for update/delete

        self.build_form()
        self.build_buttons()
        self.build_search_bar()
        self.build_table()

        self.refresh_table()

    # ---------------- FORM (input fields) ----------------
    def build_form(self):
        frame = tk.LabelFrame(self.root, text="Student Details", padx=10, pady=10)
        frame.place(x=10, y=10, width=730, height=110)

        tk.Label(frame, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = tk.Entry(frame, width=25)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Roll No:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.roll_entry = tk.Entry(frame, width=25)
        self.roll_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(frame, text="Branch:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.branch_entry = tk.Entry(frame, width=25)
        self.branch_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame, text="CGPA:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.cgpa_entry = tk.Entry(frame, width=25)
        self.cgpa_entry.grid(row=1, column=3, padx=5, pady=5)

    # ---------------- BUTTONS ----------------
    def build_buttons(self):
        frame = tk.Frame(self.root)
        frame.place(x=10, y=130, width=730, height=40)

        tk.Button(frame, text="Add Student", width=15, bg="#4CAF50", fg="white",
                  command=self.add_student).grid(row=0, column=0, padx=5)

        tk.Button(frame, text="Update Selected", width=15, bg="#2196F3", fg="white",
                  command=self.update_selected).grid(row=0, column=1, padx=5)

        tk.Button(frame, text="Delete Selected", width=15, bg="#f44336", fg="white",
                  command=self.delete_selected).grid(row=0, column=2, padx=5)

        tk.Button(frame, text="Clear Form", width=15,
                  command=self.clear_form).grid(row=0, column=3, padx=5)

    # ---------------- SEARCH BAR ----------------
    def build_search_bar(self):
        frame = tk.Frame(self.root)
        frame.place(x=10, y=180, width=730, height=40)

        tk.Label(frame, text="Search (name / roll no):").grid(row=0, column=0, padx=5)
        self.search_entry = tk.Entry(frame, width=30)
        self.search_entry.grid(row=0, column=1, padx=5)

        tk.Button(frame, text="Search", command=self.search).grid(row=0, column=2, padx=5)
        tk.Button(frame, text="Show All", command=self.refresh_table).grid(row=0, column=3, padx=5)

    # ---------------- TABLE (list of students) ----------------
    def build_table(self):
        columns = ("id", "name", "roll_no", "branch", "cgpa")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=13)

        headings = {"id": "ID", "name": "Name", "roll_no": "Roll No",
                    "branch": "Branch", "cgpa": "CGPA"}
        widths = {"id": 40, "name": 180, "roll_no": 120, "branch": 150, "cgpa": 80}

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col])

        self.tree.place(x=10, y=230, width=730, height=280)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    # ---------------- ACTIONS ----------------
    def add_student(self):
        name = self.name_entry.get().strip()
        roll_no = self.roll_entry.get().strip()
        branch = self.branch_entry.get().strip()
        cgpa = self.cgpa_entry.get().strip()

        if not name or not roll_no:
            messagebox.showwarning("Missing info", "Name and Roll No are required.")
            return

        try:
            cgpa_value = float(cgpa) if cgpa else None
        except ValueError:
            messagebox.showerror("Invalid CGPA", "CGPA must be a number, e.g. 8.83")
            return

        try:
            insert_student(name, roll_no, branch, cgpa_value)
            messagebox.showinfo("Success", f"Student '{name}' added.")
            self.clear_form()
            self.refresh_table()
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate Roll No", "This roll number already exists.")

    def update_selected(self):
        if self.selected_id is None:
            messagebox.showwarning("No selection", "Select a row from the table first.")
            return

        name = self.name_entry.get().strip()
        roll_no = self.roll_entry.get().strip()
        branch = self.branch_entry.get().strip()
        cgpa = self.cgpa_entry.get().strip()

        if not name or not roll_no:
            messagebox.showwarning("Missing info", "Name and Roll No are required.")
            return

        try:
            cgpa_value = float(cgpa) if cgpa else None
        except ValueError:
            messagebox.showerror("Invalid CGPA", "CGPA must be a number, e.g. 8.83")
            return

        update_student(self.selected_id, name, roll_no, branch, cgpa_value)
        messagebox.showinfo("Updated", "Student record updated.")
        self.clear_form()
        self.refresh_table()

    def delete_selected(self):
        if self.selected_id is None:
            messagebox.showwarning("No selection", "Select a row from the table first.")
            return

        confirm = messagebox.askyesno("Confirm delete", "Delete this student record?")
        if confirm:
            delete_student(self.selected_id)
            self.clear_form()
            self.refresh_table()

    def search(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.refresh_table()
            return
        rows = search_students(keyword)
        self.populate_table(rows)

    def on_row_select(self, event):
        """When a table row is clicked, load its data into the form fields."""
        selected = self.tree.focus()
        if not selected:
            return
        values = self.tree.item(selected, "values")
        self.selected_id = int(values[0])
        self.clear_form(keep_selection=True)
        self.name_entry.insert(0, values[1])
        self.roll_entry.insert(0, values[2])
        self.branch_entry.insert(0, values[3])
        self.cgpa_entry.insert(0, values[4])

    def clear_form(self, keep_selection=False):
        self.name_entry.delete(0, tk.END)
        self.roll_entry.delete(0, tk.END)
        self.branch_entry.delete(0, tk.END)
        self.cgpa_entry.delete(0, tk.END)
        if not keep_selection:
            self.selected_id = None

    def refresh_table(self):
        rows = fetch_all_students()
        self.populate_table(rows)

    def populate_table(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", tk.END, values=row)


# ======================================================================
# 3. ENTRY POINT
#    This is what actually runs when you press F5 in IDLE.
# ======================================================================

if __name__ == "__main__":
    create_table()          # make sure the database & table exist
    root = tk.Tk()
    app = StudentApp(root)
    root.mainloop()
