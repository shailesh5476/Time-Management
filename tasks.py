import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from database import Database
from datetime import datetime
from config import APP_TITLE

class TasksWindow:
    def __init__(self, root, user_id, logout_callback):
        self.root = root
        self.user_id = user_id
        self.logout_callback = logout_callback
        self.db = Database()
        self.db.connect()
        self.db.create_tables()
        
        self.setup_ui()
        self.load_tasks()
    
    def setup_ui(self):
        self.root.title(f"{APP_TITLE} - Tasks")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top frame with menu and add button
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Logout button
        ttk.Button(top_frame, text="Logout", 
                  command=self.logout_callback).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Add Task button
        ttk.Button(top_frame, text="➕ Add New Task", 
                  command=self.open_add_task_window).pack(side=tk.RIGHT, padx=5)
        
        # Filter frame
        filter_frame = ttk.Frame(top_frame)
        filter_frame.pack(side=tk.LEFT)
        
        ttk.Label(filter_frame, text="Filter by Status:").pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(filter_frame, textvariable=self.status_var,
                                   values=["All", "Pending", "In Progress", "Completed"],
                                   state="readonly", width=15)
        status_combo.pack(side=tk.LEFT, padx=(10, 20))
        status_combo.bind('<<ComboboxSelected>>', self.filter_tasks)
        
        # Treeview for tasks
        columns = ("ID", "Title", "Priority", "Status", "Due Date", "Created")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=20)
        
        # Define headings
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Priority", text="Priority")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Due Date", text="Due Date")
        self.tree.heading("Created", text="Created")
        
        # Sortable columns
        for col in columns:
            self.tree.heading(col, command=lambda c=col: self.sort_column(c, False))
        
        # Column widths
        self.tree.column("ID", width=60, anchor=tk.CENTER)
        self.tree.column("Title", width=350)
        self.tree.column("Priority", width=100, anchor=tk.CENTER)
        self.tree.column("Status", width=120, anchor=tk.CENTER)
        self.tree.column("Due Date", width=120, anchor=tk.CENTER)
        self.tree.column("Created", width=160)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind double-click for editing and right-click menu
        self.tree.bind("<Double-1>", self.edit_task)
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Status bar
        self.status_label = tk.StringVar()
        self.status_label.set(f"Total Tasks: 0 | Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_label, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def sort_column(self, col, reverse):
        """Sort treeview column"""
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        data.sort(reverse=reverse)
        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))
    
    def load_tasks(self, status_filter="All"):
        """Load tasks from database"""
        self.status_label.set("Loading tasks...")
        self.root.update()
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        cursor = self.db.connection.cursor(dictionary=True)
        query = """
        SELECT id, title, priority, status, due_date, created_at 
        FROM tasks 
        WHERE user_id = %s
        """
        params = [self.user_id]
        
        if status_filter != "All":
            query += " AND status = %s"
            params.append(status_filter)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        tasks = cursor.fetchall()
        
        for task in tasks:
            due_date = task['due_date'] or "No Date"
            created = task['created_at'].strftime("%d/%m/%Y %H:%M")
            
            # Color code based on priority
            tags = (task['priority'].lower(),)
            self.tree.insert("", tk.END, values=(
                task['id'],
                task['title'][:60] + "..." if len(task['title']) > 60 else task['title'],
                task['priority'],
                task['status'],
                due_date,
                created
            ), tags=tags)
        
        # Configure tags for priority colors
        self.tree.tag_configure('low', background='#f0f8f0')
        self.tree.tag_configure('medium', background='#fff8dc')
        self.tree.tag_configure('high', background='#ffe4e1')
        
        cursor.close()
        self.status_label.set(f"Total Tasks: {len(tasks)} | Ready")
    
    def filter_tasks(self, event=None):
        """Filter tasks by status"""
        status = self.status_var.get()
        self.load_tasks(status)
    
    def open_add_task_window(self):
        """Open window to add new task"""
        self.open_task_window()
    
    def open_task_window(self, task_data=None):
        """Open task window for add/edit"""
        self.task_window = tk.Toplevel(self.root)
        self.task_window.title("Edit Task" if task_data else "Add New Task")
        self.task_window.geometry("550x500")
        self.task_window.grab_set()
        self.task_window.transient(self.root)
        self.task_window.grab_set()
        
        self.create_task_form(task_data)
    
    def create_task_form(self, task_data=None):
        """Create task form for add/edit"""
        # Clear previous widgets
        for widget in self.task_window.winfo_children():
            widget.destroy()
        
        # Title
        title_label = tk.Label(self.task_window, text="Add New Task" if not task_data else "Edit Task", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Form frame
        form_frame = ttk.LabelFrame(self.task_window, text="Task Details", padding=20)
        form_frame.pack(pady=10, padx=30, fill=tk.BOTH, expand=True)
        
        # Title field
        ttk.Label(form_frame, text="Title *:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.title_entry = ttk.Entry(form_frame, font=("Arial", 11), width=50)
        self.title_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Description
        ttk.Label(form_frame, text="Description:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.desc_text = tk.Text(form_frame, height=4, width=50, font=("Arial", 10))
        self.desc_text.pack(fill=tk.X, pady=(0, 15))
        
        # Priority and Status frame
        priority_status_frame = ttk.Frame(form_frame)
        priority_status_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Priority
        ttk.Label(priority_status_frame, text="Priority:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.priority_var = tk.StringVar(value="Medium")
        priority_combo = ttk.Combobox(priority_status_frame, textvariable=self.priority_var,
                                     values=["Low", "Medium", "High"], state="readonly", width=10)
        priority_combo.pack(side=tk.LEFT, padx=(10, 30))
        
        # Status
        ttk.Label(priority_status_frame, text="Status:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.status_var_form = tk.StringVar(value="Pending")
        status_combo = ttk.Combobox(priority_status_frame, textvariable=self.status_var_form,
                                   values=["Pending", "In Progress", "Completed"], 
                                   state="readonly", width=12)
        status_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Due Date
        ttk.Label(form_frame, text="Due Date:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.due_date_entry = DateEntry(form_frame, width=12, background='darkblue',
                                       foreground='white', borderwidth=2, 
                                       date_pattern='yyyy-mm-dd')
        self.due_date_entry.pack(fill=tk.X, pady=(0, 25))
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="💾 Save Task", 
                  command=self.save_task).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="❌ Cancel", 
                  command=self.task_window.destroy).pack(side=tk.RIGHT)
        
        # Populate if editing
        if task_data:
            self.title_entry.insert(0, task_data.get('title', ''))
            self.desc_text.insert('1.0', task_data.get('description', ''))
            self.priority_var.set(task_data.get('priority', 'Medium'))
            self.status_var_form.set(task_data.get('status', 'Pending'))
            if task_data.get('due_date'):
                try:
                    self.due_date_entry.set_date(task_data['due_date'])
                except:
                    pass
        
        # Focus on title
        self.title_entry.focus()
    
    def save_task(self):
        """Save new or updated task"""
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showerror("Error", "Title is required!")
            self.title_entry.focus()
            return
        
        description = self.desc_text.get('1.0', tk.END).strip()
        priority = self.priority_var.get()
        status = self.status_var_form.get()
        due_date_str = self.due_date_entry.get()
        due_date = due_date_str if due_date_str != "__/__/____" else None
        
        cursor = self.db.connection.cursor()
        
        # Check if editing existing task
        selected_item = self.tree.selection()
        if selected_item:
            task_id = self.tree.item(selected_item)['values'][0]
            cursor.execute("""
                UPDATE tasks SET title=%s, description=%s, priority=%s, 
                status=%s, due_date=%s WHERE id=%s AND user_id=%s
            """, (title, description, priority, status, due_date, task_id, self.user_id))
            message = "Task updated successfully!"
        else:
            # New task
            cursor.execute("""
                INSERT INTO tasks (user_id, title, description, priority, status, due_date) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (self.user_id, title, description, priority, status, due_date))
            message = "Task created successfully!"
        
        self.db.connection.commit()
        cursor.close()
        
        self.task_window.destroy()
        self.load_tasks(self.status_var.get())
        messagebox.showinfo("Success", message)
    
    def edit_task(self, event):
        """Edit selected task"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a task to edit!")
            return
        
        task_id = self.tree.item(selected_item)['values'][0]
        
        cursor = self.db.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tasks WHERE id=%s AND user_id=%s", 
                      (task_id, self.user_id))
        task = cursor.fetchone()
        cursor.close()
        
        if task:
            self.open_task_window(task)
    
    def show_context_menu(self, event):
        """Show right-click context menu"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()