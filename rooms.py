import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB = "hotel.db"

# -----------------------------
# Load Rooms
# -----------------------------
def load_rooms(tree, filter_type=None, only_available=False):
    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    query = "SELECT * FROM rooms WHERE 1=1"
    params = []

    if filter_type:
        query += " AND room_type=?"
        params.append(filter_type)
    if only_available:
        query += " AND status='Available'"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    for r in rows:
        tree.insert("", "end", values=r)


# -----------------------------
# Add Room
# -----------------------------
def add_room(tree, room_no, room_type, bed, price, status):
    if not room_no or not price:
        messagebox.showerror("Error", "Room No and Price are required")
        return

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO rooms (room_no, room_type, bed, price, status) VALUES (?, ?, ?, ?, ?)",
                       (room_no, room_type, bed, price, status))
        conn.commit()
        messagebox.showinfo("Success", "Room added successfully")
        load_rooms(tree)
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Room No already exists")
    finally:
        conn.close()


# -----------------------------
# Update Room
# -----------------------------
def update_room(tree, room_id, room_no, room_type, bed, price, status):
    if not room_no or not price:
        messagebox.showerror("Error", "Room No and Price are required")
        return

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("""UPDATE rooms 
                      SET room_no=?, room_type=?, bed=?, price=?, status=? 
                      WHERE room_id=?""",
                   (room_no, room_type, bed, price, status, room_id))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Room updated successfully")
    load_rooms(tree)


# -----------------------------
# Delete Room
# -----------------------------
def delete_room(tree):
    selected = tree.focus()
    if not selected:
        messagebox.showerror("Error", "Select a room to delete")
        return

    room_id = tree.item(selected)["values"][0]

    if not messagebox.askyesno("Confirm", "Delete this room?"):
        return

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rooms WHERE room_id=?", (room_id,))
    conn.commit()
    conn.close()

    messagebox.showinfo("Deleted", "Room deleted successfully")
    load_rooms(tree)


# -----------------------------
# Search Rooms
# -----------------------------
def search_rooms(tree, search_var):
    val = search_var.get()
    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rooms WHERE room_no LIKE ? OR room_type LIKE ?", (f"%{val}%", f"%{val}%"))
    rows = cursor.fetchall()
    conn.close()

    for r in rows:
        tree.insert("", "end", values=r)


# -----------------------------
# Change Status
# -----------------------------
def change_status(tree, new_status):
    selected = tree.focus()
    if not selected:
        messagebox.showerror("Error", "Select a room")
        return

    room_id = tree.item(selected)["values"][0]

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE rooms SET status=? WHERE room_id=?", (new_status, room_id))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", f"Status changed to {new_status}")
    load_rooms(tree)


# -----------------------------
# Rooms Page UI
# -----------------------------
def rooms_page(frame):
    for w in frame.winfo_children():
        w.destroy()

    tk.Label(frame, text="Rooms Management", font=("Arial", 22, "bold"), bg="#ecf0f1").pack(pady=10)

    form_frame = tk.Frame(frame, bg="#ecf0f1")
    form_frame.pack(pady=5)

    # Form Fields
    tk.Label(form_frame, text="Room No:", bg="#ecf0f1").grid(row=0, column=0, padx=5, pady=5)
    room_no_entry = tk.Entry(form_frame)
    room_no_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Type:", bg="#ecf0f1").grid(row=1, column=0, padx=5, pady=5)
    type_entry = ttk.Combobox(form_frame, values=["Single", "Double", "Deluxe"])
    type_entry.grid(row=1, column=1, padx=5, pady=5)
    type_entry.current(0)

    tk.Label(form_frame, text="Bed:", bg="#ecf0f1").grid(row=2, column=0, padx=5, pady=5)
    bed_entry = ttk.Combobox(form_frame, values=["Single", "Double", "King"])
    bed_entry.grid(row=2, column=1, padx=5, pady=5)
    bed_entry.current(0)

    tk.Label(form_frame, text="Price:", bg="#ecf0f1").grid(row=3, column=0, padx=5, pady=5)
    price_entry = tk.Entry(form_frame)
    price_entry.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Status:", bg="#ecf0f1").grid(row=4, column=0, padx=5, pady=5)
    status_entry = ttk.Combobox(form_frame, values=["Available", "Booked"])
    status_entry.grid(row=4, column=1, padx=5, pady=5)
    status_entry.current(0)

    # Buttons Frame
    btn_frame = tk.Frame(form_frame, bg="#ecf0f1")
    btn_frame.grid(row=5, column=0, columnspan=2, pady=10)

    # Table
    tree = ttk.Treeview(frame, columns=("ID", "Room No", "Type", "Bed", "Price", "Status"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(pady=10, fill="x", padx=20)

    # Action Buttons
    tk.Button(btn_frame, text="Add", bg="#27ae60", fg="white",
              command=lambda: add_room(tree, room_no_entry.get(), type_entry.get(), bed_entry.get(),
                                       price_entry.get(), status_entry.get())).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Update", bg="#2980b9", fg="white",
              command=lambda: update_room(tree, tree.item(tree.focus())["values"][0],
                                          room_no_entry.get(), type_entry.get(), bed_entry.get(),
                                          price_entry.get(), status_entry.get())).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="Delete", bg="#c0392b", fg="white",
              command=lambda: delete_room(tree)).grid(row=0, column=2, padx=5)
    tk.Button(btn_frame, text="Change Status", bg="#8e44ad", fg="white",
              command=lambda: change_status(tree, status_entry.get())).grid(row=0, column=3, padx=5)

    # Search and Filter Frame
    search_frame = tk.Frame(frame, bg="#ecf0f1")
    search_frame.pack(pady=10)

    tk.Label(search_frame, text="Search:", bg="#ecf0f1").grid(row=0, column=0, padx=5)
    search_var = tk.Entry(search_frame)
    search_var.grid(row=0, column=1, padx=5)
    tk.Button(search_frame, text="Search", bg="#f39c12", fg="white",
              command=lambda: search_rooms(tree, search_var)).grid(row=0, column=2, padx=5)
    tk.Button(search_frame, text="Show All", bg="#16a085", fg="white",
              command=lambda: load_rooms(tree)).grid(row=0, column=3, padx=5)
    tk.Button(search_frame, text="Available Only", bg="#e67e22", fg="white",
              command=lambda: load_rooms(tree, only_available=True)).grid(row=0, column=4, padx=5)

    # Filter by Type
    tk.Label(search_frame, text="Filter Type:", bg="#ecf0f1").grid(row=1, column=0, padx=5)
    filter_type = ttk.Combobox(search_frame, values=["Single", "Double", "Deluxe"])
    filter_type.grid(row=1, column=1, padx=5)
    filter_type.current(0)
    tk.Button(search_frame, text="Apply Filter", bg="#d35400", fg="white",
              command=lambda: load_rooms(tree, filter_type.get())).grid(row=1, column=2, padx=5)

    # Load initial data
    load_rooms(tree)
