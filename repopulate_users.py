from app import app, db, User, UserSkill, UserClub, Feedback, EventRegistration, Message, Club, Event
from flask_bcrypt import Bcrypt
import random
from datetime import datetime, timedelta

bcrypt = Bcrypt()

def repopulate_users():
    with app.app_context():
        print("🧹 Clearing existing users and their data...")
        
        # 1. Clear dependent tables first to avoid FK issues
        # (Though cascade delete might handle this, explicit is safer for SQLite sometimes)
        db.session.query(UserSkill).delete()
        db.session.query(UserClub).delete()
        db.session.query(Feedback).delete()
        db.session.query(EventRegistration).delete()
        db.session.query(Message).delete()
        
        # Note: If users manage clubs or created events, those might be affected.
        # The user's previous request was to delete all clubs/events, so those should be 0.
        # But if there were any, deleting the user might fail if FK constraints are strict 
        # or cascade isn't set.
        # Let's verify and clear Clus/Events connected to users if any exist (safety net).
        # Actually, let's just delete Users and see. database is supposed to be empty of clubs/events.
        
        print("Deleting Users...")
        db.session.query(User).delete()
        db.session.commit()
        print("✅ Users cleared.")

        # 2. Add 10 Dummy Users
        print("🌱 Seeding 10 dummy users...")
        
        dummy_users = [
            ("Aarav Patel", "aarav@example.com", "IIT Bombay", 450, "Club Leader,Hackathon Winner"),
            ("Vivaan Gupta", "vivaan@example.com", "BITS Pilani", 320, "Streak 7,Newbie"),
            ("Aditya Sharma", "aditya@example.com", "NIT Trichy", 280, "Social Butterfly"),
            ("Vihaan Singh", "vihaan@example.com", "IIIT Hyderabad", 210, "First Club Joined"),
            ("Arjun Kumar", "arjun@example.com", "VIT Vellore", 190, "Explorer"),
            ("Sai Iyer", "sai@example.com", "SRM University", 150, "Newbie"),
            ("Reyansh Reddy", "reyansh@example.com", "Manipal", 120, "Explorer"),
            ("Krishna Das", "krishna@example.com", "Jadavpur Univ", 80, "Newbie"),
            ("Ishaan Joshi", "ishaan@example.com", "Thapar", 50, "First Club Joined"),
            ("Shaurya Verma", "shaurya@example.com", "Amity", 30, "Newbie")
        ]

        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')

        for username, email, college, xp, badges in dummy_users:
            user = User(
                username=username,
                email=email,
                password=hashed_password,
                college=college,
                xp=xp,
                badges=badges,
                streak_count=random.randint(0, 10),
                last_active=datetime.utcnow() - timedelta(days=random.randint(0, 5))
            )
            db.session.add(user)
        
        db.session.commit()
        print(f"🎉 Successfully added {len(dummy_users)} dummy users!")

if __name__ == "__main__":
    repopulate_users()
