from app import app, db, Club, Event, Feedback, UserClub, Message, EventRegistration, ClubSkill

def clean_database():
    with app.app_context():
        print("🧹 Cleaning ALL Club and Event data...")
        
        try:
            # Delete in order to respect potential foreign key constraints
            print("Deleting Event Registrations...")
            EventRegistration.query.delete()
            
            print("Deleting Feedbacks...")
            Feedback.query.delete()
            
            print("Deleting Chat Messages...")
            Message.query.delete()
            
            print("Deleting Club Skills...")
            ClubSkill.query.delete()
            
            print("Deleting Club Memberships...")
            UserClub.query.delete()
            
            print("Deleting Events...")
            Event.query.delete()
            
            print("Deleting Clubs...")
            Club.query.delete()
            
            db.session.commit()
            print("✨ Cleanup complete. All clubs and events removed.")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    clean_database()
