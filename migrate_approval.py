import sqlite3

def migrate():
    print("Migrating database for Approval System...")
    conn = sqlite3.connect('instance/site.db')
    cursor = conn.cursor()

    # defined default as 'approved' for EXISTING records so they don't break
    # validation for NEW records will be handled in app.py logic (defaulting to 'pending')
    
    # helper to add column
    def add_column_if_not_exists(table, column, definition):
        try:
            cursor.execute(f"SELECT {column} FROM {table} LIMIT 1")
            print(f"Column '{column}' already exists in table '{table}'.")
        except sqlite3.OperationalError:
            print(f"Adding '{column}' column to '{table}' table...")
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
                conn.commit()
                # Update existing records to 'approved'
                cursor.execute(f"UPDATE {table} SET {column} = 'approved'")
                conn.commit()
                print(f"'{column}' added and defaults set to 'approved'.")
            except Exception as e:
                print(f"Error adding '{column}' to '{table}': {e}")

    # 1. Add status to Club
    add_column_if_not_exists('club', 'status', "VARCHAR(20) DEFAULT 'pending'")

    # 2. Add status to Event
    add_column_if_not_exists('event', 'status', "VARCHAR(20) DEFAULT 'pending'")

    # 3. Add is_admin to User
    add_column_if_not_exists('user', 'is_admin', "BOOLEAN DEFAULT 0")

    # 4. Make Amit an Admin
    try:
        cursor.execute("UPDATE user SET is_admin = 1 WHERE email = 'amit@example.com'")
        if cursor.rowcount > 0:
            print("✅ User 'amit@example.com' is now an Admin.")
        else:
            print("⚠️ User 'amit@example.com' not found. Admin not set.")
        conn.commit()
    except Exception as e:
        print(f"Error setting admin: {e}")
    
    conn.close()
    print("Migration complete.")

if __name__ == '__main__':
    migrate()
