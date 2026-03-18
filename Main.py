import tkinter as tk
from tkinter import ttk, messagebox
from auth import AuthWindow
from tasks import TasksWindow
from database import Database
from config import APP_TITLE, WINDOW_SIZE

class TimeManagementApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.current_user_id = None
        self.db = Database()
        
        # Initialize database FIRST
        if self.db.connect():
            self.db.create_tables()  #  This was missing!
            print(" Application ready!")
        else:
            messagebox.showerror("Database Error", 
                "Cannot connect to database!\nCheck config.py settings.")
            return
        
        self.show_login()
    
    def show_login(self):
        """Show login window"""
        self.clear_window()
        AuthWindow(self.root, self.on_login_success)
    
    def on_login_success(self, user_id):
        """Callback when login is successful"""
        self.current_user_id = user_id
        self.show_tasks()
    
    def show_tasks(self):
        """Show main tasks window"""
        self.clear_window()
        TasksWindow(self.root, self.current_user_id, self.logout)
    
    def logout(self):
        """Logout and return to login screen"""
        self.current_user_id = None
        self.show_login()
    
    def clear_window(self):
        """Clear all widgets from root window"""
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.title(APP_TITLE)
    
    def run(self):
        """Start the application"""
        style = ttk.Style()
        style.theme_use('clam')
        self.root.eval('tk::PlaceWindow . center')
        self.root.mainloop()
    
    def __del__(self):
        """Cleanup on exit"""
        self.db.close()

if __name__ == "__main__":
    app = TimeManagementApp()
    app.run()