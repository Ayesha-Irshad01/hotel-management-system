import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import sqlite3
import main  # your main.py dashboard

DB = "hotel.db"

# -----------------------------
# Database Initialization
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("admin", "admin123"))
    conn.commit()
    conn.close()

def check_login(username, password):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def register_user(username, password):
    try:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

# -----------------------------
# Styled Button
# -----------------------------
def styled_button(master, text, command, bg="#3498db", fg="white"):
    return tk.Button(master, text=text, bg=bg, fg=fg, font=("Arial", 12, "bold"),
                     activebackground="#2ecc71", activeforeground="white", bd=0, relief="flat",
                     command=command, cursor="hand2")

# -----------------------------
# Login/Register Page
# -----------------------------
def login_register_page(root):
    for widget in root.winfo_children():
        widget.destroy()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Background Image
    bg_img = Image.open("bg.jpg")  
 
    bg_img = bg_img.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_img)
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    root.bg_photo = bg_photo

    # -----------------------------
    # Card Frame (rounded corners effect)
    # -----------------------------
    card_width = 400
    card_height = 400
    card_x = screen_width // 2 - card_width // 2
    card_y = screen_height // 2 - card_height // 2

    canvas = tk.Canvas(root, width=card_width, height=card_height, bg="#ffffff", highlightthickness=0)
    canvas.place(x=card_x, y=card_y)

    # Rounded rectangle
    radius = 20
    def round_rect(x1, y1, x2, y2, r=25, **kwargs):
        points = [x1+r, y1,
                  x1+r, y1,
                  x2-r, y1,
                  x2-r, y1,
                  x2, y1,
                  x2, y1+r,
                  x2, y1+r,
                  x2, y2-r,
                  x2, y2-r,
                  x2, y2,
                  x2-r, y2,
                  x2-r, y2,
                  x1+r, y2,
                  x1+r, y2,
                  x1, y2,
                  x1, y2-r,
                  x1, y2-r,
                  x1, y1+r,
                  x1, y1+r,
                  x1, y1]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    round_rect(0, 0, card_width, card_height, r=radius, fill="#ffffff", outline="#cccccc")

    # -----------------------------
    # Tabs (Login/Register)
    # -----------------------------
    tab_frame = tk.Frame(canvas, bg="#ffffff")
    tab_frame.place(x=0, y=10, width=card_width, height=40)

    login_btn = tk.Button(tab_frame, text="Login", bg="#27ae60", fg="white", bd=0, font=("Arial", 12, "bold"))
    login_btn.place(x=0, y=0, width=card_width//2, height=40)
    register_btn = tk.Button(tab_frame, text="Register", bg="#bdc3c7", fg="white", bd=0, font=("Arial", 12, "bold"))
    register_btn.place(x=card_width//2, y=0, width=card_width//2, height=40)

    form_frame = tk.Frame(canvas, bg="#ffffff")
    form_frame.place(x=20, y=70, width=card_width-40, height=card_height-100)

    # -----------------------------
    # Login Form
    # -----------------------------
    login_frame = tk.Frame(form_frame, bg="#ffffff")
    login_frame.pack(fill="both", expand=True)

    tk.Label(login_frame, text="Username", bg="#ffffff").pack(pady=10)
    login_user = tk.Entry(login_frame, font=("Arial", 12))
    login_user.pack(pady=5, fill="x")
    tk.Label(login_frame, text="Password", bg="#ffffff").pack(pady=10)
    login_pass = tk.Entry(login_frame, show="*", font=("Arial", 12))
    login_pass.pack(pady=5, fill="x")

    def login_action():
        if check_login(login_user.get(), login_pass.get()):
            messagebox.showinfo("Success", f"Welcome {login_user.get()}!")
            for widget in root.winfo_children():
                widget.destroy()
            main.open_main_window(root)
        else:
            messagebox.showerror("Error", "Invalid username or password")

    styled_button(login_frame, "Login", login_action, bg="#27ae60").pack(pady=20, fill="x")

    # -----------------------------
    # Register Form
    # -----------------------------
    register_frame = tk.Frame(form_frame, bg="#ffffff")

    tk.Label(register_frame, text="Username", bg="#ffffff").pack(pady=5)
    reg_user = tk.Entry(register_frame, font=("Arial", 12))
    reg_user.pack(pady=5, fill="x")
    tk.Label(register_frame, text="Password", bg="#ffffff").pack(pady=5)
    reg_pass = tk.Entry(register_frame, show="*", font=("Arial", 12))
    reg_pass.pack(pady=5, fill="x")
    tk.Label(register_frame, text="Confirm Password", bg="#ffffff").pack(pady=5)
    reg_confirm = tk.Entry(register_frame, show="*", font=("Arial", 12))
    reg_confirm.pack(pady=5, fill="x")

    def register_action():
        if not reg_user.get() or not reg_pass.get():
            messagebox.showerror("Error", "Username and password required")
            return
        if reg_pass.get() != reg_confirm.get():
            messagebox.showerror("Error", "Passwords do not match")
            return
        if register_user(reg_user.get(), reg_pass.get()):
            messagebox.showinfo("Success", "User registered! Please login.")
            show_login()
        else:
            messagebox.showerror("Error", "Username already exists")

    styled_button(register_frame, "Register", register_action, bg="#27ae60").pack(pady=15, fill="x")

    # -----------------------------
    # Switch Tabs
    # -----------------------------
    def show_login():
        register_frame.pack_forget()
        login_frame.pack(fill="both", expand=True)
        login_btn.config(bg="#27ae60")
        register_btn.config(bg="#bdc3c7")

    def show_register():
        login_frame.pack_forget()
        register_frame.pack(fill="both", expand=True)
        register_btn.config(bg="#27ae60")
        login_btn.config(bg="#bdc3c7")

    login_btn.config(command=show_login)
    register_btn.config(command=show_register)

# -----------------------------
# Open App
# -----------------------------
def open_app():
    init_db()
    root = tk.Tk()
    root.title("Hotel Management System")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}+0+0")
    root.resizable(False, False)
    login_register_page(root)
    root.mainloop()

if __name__ == "__main__":
    open_app()
