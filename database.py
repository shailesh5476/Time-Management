import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG
import hashlib

class Database:
    def __init__(self):
        self.connection = None
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                print("Successfully connected to MySQL database")
                cursor = self.connection.cursor()
                cursor.execute("SELECT DATABASE()")
                db_name = cursor.fetchone()
                print(f" Using database: {db_name[0]}")
                cursor.close()
                return True
        except Error as e:
            print(f" Error connecting to MySQL: {e}")
            return False
    
    def create_tables(self):
        """Create required tables if they don't exist"""
        if not self.connection or not self.connection.is_connected():
            return False
            
        cursor = self.connection.cursor()
        
        try:
            # Users table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB
            """)
            
            # Tasks table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                priority ENUM('Low', 'Medium', 'High') DEFAULT 'Medium',
                status ENUM('Pending', 'In Progress', 'Completed') DEFAULT 'Pending',
                due_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_status (user_id, status),
                INDEX idx_due_date (due_date)
            ) ENGINE=InnoDB
            """)
            
            self.connection.commit()
            print(" Tables created/verified successfully!")
            return True
            
        except Error as e:
            print(f" Error creating tables: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print(" Database connection closed")