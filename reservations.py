import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime

DB = "hotel.db"

# -----------------------------
# Load Reservations
# -----------------------------
def load_reservations(tree):
    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.res_id,
               c.name,
               ro.room_no,
               r.check_in,
               r.check_out,
               r.total_days,
               r.total_cost,
               r.status
        FROM reservations r
        JOIN customers c ON r.customer_id = c.customer_id
        JOIN rooms ro ON r.room_id = ro.room_id
    """)
    rows = cursor.fetchall()
    conn.close()

    for i, r in enumerate(rows):
        tag = 'evenrow' if i % 2 == 0 else 'oddrow'
        tree.insert("", "end", values=r, tags=(tag,))


# -----------------------------
# Add Reservation
# -----------------------------
def add_reservation(tree, customer_var, room_var, checkin_entry, checkout_entry):
    if not customer_var.get() or not room_var.get():
        messagebox.showerror("Error", "Select customer and room")
        return

    check_in = checkin_entry.get()
    check_out = checkout_entry.get()

    try:
        ci = datetime.strptime(check_in, "%Y-%m-%d")
        co = datetime.strptime(check_out, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Error", "Invalid date format")
        return

    total_days = (co - ci).days
    if total_days <= 0:
        messagebox.showerror("Error", "Check-out must be after check-in")
        return

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # Get customer ID
    cursor.execute("SELECT customer_id FROM customers WHERE name=?", (customer_var.get(),))
    customer = cursor.fetchone()
    if not customer:
        messagebox.showerror("Error", "Customer not found")
        conn.close()
        return
    customer_id = customer[0]

    # Get room ID and price
    cursor.execute("SELECT room_id, price FROM rooms WHERE room_no=? AND status='Available'", (room_var.get(),))
    room = cursor.fetchone()
    if not room:
        messagebox.showerror("Error", "Room not available")
        conn.close()
        return
    room_id, price = room

    total_cost = total_days * price

    # Insert reservation
    cursor.execute("""
        INSERT INTO reservations
        (customer_id, room_id, check_in, check_out, total_days, total_cost, status)
        VALUES (?, ?, ?, ?, ?, ?, 'Active')
    """, (customer_id, room_id, check_in, check_out, total_days, total_cost))

    # Update room status
    cursor.execute("UPDATE rooms SET status='Booked' WHERE room_id=?", (room_id,))

    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Reservation added successfully")
    load_reservations(tree)
    # Optionally refresh available rooms in the combobox
    refresh_rooms(tree, room_var)


# -----------------------------
# Delete Reservation
# -----------------------------
def delete_reservation(tree):
    selected = tree.focus()
    if not selected:
        messagebox.showerror("Error", "Select a reservation")
        return

    res_id = tree.item(selected)["values"][0]

    if not messagebox.askyesno("Confirm", "Delete this reservation?"):
        return

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # Get room id
    cursor.execute("SELECT room_id FROM reservations WHERE res_id=?", (res_id,))
    room_id = cursor.fetchone()[0]

    # Free the room
    cursor.execute("UPDATE rooms SET status='Available' WHERE room_id=?", (room_id,))

    # Delete reservation
    cursor.execute("DELETE FROM reservations WHERE res_id=?", (res_id,))
    conn.commit()
    conn.close()

    messagebox.showinfo("Deleted", "Reservation deleted")
    load_reservations(tree)
    # Optionally refresh rooms in combobox
    refresh_rooms(tree)


# -----------------------------
# Refresh available rooms
# -----------------------------
def refresh_rooms(tree=None, room_var=None):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT room_no FROM rooms WHERE status='Available'")
    rooms = [r[0] for r in cursor.fetchall()]
    conn.close()

    if room_var:
        room_var['values'] = rooms
        if rooms:
            room_var.set(rooms[0])
        else:
            room_var.set('')

# -----------------------------
# Reservations Page UI
# -----------------------------
def reservations_page(frame):
    # Clear frame
    for w in frame.winfo_children():
        w.destroy()
    frame.config(bg="#ecf0f1")

    # Title
    tk.Label(
        frame,
        text="Reservations Management",
        font=("Arial", 22, "bold"),
        bg="#ecf0f1",
        fg="#2c3e50"
    ).pack(pady=15)

    # Form Frame
    form_frame = tk.Frame(frame, bg="#ecf0f1")
    form_frame.pack(pady=10, padx=20)

    # Fetch customers & available rooms
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM customers")
    customers = [c[0] for c in cursor.fetchall()]

    cursor.execute("SELECT room_no FROM rooms WHERE status='Available'")
    rooms = [r[0] for r in cursor.fetchall()]
    conn.close()

    # Customer
    tk.Label(form_frame, text="Customer:", bg="#ecf0f1", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5)
    customer_var = ttk.Combobox(form_frame, values=customers, width=25)
    customer_var.grid(row=0, column=1, padx=5, pady=5)

    # Room
    tk.Label(form_frame, text="Room:", bg="#ecf0f1", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5)
    room_var = ttk.Combobox(form_frame, values=rooms, width=25)
    room_var.grid(row=1, column=1, padx=5, pady=5)

    # Check-in
    tk.Label(form_frame, text="Check-in:", bg="#ecf0f1", font=("Arial", 12)).grid(row=2, column=0, padx=5, pady=5)
    checkin_entry = DateEntry(form_frame, date_pattern="yyyy-mm-dd", width=22)
    checkin_entry.grid(row=2, column=1, padx=5, pady=5)

    # Check-out
    tk.Label(form_frame, text="Check-out:", bg="#ecf0f1", font=("Arial", 12)).grid(row=3, column=0, padx=5, pady=5)
    checkout_entry = DateEntry(form_frame, date_pattern="yyyy-mm-dd", width=22)
    checkout_entry.grid(row=3, column=1, padx=5, pady=5)

    # ---------------------
    # Table (Treeview)
    # ---------------------
    tree = ttk.Treeview(
        frame,
        columns=("ID", "Customer", "Room", "Check-in", "Check-out", "Days", "Cost", "Status"),
        show="headings"
    )
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=120)

    tree.tag_configure("evenrow", background="#f2f2f2")
    tree.tag_configure("oddrow", background="#ffffff")
    tree.pack(fill="both", expand=True, padx=20, pady=10)

    # ---------------------
    # Buttons
    # ---------------------
    btn_frame = tk.Frame(form_frame, bg="#ecf0f1")
    btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

    tk.Button(
        btn_frame,
        text="Add Reservation",
        bg="#27ae60",
        fg="white",
        command=lambda: add_reservation(
            tree, customer_var, room_var, checkin_entry, checkout_entry
        )
    ).grid(row=0, column=0, padx=5)

    tk.Button(
        btn_frame,
        text="Delete Reservation",
        bg="#c0392b",
        fg="white",
        command=lambda: delete_reservation(tree)
    ).grid(row=0, column=1, padx=5)

    # Load data into treeview
    load_reservations(tree)
