# database.py
# Step 2: Full Database Setup for Hotel Management System
# Author: You
# Description: Connects to SQLite, creates tables, and inserts sample data.

import sqlite3

# -----------------------------
# Step 1: Connect to SQLite DB
# -----------------------------
def connect():
    """
    Connect to SQLite database (hotel.db).
    Returns the connection object.
    """
    conn = sqlite3.connect("hotel.db")
    # Enable foreign key support in SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# -----------------------------
# Step 2: Create Tables
# -----------------------------
def create_tables(conn):
    """
    Create all required tables for Hotel Management System.
    """
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )""")

    # Customers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        nationality TEXT,
        gender TEXT,
        dob TEXT,
        address TEXT
    )""")

    # Rooms table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rooms (
        room_id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_no TEXT UNIQUE NOT NULL,
        room_type TEXT,
        bed TEXT,
        price INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'Available'
    )""")

    # Reservations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reservations (
        res_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        room_id INTEGER NOT NULL,
        check_in TEXT NOT NULL,
        check_out TEXT NOT NULL,
        total_days INTEGER,
        total_cost INTEGER,
        status TEXT DEFAULT 'Active',
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
        FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE CASCADE
    )""")

    # Staff table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS staff (
        staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        role TEXT,
        salary INTEGER
    )""")

    # Payments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        res_id INTEGER,
        amount INTEGER,
        payment_date TEXT,
        method TEXT,
        FOREIGN KEY (res_id) REFERENCES reservations(res_id) ON DELETE SET NULL
    )""")

    conn.commit()
    print("Tables created successfully.")

# -----------------------------
# Step 3: Insert Sample Data
# -----------------------------
def insert_sample_data(conn):
    """
    Insert demo/admin users, rooms, customers, reservation, and payment.
    """
    cursor = conn.cursor()

    # Sample Users
    cursor.execute("""
        INSERT OR IGNORE INTO users (username, password)
        VALUES 
        ('admin', 'admin123'),
        ('staff', 'staff123')
    """)

    # Sample Rooms
    cursor.execute("""
        INSERT OR IGNORE INTO rooms (room_no, room_type, bed, price, status)
        VALUES
        ('101', 'Single', 'Single', 3000, 'Available'),
        ('102', 'Double', 'Double', 4500, 'Available'),
        ('103', 'Deluxe', 'King', 7000, 'Available')
    """)

    # Sample Customers
    cursor.execute("""
        INSERT OR IGNORE INTO customers (name, phone, nationality, gender, dob, address)
        VALUES
        ('Ali Khan', '03123456789', 'Pakistani', 'Male', '1998-05-12', 'Lahore'),
        ('Sara Ahmed', '03051234567', 'Pakistani', 'Female', '2000-11-20', 'Karachi')
    """)

    # Sample Reservation
    cursor.execute("""
        INSERT OR IGNORE INTO reservations 
        (customer_id, room_id, check_in, check_out, total_days, total_cost, status)
        VALUES
        (1, 1, '2025-01-10', '2025-01-12', 2, 6000, 'Active')
    """)

    # Sample Payment
    cursor.execute("""
        INSERT OR IGNORE INTO payments (res_id, amount, payment_date, method)
        VALUES
        (1, 6000, '2025-01-10', 'Cash')
    """)

    conn.commit()
    print("Sample data inserted successfully.")

# -----------------------------
# Step 4: Initialize Database
# -----------------------------
if __name__ == "__main__":
    # Connect to DB
    conn = connect()

    # Create tables
    create_tables(conn)

    # Insert sample/demo data
    insert_sample_data(conn)

    # Close connection
    conn.close()
    print("Database setup complete. You can now connect to hotel.db from Python GUI.")
