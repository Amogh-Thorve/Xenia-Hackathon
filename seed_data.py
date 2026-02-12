from app import app, db, Skill, Career, Club, ClubSkill
import json

def seed():
    with app.app_context():
        # 1. Skills
        skills_data = [
            "DSA", "Web Development", "Machine Learning", "Public Speaking", 
            "Leadership", "Event Management", "Creative Writing", "Music", 
            "Photography", "Teamwork", "Problem Solving", "Networking",
            "Python", "Java", "JavaScript", "C++", "Data Analysis",
            "UI/UX Design", "Graphic Design", "Video Editing", "Content Writing",
            "Marketing", "Sales", "Finance", "Accounting", "Project Management",
            "Research", "Critical Thinking", "Communication", "Time Management",
            "Adaptability", "Creativity", "Collaboration"
        ]
        
        print("Seeding Skills...")
        for s_name in skills_data:
            if not Skill.query.filter_by(name=s_name).first():
                db.session.add(Skill(name=s_name))
        db.session.commit()

        # 2. Careers
        careers_data = [
            {
                "name": "Software Engineer", 
                "skills": ["DSA", "Web Development", "Problem Solving", "Teamwork"]
            },
            {
                "name": "Data Scientist", 
                "skills": ["Machine Learning", "Problem Solving", "DSA"]
            },
            {
                "name": "Product Manager", 
                "skills": ["Leadership", "Public Speaking", "Event Management", "Teamwork"]
            },
            {
                "name": "Creative Director", 
                "skills": ["Creative Writing", "Music", "Photography", "Leadership"]
            }
        ]

        print("Seeding Careers...")
        for c in careers_data:
            if not Career.query.filter_by(name=c['name']).first():
                career = Career(name=c['name'], required_skills=json.dumps(c['skills']))
                db.session.add(career)
        db.session.commit()

        # 3. Assign Skills to existing Clubs (Heuristic based on name/category)
        print("Mapping Skills to Clubs...")
        clubs = Club.query.all()
        all_skills = {s.name: s.id for s in Skill.query.all()}
        
        for club in clubs:
            # Clear existing just in case
            ClubSkill.query.filter_by(club_id=club.id).delete()
            
            c_text = (club.name + " " + club.description + " " + (club.category or "")).lower()
            
            # Default skill: Teamwork
            if "Teamwork" in all_skills:
                db.session.add(ClubSkill(club_id=club.id, skill_id=all_skills["Teamwork"], points=5))

            if "coding" in c_text or "tech" in c_text or "developer" in c_text:
                if "DSA" in all_skills: db.session.add(ClubSkill(club_id=club.id, skill_id=all_skills["DSA"], points=20))
                if "Web Development" in all_skills: db.session.add(ClubSkill(club_id=club.id, skill_id=all_skills["Web Development"], points=15))
            
            if "music" in c_text or "art" in c_text or "dance" in c_text:
                if "Music" in all_skills: db.session.add(ClubSkill(club_id=club.id, skill_id=all_skills["Music"], points=20))
                if "Creative Writing" in all_skills: db.session.add(ClubSkill(club_id=club.id, skill_id=all_skills["Creative Writing"], points=10))

            if "debate" in c_text or "speaker" in c_text:
                if "Public Speaking" in all_skills: db.session.add(ClubSkill(club_id=club.id, skill_id=all_skills["Public Speaking"], points=25))
            
            if "manager" in c_text or "leader" in c_text:
                if "Leadership" in all_skills: db.session.add(ClubSkill(club_id=club.id, skill_id=all_skills["Leadership"], points=20))

        db.session.commit()
        print("Seeding Complete!")

if __name__ == '__main__':
    seed()
