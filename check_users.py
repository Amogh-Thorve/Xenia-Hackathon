from app import app, db, User, bcrypt
import sys

def check_user(email, password_attempt='password'):
    with app.app_context():
        print(f"Checking user: {email}")
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"❌ User with email '{email}' does NOT exist in the database.")
            return False
            
        print(f"✅ User found: ID={user.id}, Username={user.username}")
        print(f"   is_admin: {user.is_admin}")
        
        # Check password
        if bcrypt.check_password_hash(user.password, password_attempt):
            print(f"✅ Password '{password_attempt}' is CORRECT.")
        else:
            print(f"❌ Password '{password_attempt}' is INCORRECT.")
            # Optional: Start a new hash to see if it matches format
            # print(f"   Stored Hash: {user.password}")

        return True

def fix_amit():
    with app.app_context():
        email = 'amit@example.com'
        user = User.query.filter_by(email=email).first()
        
        if user:
            print(f"Updating password for {email} to 'password'...")
            hashed_pw = bcrypt.generate_password_hash('password').decode('utf-8')
            user.password = hashed_pw
            user.is_admin = True
            db.session.commit()
            print("✅ Password updated and Admin privileges granted.")
        else:
            print(f"Creating user {email}...")
            hashed_pw = bcrypt.generate_password_hash('password').decode('utf-8')
            user = User(
                username='Amit', 
                email=email, 
                password=hashed_pw,
                college='IIT Bombay',
                is_admin=True
            )
            db.session.add(user)
            db.session.commit()
            print("✅ User created with Admin privileges.")

if __name__ == '__main__':
    print("--- DIAGNOSTIC START ---")
    exists = check_user('amit@example.com')
    
    print("\n--- ATTEMPTING FIX ---")
    fix_amit()
    
    print("\n--- VERIFICATION ---")
    check_user('amit@example.com')
