from database import Database
from config import DB_CONFIG

db = Database()
if db.connect():
    db.create_tables()
    
    # Test user creation
    cursor = db.connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f" Total users: {user_count}")
    
    cursor.execute("SELECT COUNT(*) FROM tasks")
    task_count = cursor.fetchone()[0]
    print(f" Total tasks: {task_count}")
    
    cursor.close()
    db.close()
else:
    print(" Database connection failed!")