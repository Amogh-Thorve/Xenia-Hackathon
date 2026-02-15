from app import app, db, User

def make_admin(email):
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if user:
            user.is_admin = True
            db.session.commit()
            print(f"✅ User {user.username} ({email}) is now an Admin.")
        else:
            print(f"❌ User with email {email} not found.")

if __name__ == '__main__':
    # Default behavior: Make 'amit@example.com' (from setup_db) an admin
    make_admin('amit@example.com')
    
    # You can also uncomment this to ask for input:
    # email = input("Enter email to promote to Admin: ")
    # make_admin(email)
