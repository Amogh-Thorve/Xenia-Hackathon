import random
from app import app, db, User, bcrypt
from datetime import datetime, timedelta

def seed_database():
    with app.app_context():
        print("🧹 Wiping the database...")
        db.drop_all()
        db.create_all()
        print("✅ Database tables recreated.")

        dummy_data = [
            ("Amit Shah", "amit@iitb.ac.in", "IIT Bombay", 450, "Club Leader,Hackathon Winner,First Club Joined"),
            ("Priya Sharma", "priya@bits.edu", "BITS Pilani", 320, "Club Leader,Streak 7,Newbie"),
            ("Rahul Gupta", "rahul@nitw.ac.in", "NIT Warangal", 280, "Streak 7,Social Butterfly,First Club Joined"),
            ("Sneha Reddy", "sneha@iiith.ac.in", "IIIT Hyderabad", 210, "First Club Joined,Newbie"),
            ("Karthik S.", "karthik@mit.edu", "MIT", 190, "Social Butterfly,Explorer"),
            ("Anjali Verma", "anjali@dtu.ac.in", "DTU", 150, "Newbie,First Club Joined"),
            ("Vikram Singh", "vikram@rvce.edu", "RVCE", 120, "Explorer"),
            ("Meera Nair", "meera@vit.ac.in", "VIT", 80, "Newbie"),
            ("Arjun Das", "arjun@srm.edu", "SRM", 50, "First Club Joined"),
            ("Ishita Paul", "ishita@ju.ac.in", "Jadavpur University", 30, "Newbie")
        ]

        print(f"🌱 Seeding {len(dummy_data)} dummy users...")
        
        # Fixed password for all dummy users for easy testing
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')

        for username, email, college, xp, badges in dummy_data:
            user = User(
                username=username,
                email=email,
                password=hashed_password,
                college=college,
                xp=xp,
                badges=badges,
                streak_count=random.randint(0, 15),
                last_active=datetime.utcnow() - timedelta(days=random.randint(0, 5))
            )
            db.session.add(user)

        db.session.commit()
        print("🎉 Seeding complete! 10 users added successfully.")

if __name__ == "__main__":
    seed_database()
