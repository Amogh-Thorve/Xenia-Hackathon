from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        # Add columns if they don't exist
        with db.engine.connect() as conn:
            # Check for is_recruiter
            try:
                conn.execute(text("ALTER TABLE user ADD COLUMN is_recruiter BOOLEAN DEFAULT 0"))
                conn.execute(text("ALTER TABLE user ADD COLUMN company VARCHAR(100)"))
                conn.commit()
                print("Added recruiter columns to user table.")
            except Exception as e:
                print(f"Recruiter columns might already exist: {e}")

            # Create association table manually if needed
            try:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS recruiter_shortlist (
                        recruiter_id INTEGER NOT NULL, 
                        student_id INTEGER NOT NULL, 
                        PRIMARY KEY (recruiter_id, student_id), 
                        FOREIGN KEY(recruiter_id) REFERENCES user (id), 
                        FOREIGN KEY(student_id) REFERENCES user (id)
                    )
                """))
                conn.commit()
                print("Created recruiter_shortlist table.")
            except Exception as e:
                print(f"Error creating association table: {e}")

if __name__ == "__main__":
    migrate()
