import tkinter as tk
from tkinter import ttk
from auth import AuthWindow
from tasks import TasksWindow

class TimeManagementApp:
    def __init__(self):
        self.root = tk.Tk()
        self.show_login()
    
    def show_login(self):
        """Show login window"""
        self.clear_window()
        AuthWindow(self.root, self.show_main_window)
    
    def show_main_window(self, user_id):
        """Show main tasks window after successful login"""
        self.clear_window()
        TasksWindow(self.root, user_id, self.logout)
    
    def logout(self):
        """Logout and return to login screen"""
        self.show_login()
    
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TimeManagementApp()
    app.run()