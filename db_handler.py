import sqlite3
import os

class DBHandler:
    def __init__(self, db_path):
        """Initialize the connection settings."""
        self.db_path = db_path
        self.connection = None
        self.cursor = None

    def __enter__(self):
        """Opens the connection when entering a 'with' block."""
        try:
            if not os.path.exists(self.db_path):
                print(f"⚠️ Warning: Database file '{self.db_path}' not found.")
            
            self.connection = sqlite3.connect(self.db_path)
            # This allows accessing columns by name if needed
            self.connection.row_factory = sqlite3.Row 
            self.cursor = self.connection.cursor()
            return self
        except sqlite3.Error as e:
            print(f"❌ Connection Error: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes the connection when exiting a 'with' block."""
        if self.connection:
            self.connection.close()

    def get_schema(self):
        """Constructs a string representation of the database schema."""
        schema_str = []
        try:
            # Get all table names
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = self.cursor.fetchall()
            
            for table in tables:
                table_name = table['name']
                schema_str.append(f"Table: {table_name}")
                
                # Get columns for this table
                self.cursor.execute(f"PRAGMA table_info({table_name})")
                columns = self.cursor.fetchall()
                for col in columns:
                    schema_str.append(f"  - {col['name']} ({col['type']})")
                schema_str.append("") # Empty line between tables
                
            return "\n".join(schema_str)
        except Exception as e:
            return f"Error getting schema: {e}"

    def execute_query(self, sql_query, params=()):
        """
        Executes a SQL query and returns the results and column headers.
        """
        try:
            self.cursor.execute(sql_query, params)
            
            # If it's a SELECT query, fetch results
            if self.cursor.description:
                headers = [description[0] for description in self.cursor.description]
                results = self.cursor.fetchall()
                # Convert Row objects to dictionaries or tuples for easier printing
                clean_results = [tuple(row) for row in results]
                return headers, clean_results
            else:
                # For INSERT/UPDATE/DELETE, commit changes
                self.connection.commit()
                return [], []
                
        except sqlite3.Error as e:
            print(f"❌ SQL Error: {e}")
            return None, None