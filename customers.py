import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_NAME = "hotel.db"

# -------------------------------------------
# Function to load the CUSTOMER PAGE inside main_area
# -------------------------------------------
def customer_page(frame):
    # Clear previous content
    for widget in frame.winfo_children():
        widget.destroy()

    # Page title
    tk.Label(frame, text="Customer Management", font=("Arial", 20, "bold"), bg="#ecf0f1").pack(pady=15)

    # Table Frame
    table_frame = tk.Frame(frame, bg="#ecf0f1")
    table_frame.pack(pady=10)

    # Customer Table (Treeview)
    columns = ("ID", "Name", "Phone", "Nationality", "Gender", "DOB", "Address")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)

    tree.pack()

    # Load data initially
    load_customers(tree)

    # Buttons Frame
    btn_frame = tk.Frame(frame, bg="#ecf0f1")
    btn_frame.pack(pady=20)

    tk.Button(btn_frame, text="Add Customer", width=15, command=lambda: add_customer(tree)).grid(row=0, column=0, padx=10)
    tk.Button(btn_frame, text="Edit Customer", width=15, command=lambda: edit_customer(tree)).grid(row=0, column=1, padx=10)
    tk.Button(btn_frame, text="Delete Customer", width=15, command=lambda: delete_customer(tree)).grid(row=0, column=2, padx=10)
    tk.Button(btn_frame, text="Refresh", width=15, command=lambda: load_customers(tree)).grid(row=0, column=3, padx=10)


# -------------------------------------------
# FETCH ALL CUSTOMERS
# -------------------------------------------
def load_customers(tree):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT * FROM customers")
    rows = cur.fetchall()

    tree.delete(*tree.get_children())  # Clear table

    for row in rows:
        tree.insert("", "end", values=row)

    conn.close()


# -------------------------------------------
# ADD CUSTOMER WINDOW
# -------------------------------------------
def add_customer(tree):
    add_win = tk.Toplevel()
    add_win.title("Add Customer")
    add_win.geometry("400x450")

    labels = ["Name", "Phone", "Nationality", "Gender", "DOB (YYYY-MM-DD)", "Address"]
    entries = []

    for i, label_text in enumerate(labels):
        tk.Label(add_win, text=label_text).pack(pady=5)
        entry = tk.Entry(add_win, width=30)
        entry.pack()
        entries.append(entry)

    def save_customer():
        values = [e.get() for e in entries]

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO customers (name, phone, nationality, gender, dob, address)
            VALUES (?, ?, ?, ?, ?, ?)
        """, values)
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Customer added successfully!")
        add_win.destroy()
        load_customers(tree)

    tk.Button(add_win, text="Save", width=20, command=save_customer).pack(pady=20)


# -------------------------------------------
# EDIT CUSTOMER WINDOW
# -------------------------------------------
def edit_customer(tree):
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Warning", "Please select a customer to edit.")
        return

    values = tree.item(selected, "values")
    customer_id = values[0]

    edit_win = tk.Toplevel()
    edit_win.title("Edit Customer")
    edit_win.geometry("400x450")

    labels = ["Name", "Phone", "Nationality", "Gender", "DOB (YYYY-MM-DD)", "Address"]
    entries = []

    for i, label_text in enumerate(labels):
        tk.Label(edit_win, text=label_text).pack(pady=5)
        entry = tk.Entry(edit_win, width=30)
        entry.insert(0, values[i+1])
        entry.pack()
        entries.append(entry)

    def update_customer():
        updated_vals = [e.get() for e in entries]

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        cur.execute("""
            UPDATE customers
            SET name=?, phone=?, nationality=?, gender=?, dob=?, address=?
            WHERE customer_id=?
        """, updated_vals + [customer_id])

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Customer updated successfully!")
        edit_win.destroy()
        load_customers(tree)

    tk.Button(edit_win, text="Update", width=20, command=update_customer).pack(pady=20)


# -------------------------------------------
# DELETE CUSTOMER
# -------------------------------------------
def delete_customer(tree):
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Warning", "Select a customer to delete.")
        return

    values = tree.item(selected, "values")
    customer_id = values[0]

    confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this customer?")
    if not confirm:
        return

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM customers WHERE customer_id=?", (customer_id,))
    conn.commit()
    conn.close()

    messagebox.showinfo("Deleted", "Customer deleted successfully!")
    load_customers(tree)
