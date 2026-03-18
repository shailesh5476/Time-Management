import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class AuthWindow:
    def __init__(self, root, login_callback):
        self.root = root
        self.login_callback = login_callback
        self.db = Database()
        self.db.connect()
        self.db.create_tables()
        self.setup_ui()
    
    def setup_ui(self):
        self.root.title("Time Management System - Login")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        
        # Center the window
        self.root.eval('tk::PlaceWindow . center')
        
        # Title
        title_label = tk.Label(self.root, text="Time Management System", 
                              font=("Arial", 20, "bold"))
        title_label.pack(pady=30)
        
        # Notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Login frame
        self.login_frame = ttk.Frame(notebook)
        notebook.add(self.login_frame, text="Login")
        self.setup_login_form()
        
        # Register frame
        self.register_frame = ttk.Frame(notebook)
        notebook.add(self.register_frame, text="Create Account")
        self.setup_register_form()
    
    def setup_login_form(self):
        # Username
        ttk.Label(self.login_frame, text="Username:", font=("Arial", 12)).pack(pady=10)
        self.login_username = ttk.Entry(self.login_frame, font=("Arial", 12), width=30)
        self.login_username.pack(pady=5)
        self.login_username.focus()
        
        # Password
        ttk.Label(self.login_frame, text="Password:", font=("Arial", 12)).pack(pady=10)
        self.login_password = ttk.Entry(self.login_frame, show="*", font=("Arial", 12), width=30)
        self.login_password.pack(pady=5)
        
        # Login button
        ttk.Button(self.login_frame, text="Login", command=self.login,
                  style="Accent.TButton").pack(pady=30)
    
    def setup_register_form(self):
        # Username
        ttk.Label(self.register_frame, text="Username:", font=("Arial", 12)).pack(pady=10)
        self.reg_username = ttk.Entry(self.register_frame, font=("Arial", 12), width=30)
        self.reg_username.pack(pady=5)
        
        # Password
        ttk.Label(self.register_frame, text="Password:", font=("Arial", 12)).pack(pady=10)
        self.reg_password = ttk.Entry(self.register_frame, show="*", font=("Arial", 12), width=30)
        self.reg_password.pack(pady=5)
        
        # Confirm Password
        ttk.Label(self.register_frame, text="Confirm Password:", font=("Arial", 12)).pack(pady=10)
        self.reg_confirm_password = ttk.Entry(self.register_frame, show="*", font=("Arial", 12), width=30)
        self.reg_confirm_password.pack(pady=5)
        
        # Register button
        ttk.Button(self.register_frame, text="Create Account", command=self.register,
                  style="Accent.TButton").pack(pady=30)
    
    def login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password!")
            return
        
        cursor = self.db.connection.cursor()
        password_hash = self.db.hash_password(password)
        
        cursor.execute("SELECT id FROM users WHERE username=%s AND password_hash=%s", 
                      (username, password_hash))
        user = cursor.fetchone()
        
        if user:
            self.login_callback(user[0])  # Pass user_id to main window
        else:
            messagebox.showerror("Error", "Invalid username or password!")
        
        cursor.close()
    
    def register(self):
        username = self.reg_username.get().strip()
        password = self.reg_password.get().strip()
        confirm_password = self.reg_confirm_password.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill all fields!")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters!")
            return
        
        try:
            cursor = self.db.connection.cursor()
            password_hash = self.db.hash_password(password)
            
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                          (username, password_hash))
            self.db.connection.commit()
            messagebox.showinfo("Success", "Account created successfully! Please login.")
            
            # Switch to login tab
            notebook = self.root.nametowidget(".!notebook")
            notebook.select(0)
            
            # Clear register form
            self.reg_username.delete(0, tk.END)
            self.reg_password.delete(0, tk.END)
            self.reg_confirm_password.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", "Username already exists!")
        
        finally:
            cursor.close()