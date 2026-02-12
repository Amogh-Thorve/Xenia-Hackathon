from app import app, db, User, BADGE_DEFINITIONS
import random
from datetime import datetime, timedelta

def randomize_users():
    with app.app_context():
        users = User.query.all()
        print(f"🎲 Randomizing stats for {len(users)} users...")
        
        all_badges = list(BADGE_DEFINITIONS.keys())
        
        for user in users:
            # 1. Random XP (50 to 2500)
            user.xp = random.randint(50, 2500)
            user.points = user.xp  # Keep points in sync if needed
            
            # 2. Random Badges (0 to 5 badges)
            num_badges = random.randint(0, 5)
            user_badges = random.sample(all_badges, num_badges)
            user.badges = ",".join(user_badges)
            
            # 3. Random Streak (0 to 30 days)
            user.streak_count = random.randint(0, 30)
            
            # 4. Random Last Active (0 to 14 days ago)
            days_ago = random.randint(0, 14)
            user.last_active = datetime.utcnow() - timedelta(days=days_ago)
            
            # 5. Random Participation Score
            user.participation_score = random.randint(0, 50)
            
            print(f"  - {user.username}: {user.xp} XP, {num_badges} Badges, Streak {user.streak_count}")
            
        db.session.commit()
        print("✅ User stats randomized successfully!")

if __name__ == "__main__":
    randomize_users()
