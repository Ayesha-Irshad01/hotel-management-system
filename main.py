# main.py
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import sqlite3
import os

DB = "hotel.db"

# -----------------------------
# Modern Card Creator
# -----------------------------
def create_modern_card(master, title, value, width=300, height=180, colors=("lightblue", "#3498db")):
    """
    Creates a modern card with rounded corners, shadow, and gradient colors.
    colors: tuple(light_color, dark_color)
    """
    # Create image with RGBA
    img = Image.new("RGBA", (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(img)

    # Shadow
    shadow_color = (0,0,0,60)
    offset = 6
    draw.rounded_rectangle([offset, offset, width, height], radius=20, fill=shadow_color)

    # Gradient card
    for i in range(height):
        r1, g1, b1 = master.winfo_rgb(colors[0])
        r2, g2, b2 = master.winfo_rgb(colors[1])
        r = int(r1/256 + (r2/256 - r1/256) * i / height)
        g = int(g1/256 + (g2/256 - g1/256) * i / height)
        b = int(b1/256 + (b2/256 - b1/256) * i / height)
        draw.line([(0, i), (width, i)], fill=(r,g,b,255))

    # Rounded corners mask
    mask = Image.new("L", (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0,0,width,height], radius=20, fill=255)
    img.putalpha(mask)

    tk_img = ImageTk.PhotoImage(img)
    canvas = tk.Canvas(master, width=width, height=height, bd=0, highlightthickness=0, bg=master['bg'])
    canvas.create_image(0, 0, anchor="nw", image=tk_img)
    canvas.image = tk_img

    # Add text
    canvas.create_text(width//2, 50, text=title, font=("Arial", 16, "bold"), fill="white")
    canvas.create_text(width//2, 120, text=value, font=("Arial", 26, "bold"), fill="white")

    return canvas

# -----------------------------
# Main Window
# -----------------------------
def open_main_window(root=None):
    if root is None:
        root = tk.Tk()
        root.title("Hotel Management System - Dashboard")
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.geometry(f"{screen_width}x{screen_height}+0+0")
        root.resizable(True, True)
    else:
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.geometry(f"{screen_width}x{screen_height}+0+0")

    # -----------------------------
    # Sidebar
    # -----------------------------
    sidebar = tk.Frame(root, bg="#2c3e50", width=250)
    sidebar.pack(side="left", fill="y")

    buttons = ["Dashboard", "Customers", "Rooms", "Reservations", "Staff", "Payments", "Logout"]

    main_area = tk.Frame(root, bg="#ecf0f1")
    main_area.pack(side="right", expand=True, fill="both")

    # -----------------------------
    # Change Page Function
    # -----------------------------
    def change_page(page_name):
        for widget in main_area.winfo_children():
            widget.destroy()

        if page_name == "Dashboard":
            # Background
            bg_path = "dashboard_bg.jpg"
            if os.path.exists(bg_path):
                img = Image.open(bg_path)
                main_area.update()
                main_width = main_area.winfo_width() or screen_width - 250
                main_height = main_area.winfo_height() or screen_height
                img = img.resize((main_width, main_height), Image.Resampling.LANCZOS)
                bg_img = ImageTk.PhotoImage(img)
                bg_label = tk.Label(main_area, image=bg_img)
                bg_label.image = bg_img
                bg_label.place(x=0, y=0, relwidth=1, relheight=1)

            # Database queries
            conn = sqlite3.connect(DB)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM customers")
            total_customers = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM rooms WHERE status='Available'")
            available_rooms = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM reservations WHERE status='Active'")
            active_reservations = cursor.fetchone()[0]

            cursor.execute("SELECT SUM(amount) FROM payments")
            total_payments = cursor.fetchone()[0] or 0

            conn.close()

            # Welcome Label
            tk.Label(main_area, text=" Welcome to Hotel Management System ",
                     font=("Arial", 32, "bold"), bg="#ffffff", fg="#2c3e50").place(relx=0.05, rely=0.02)

            # -----------------------------
            # Dashboard Cards
            # -----------------------------
            card_data = [
                ("Total Customers 👥", total_customers, ("#85c1e9", "#3498db")),
                ("Rooms 🛏️", available_rooms, ("#82e0aa", "#2ecc71")),
                ("Reservations 📅", active_reservations, ("#f5b041", "#e67e22")),
                ("Total Payments 💵", f"${total_payments}", ("#f1948a", "#e74c3c"))
            ]

            x_start = 0.03
            y_start = 0.15
            x_spacing = 0.245
            card_width = 300
            card_height = 180

            for i, (title, value, colors) in enumerate(card_data):
                card = create_modern_card(main_area, title, value, width=card_width, height=card_height, colors=colors)
                card.place(relx=x_start + i*x_spacing, rely=y_start)

        else:
            # Placeholder pages
            try:
                if page_name == "Customers":
                    from customers import customer_page
                    customer_page(main_area)
                elif page_name == "Rooms":
                    from rooms import rooms_page
                    rooms_page(main_area)
                elif page_name == "Reservations":
                    from reservations import reservations_page
                    reservations_page(main_area)
                elif page_name == "Staff":
                    from staff import staff_page
                    staff_page(main_area)
                elif page_name == "Payments":
                    from payments import payments_page
                    payments_page(main_area)
            except:
                tk.Label(main_area, text=f"{page_name} Module Placeholder",
                         bg="#ecf0f1", font=("Arial", 16)).pack(pady=20)

        if page_name == "Logout":
            root.destroy()
            import login
            login.open_app()

    # -----------------------------
    # Sidebar Buttons
    # -----------------------------
    for btn_text in buttons:
        b = tk.Button(sidebar, text=btn_text, fg="white", bg="#34495e",
                      font=("Arial", 14, "bold"), bd=0, relief="flat",
                      command=lambda txt=btn_text: change_page(txt))
        b.pack(fill="x", pady=10, padx=10)

    change_page("Dashboard")
    return root

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    open_main_window()
