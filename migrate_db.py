import sqlite3

def migrate():
    print("Checking database schema...")
    conn = sqlite3.connect('instance/site.db')
    cursor = conn.cursor()
    
    # helper to add column if it doesn't exist
    def add_column(table, column, definition):
        try:
            cursor.execute(f"SELECT {column} FROM {table} LIMIT 1")
        except sqlite3.OperationalError:
            print(f"Adding {column} column to {table} table...")
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
                conn.commit()
                print(f"{column} added successfully.")
            except Exception as e:
                print(f"Error adding {column}: {e}")

    # 1. user_skill
    add_column('user_skill', 'is_manual', 'BOOLEAN DEFAULT 0')

    # 2. message
    add_column('message', 'is_pinned', 'BOOLEAN DEFAULT 0')

    # 3. event
    add_column('event', 'registration_fee', 'FLOAT DEFAULT 0.0')
    add_column('event', 'upi_id', 'VARCHAR(100)')
    add_column('event', 'creator_id', 'INTEGER')

    # 4. event_registration
    add_column('event_registration', 'transaction_id', 'VARCHAR(100)')
    
    conn.close()

if __name__ == '__main__':
    migrate()
