import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from datetime import datetime
import hashlib
import matplotlib
import os



matplotlib.use('TkAgg')

# ================= CONFIGURATION =================
# UPDATE THESE WITH YOUR MYSQL CREDENTIALS
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',          # Your MySQL username
    'password': "Skg@5476",  # Your MySQL password
    'database': 'time_management_db',
    'port': 3306,
    'charset':"utf8"
}

# ================= DATABASE FUNCTIONS =================
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Database Connection Error: {err}")
        return None

def hash_password(password):
    # Simple hashing for demonstration (Use bcrypt in production)
    return hashlib.sha256(password.encode()).hexdigest()

def init_database():
    """Creates tables and default admin user if they don't exist."""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 1. Create Tasks Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task_name VARCHAR(255) NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. Create Admins Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL
            )
        """)
        
        # 3. Insert Default Admin if not exists
        cursor.execute("SELECT * FROM admins WHERE username = 'admin'")
        if not cursor.fetchone():
            default_pass = hash_password("admin123")
            cursor.execute("INSERT INTO admins (username, password_hash) VALUES ('admin', %s)", (default_pass,))
            print("Default admin created: admin / admin123")
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Database Initialization Error: {e}")
        return False

def verify_login(username, password):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            hashed_pw = hash_password(password)
            sql = "SELECT * FROM admins WHERE username = %s AND password_hash = %s"
            cursor.execute(sql, (username, hashed_pw))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            return user is not None
        except Exception as e:
            print(f"Login Verification Error: {e}")
            return False
    return False

def log_task(task_name, start_time, end_time):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            sql = "INSERT INTO tasks (task_name, start_time, end_time) VALUES (%s, %s, %s)"
            val = (task_name, start_time, end_time)
            cursor.execute(sql, val)
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except mysql.connector.Error as err:
            print(f"Insert Error: {err}")
            return False
    return False

def fetch_data():
    conn = get_db_connection()
    if conn:
        try:
            query = "SELECT task_name, start_time, end_time FROM tasks ORDER BY created_at DESC"
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Fetch Error: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# ================= UI CLASSES =================

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Login")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        width = 400
        height = 300
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Time Management System", font=("Arial", 16, "bold")).pack(pady=20)
        
        ttk.Label(frame, text="Username:").pack(anchor="w")
        self.username_entry = ttk.Entry(frame, width=30)
        self.username_entry.pack(pady=5)

        ttk.Label(frame, text="Password:").pack(anchor="w")
        self.password_entry = ttk.Entry(frame, width=30, show="*")
        self.password_entry.pack(pady=5)

        ttk.Button(frame, text="Login", command=self.login_action).pack(pady=20)
        
        ttk.Label(frame, text="Default: admin / admin123", font=("Arial", 8), foreground="gray").pack(pady=5)

    def login_action(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter username and password.")
            return

        if verify_login(username, password):
            messagebox.showinfo("Success", "Login Successful!")
            self.clear_root()
            MainApp(self.root)
        else:
            messagebox.showerror("Error", "Invalid Username or Password.")

    def clear_root(self):
        """Clears all widgets from the root window to switch views."""
        for widget in self.root.winfo_children():
            widget.destroy()

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Time Management Dashboard")
        self.root.geometry("900x700")
        
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        # --- Frame 1: Input Section ---
        input_frame = ttk.LabelFrame(self.root, text="Log New Task", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Task Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.task_entry = ttk.Entry(input_frame, width=30)
        self.task_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Start Time (YYYY-MM-DD HH:MM):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.start_entry = ttk.Entry(input_frame, width=30)
        self.start_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="End Time (YYYY-MM-DD HH:MM):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.end_entry = ttk.Entry(input_frame, width=30)
        self.end_entry.grid(row=2, column=1, padx=5, pady=5)

        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Log Task", command=self.log_task_action).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Logout", command=self.logout_action).pack(side="right", padx=5)

        # --- Frame 2: History Table ---
        table_frame = ttk.LabelFrame(self.root, text="Task History", padding=10)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("ID", "Task", "Start", "End")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Task", text="Task Name")
        self.tree.heading("Start", text="Start Time")
        self.tree.heading("End", text="End Time")

        self.tree.column("ID", width=50)
        self.tree.column("Task", width=200)
        self.tree.column("Start", width=150)
        self.tree.column("End", width=150)

        self.tree.pack(fill="both", expand=True)

        # --- Frame 3: Analytics Section ---
        chart_frame = ttk.LabelFrame(self.root, text="Performance Analytics", padding=10)
        chart_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(chart_frame, text="Generate Performance Chart", command=self.show_chart).pack(pady=5)

    def log_task_action(self):
        task = self.task_entry.get()
        start = self.start_entry.get()
        end = self.end_entry.get()

        if not task or not start or not end:
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return

        try:
            # Validate datetime format
            datetime.strptime(start, "%Y-%m-%d %H:%M")
            datetime.strptime(end, "%Y-%m-%d %H:%M")
            
            if datetime.strptime(end, "%Y-%m-%d %H:%M") <= datetime.strptime(start, "%Y-%m-%d %H:%M"):
                messagebox.showerror("Time Error", "End time must be after start time.")
                return

            success = log_task(task, start, end)
            if success:
                messagebox.showinfo("Success", "Task Logged Successfully!")
                self.task_entry.delete(0, tk.END)
                self.start_entry.delete(0, tk.END)
                self.end_entry.delete(0, tk.END)
                self.refresh_table()
            else:
                messagebox.showerror("Error", "Failed to log task.")
        except ValueError:
            messagebox.showerror("Format Error", "Please use format: YYYY-MM-DD HH:MM")

    def refresh_table(self):
        # Clear existing data
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        df = fetch_data()
        if not df.empty:
            for _, row in df.iterrows():
                self.tree.insert("", tk.END, values=(row['id'], row['task_name'], row['start_time'], row['end_time']))

    def show_chart(self):
        df = fetch_data()
        if df.empty:
            messagebox.showinfo("Info", "No data available to plot.")
            return

        # Calculate Duration in Hours
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['end_time'] = pd.to_datetime(df['end_time'])
        df['duration_hours'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 3600

        # Aggregate by Task Name
        task_summary = df.groupby('task_name')['duration_hours'].sum().reset_index()

        # Create Matplotlib Figure
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(task_summary['task_name'], task_summary['duration_hours'], color='skyblue', edgecolor='black')
        ax.set_title('Total Hours Spent per Task')
        ax.set_xlabel('Task Name')
        ax.set_ylabel('Hours')
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()

        # Embed in Tkinter
        # Clear previous chart frame if exists
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame) and widget != self.root:
                # We only want to clear the chart area, but for simplicity in this demo
                # we will just create a new frame for the chart
                pass
        
        # Create a frame specifically for the chart
        chart_container = ttk.Frame(self.root)
        chart_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        canvas = FigureCanvasTkAgg(fig, master=chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Add Toolbar
        toolbar = NavigationToolbar2Tk(canvas, chart_container)
        toolbar.update()

    def logout_action(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.clear_root()
            LoginWindow(self.root)

    def clear_root(self):
        """Clears all widgets from the root window to switch views."""
        for widget in self.root.winfo_children():
            widget.destroy()

# ================= MAIN ENTRY POINT =================
if __name__ == "__main__":
    # Initialize Database (Tables + Default Admin)
    if not init_database():
        print("Failed to initialize database. Please check your MySQL connection.")
        exit(1)

    root = tk.Tk()
    # Start with Login Window
    LoginWindow(root)
    root.mainloop()