import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime

DB = "hotel.db"

# -----------------------------
# Load Payments
# -----------------------------
def load_payments(tree):
    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.payment_id, r.res_id, c.name, p.amount, p.payment_date, p.method
        FROM payments p
        JOIN reservations r ON p.res_id=r.res_id
        JOIN customers c ON r.customer_id=c.customer_id
    """)
    rows = cursor.fetchall()
    conn.close()

    for i, r in enumerate(rows):
        tag = 'evenrow' if i % 2 == 0 else 'oddrow'
        tree.insert("", "end", values=r, tags=(tag,))

# -----------------------------
# Add Payment
# -----------------------------
def add_payment(tree, res_var, amount_var, date_var, method_var):
    if not res_var.get() or not amount_var.get() or not method_var.get():
        messagebox.showerror("Error", "Select reservation, amount, and method")
        return

    payment_date = date_var.get()

    # Convert reservation ID to integer
    try:
        res_id = int(res_var.get())
    except ValueError:
        messagebox.showerror("Error", "Invalid reservation ID")
        return

    # Convert amount to float
    try:
        amount = float(amount_var.get())
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number")
        return

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # Check reservation exists
    cursor.execute("SELECT res_id FROM reservations WHERE res_id=?", (res_id,))
    res = cursor.fetchone()
    if not res:
        messagebox.showerror("Error", "Reservation not found")
        conn.close()
        return

    # Insert payment
    cursor.execute(
        "INSERT INTO payments(res_id, amount, payment_date, method) VALUES(?,?,?,?)",
        (res_id, amount, payment_date, method_var.get())
    )
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Payment added successfully")
    load_payments(tree)  # Refresh table immediately

# -----------------------------
# Delete Payment
# -----------------------------
def delete_payment(tree):
    selected = tree.focus()
    if not selected:
        messagebox.showerror("Error", "Select a payment")
        return

    payment_id = tree.item(selected)["values"][0]

    if not messagebox.askyesno("Confirm", "Delete this payment?"):
        return

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM payments WHERE payment_id=?", (payment_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Deleted", "Payment deleted successfully")
    load_payments(tree)  # Refresh table

# -----------------------------
# Payments Page UI
# -----------------------------
def payments_page(frame):
    # Clear frame
    for w in frame.winfo_children():
        w.destroy()
    frame.config(bg="#ecf0f1")

    # Title
    tk.Label(frame, text="Payments", font=("Arial", 22, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=10)

    form_frame = tk.Frame(frame, bg="#ecf0f1")
    form_frame.pack(pady=5, padx=20)

    # Fetch reservations
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT res_id FROM reservations")
    reservations = [r[0] for r in cursor.fetchall()]
    conn.close()

    # ---------------------
    # Form fields
    # ---------------------
    tk.Label(form_frame, text="Reservation ID:", bg="#ecf0f1").grid(row=0, column=0, padx=5, pady=5)
    res_var = ttk.Combobox(form_frame, values=reservations, width=25)
    res_var.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Amount:", bg="#ecf0f1").grid(row=1, column=0, padx=5, pady=5)
    amount_var = tk.Entry(form_frame, width=27)
    amount_var.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Payment Date:", bg="#ecf0f1").grid(row=2, column=0, padx=5, pady=5)
    date_var = DateEntry(form_frame, date_pattern="yyyy-mm-dd", width=25)
    date_var.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Method:", bg="#ecf0f1").grid(row=3, column=0, padx=5, pady=5)
    method_var = ttk.Combobox(form_frame, values=["Cash", "Card", "Online"], width=25)
    method_var.grid(row=3, column=1, padx=5, pady=5)

    # ---------------------
    # Buttons
    # ---------------------
    btn_frame = tk.Frame(form_frame, bg="#ecf0f1")
    btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

    # Table
    tree = ttk.Treeview(frame, columns=("Payment ID", "Reservation ID", "Customer", "Amount", "Date", "Method"),
                        show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=120)

    tree.tag_configure("evenrow", background="#f2f2f2")
    tree.tag_configure("oddrow", background="#ffffff")
    tree.pack(pady=10, fill="both", expand=True, padx=20)

    # Action Buttons
    tk.Button(btn_frame, text="Add Payment", bg="#27ae60", fg="white",
              command=lambda: add_payment(tree, res_var, amount_var, date_var, method_var)).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Delete Payment", bg="#c0392b", fg="white",
              command=lambda: delete_payment(tree)).grid(row=0, column=1, padx=5)

    # Load initial data
    load_payments(tree)
