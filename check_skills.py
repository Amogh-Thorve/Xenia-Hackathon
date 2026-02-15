from app import app, db, User, Skill, UserSkill, ClubSkill

def check_skills():
    with app.app_context():
        skills = Skill.query.all()
        print(f"Total Skills in DB: {len(skills)}")
        for s in skills:
            print(f"- {s.name}")
        
        user_skills = UserSkill.query.all()
        print(f"\nTotal UserSkill entries: {len(user_skills)}")
        
        # Check a specific student (Aarav Patel from screenshot or first one)
        student = User.query.filter_by(is_recruiter=False, is_admin=False).first()
        if student:
            print(f"\nStats for {student.username}:")
            print(f"Manual Skills (UserSkill): {[us.skill.name for us in student.skills]}")
            print(f"Aggregated Skills (get_skill_stats): {student.get_skill_stats()}")

if __name__ == "__main__":
    check_skills()
