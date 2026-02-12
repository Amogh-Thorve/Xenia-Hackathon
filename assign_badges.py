from app import app, db, User

def assign_badges():
    with app.app_context():
        # 1. Ishaan Joshi
        ishaan = User.query.filter_by(username="Ishaan Joshi").first()
        if ishaan:
            ishaan.badges = "Campus Legend,Code Ninja,Hackathon Winner"
            ishaan.xp = 3500
            print(f"Updated Ishaan: {ishaan.badges}")

        # 2. Krishna Das
        krishna = User.query.filter_by(username="Krishna Das").first()
        if krishna:
            krishna.badges = "Club Leader,Event Speaker,Visionary"
            krishna.xp = 2800
            print(f"Updated Krishna: {krishna.badges}")

        # 3. Aarav Patel
        aarav = User.query.filter_by(username="Aarav Patel").first()
        if aarav:
            aarav.badges = "Social Butterfly,Networker,Volunteer Star"
            aarav.xp = 2200
            print(f"Updated Aarav: {aarav.badges}")

        db.session.commit()
        print("✅ Badges assigned successfully!")

if __name__ == "__main__":
    assign_badges()
