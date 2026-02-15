from app import app, db, User, Skill, UserSkill, Club, UserClub

def seed_skills():
    with app.app_context():
        students = User.query.filter_by(is_recruiter=False, is_admin=False).all()
        skills = Skill.query.limit(5).all()
        
        if not skills:
            print("No skills found in DB. Seeding some...")
            for s_name in ["Coding", "Design", "Leadership", "Public Speaking", "Gaming"]:
                skill = Skill(name=s_name)
                db.session.add(skill)
            db.session.commit()
            skills = Skill.query.limit(5).all()

        for student in students:
            # Add 2-3 random skills
            import random
            selected_skills = random.sample(skills, random.randint(2, 3))
            for skill in selected_skills:
                # Check if already has it
                exists = UserSkill.query.filter_by(user_id=student.id, skill_id=skill.id).first()
                if not exists:
                    us = UserSkill(user_id=student.id, skill_id=skill.id, amount=random.randint(20, 80), is_manual=True)
                    db.session.add(us)
        
        db.session.commit()
        print(f"Seeded skills for {len(students)} students.")

if __name__ == "__main__":
    seed_skills()
