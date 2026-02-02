import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB = "hotel.db"

# -----------------------------
# Load Staff
# -----------------------------
def load_staff(tree):
    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM staff")
    rows = cursor.fetchall()
    conn.close()

    for r in rows:
        tree.insert("", "end", values=r)


# -----------------------------
# Add Staff
# -----------------------------
def add_staff(tree, name, phone, role, salary):
    if not name:
        messagebox.showerror("Error", "Name is required")
        return

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO staff(name, phone, role, salary) VALUES (?, ?, ?, ?)",
                   (name, phone, role, salary))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Staff added successfully")
    load_staff(tree)


# -----------------------------
# Update Staff
# -----------------------------
def update_staff(tree, staff_id, name, phone, role, salary):
    if not name:
        messagebox.showerror("Error", "Name is required")
        return

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE staff SET name=?, phone=?, role=?, salary=? WHERE staff_id=?",
                   (name, phone, role, salary, staff_id))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Staff updated successfully")
    load_staff(tree)


# -----------------------------
# Delete Staff
# -----------------------------
def delete_staff(tree):
    selected = tree.focus()
    if not selected:
        messagebox.showerror("Error", "Select a staff member")
        return

    staff_id = tree.item(selected)["values"][0]

    if not messagebox.askyesno("Confirm", "Delete this staff member?"):
        return

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM staff WHERE staff_id=?", (staff_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Deleted", "Staff member deleted")
    load_staff(tree)


# -----------------------------
# Search Staff
# -----------------------------
def search_staff(tree, search_var):
    val = search_var.get()
    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM staff WHERE name LIKE ? OR role LIKE ?", (f"%{val}%", f"%{val}%"))
    rows = cursor.fetchall()
    conn.close()

    for r in rows:
        tree.insert("", "end", values=r)


# -----------------------------
# Staff Page UI
# -----------------------------
def staff_page(frame):
    for w in frame.winfo_children():
        w.destroy()

    tk.Label(frame, text="Staff Management", font=("Arial", 22, "bold"), bg="#ecf0f1").pack(pady=10)

    form_frame = tk.Frame(frame, bg="#ecf0f1")
    form_frame.pack(pady=5)

    # Form fields
    tk.Label(form_frame, text="Name:", bg="#ecf0f1").grid(row=0, column=0, padx=5, pady=5)
    name_entry = tk.Entry(form_frame)
    name_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Phone:", bg="#ecf0f1").grid(row=1, column=0, padx=5, pady=5)
    phone_entry = tk.Entry(form_frame)
    phone_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Role:", bg="#ecf0f1").grid(row=2, column=0, padx=5, pady=5)
    role_entry = tk.Entry(form_frame)
    role_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Salary:", bg="#ecf0f1").grid(row=3, column=0, padx=5, pady=5)
    salary_entry = tk.Entry(form_frame)
    salary_entry.grid(row=3, column=1, padx=5, pady=5)

    # Buttons frame
    btn_frame = tk.Frame(form_frame, bg="#ecf0f1")
    btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

    # Table
    tree = ttk.Treeview(frame, columns=("ID", "Name", "Phone", "Role", "Salary"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(pady=10, fill="x", padx=20)

    # Action Buttons
    tk.Button(btn_frame, text="Add", bg="#27ae60", fg="white",
              command=lambda: add_staff(tree, name_entry.get(), phone_entry.get(), role_entry.get(),
                                        salary_entry.get())).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Update", bg="#2980b9", fg="white",
              command=lambda: update_staff(tree, tree.item(tree.focus())["values"][0], name_entry.get(),
                                           phone_entry.get(), role_entry.get(), salary_entry.get())).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="Delete", bg="#c0392b", fg="white",
              command=lambda: delete_staff(tree)).grid(row=0, column=2, padx=5)

    # Search
    search_frame = tk.Frame(frame, bg="#ecf0f1")
    search_frame.pack(pady=10)
    tk.Label(search_frame, text="Search:", bg="#ecf0f1").grid(row=0, column=0, padx=5)
    search_var = tk.Entry(search_frame)
    search_var.grid(row=0, column=1, padx=5)
    tk.Button(search_frame, text="Search", bg="#f39c12", fg="white",
              command=lambda: search_staff(tree, search_var)).grid(row=0, column=2, padx=5)
    tk.Button(search_frame, text="Show All", bg="#16a085", fg="white",
              command=lambda: load_staff(tree)).grid(row=0, column=3, padx=5)

    # Load initial data
    load_staff(tree)
