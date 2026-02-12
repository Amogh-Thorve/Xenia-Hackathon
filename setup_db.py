from app import app, db, User, Club, Event, UserClub, EventRegistration, Feedback, Skill, ClubSkill, UserSkill
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta

bcrypt_obj = Bcrypt(app)

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables...")
    db.create_all()

    # Create Test Users with XP
    pw = bcrypt_obj.generate_password_hash('password').decode('utf-8')

    u1 = User(username='Amit', email='amit@example.com', password=pw,
              college='IIT Bombay', hobbies='Coding, AI, Chess',
              xp=350, points=350, streak_count=5, badges='Club Leader,First Club Joined,Newbie,Social Butterfly,')
    u2 = User(username='Priya', email='priya@example.com', password=pw,
              college='BITS Pilani', hobbies='Music, Dance, Photography',
              xp=220, points=220, streak_count=3, badges='Club Leader,First Club Joined,Newbie,')
    u3 = User(username='Rahul', email='rahul@example.com', password=pw,
              college='NIT Trichy', hobbies='Sports, Badminton, Gaming',
              xp=180, points=180, streak_count=7, badges='First Club Joined,Newbie,Streak 7,')
    u4 = User(username='Sneha', email='sneha@example.com', password=pw,
              college='VIT', hobbies='AI, Machine Learning, Data Science',
              xp=150, points=150, streak_count=2, badges='First Club Joined,Newbie,')
    u5 = User(username='Karthik', email='karthik@example.com', password=pw,
              college='MIT', hobbies='Debate, Writing, Public Speaking',
              xp=120, points=120, streak_count=0, badges='Club Leader,Newbie,')

    db.session.add_all([u1, u2, u3, u4, u5])
    db.session.commit()
    print("Users created.")

    # Create Clubs
    c1 = Club(name='Coding Club', description='A place for competitive programming and hackathons.',
              category='Technology', manager_id=u1.id, popularity_score=12)
    c2 = Club(name='Badminton Club', description='Smash hard, play hard. Join us on the court every weekend!',
              category='Sports', manager_id=u3.id, popularity_score=8)
    c3 = Club(name='Music Society', description='Jamming sessions every Friday. Open mic nights monthly.',
              category='Music', manager_id=u2.id, popularity_score=10)
    c4 = Club(name='AI Enthusiasts', description='Exploring the future of Artificial Intelligence and ML.',
              category='Technology', manager_id=u1.id, popularity_score=15)
    c5 = Club(name='Debate Club', description='Voice your opinion. Monthly parliamentary debates.',
              category='Social', manager_id=u5.id, popularity_score=6)
    c6 = Club(name='Photography Club', description='Capture moments. Weekly photowalks and editing workshops.',
              category='Arts', manager_id=u2.id, popularity_score=9)

    db.session.add_all([c1, c2, c3, c4, c5, c6])
    db.session.commit()
    print("Clubs created.")

    # Create Skills
    skills_list = [
        "Python", "DSA", "Web Development", "AI/ML", "Data Science",       # Tech
        "Public Speaking", "Debate", "Leadership", "Communication",        # Soft Skills
        "Music Theory", "Instrumental", "Vocals",                          # Music
        "Photography", "Photo Editing", "Visual Arts",                     # Arts
        "Badminton", "Sportsmanship", "Teamwork"                           # Sports
    ]
    skill_objs = {}
    for s_name in skills_list:
        skill = Skill(name=s_name)
        db.session.add(skill)
        skill_objs[s_name] = skill
    db.session.commit()
    print("Skills created.")

    # Assign Skills to Clubs
    # Coding Club -> DSA, Python
    # AI Enthusiasts -> AI/ML, Data Science
    # Debate Club -> Public Speaking, Debate
    # Music Society -> Music Theory, Vocals
    # Badminton Club -> Badminton, Sportsmanship
    # Photography Club -> Photography, Photo Editing
    club_skills = [
        ClubSkill(club_id=c1.id, skill_id=skill_objs["DSA"].id, points=20),
        ClubSkill(club_id=c1.id, skill_id=skill_objs["Python"].id, points=15),
        ClubSkill(club_id=c4.id, skill_id=skill_objs["AI/ML"].id, points=25),
        ClubSkill(club_id=c4.id, skill_id=skill_objs["Data Science"].id, points=20),
        ClubSkill(club_id=c5.id, skill_id=skill_objs["Public Speaking"].id, points=20),
        ClubSkill(club_id=c5.id, skill_id=skill_objs["Debate"].id, points=25),
        ClubSkill(club_id=c3.id, skill_id=skill_objs["Music Theory"].id, points=15),
        ClubSkill(club_id=c3.id, skill_id=skill_objs["Vocals"].id, points=15),
        ClubSkill(club_id=c2.id, skill_id=skill_objs["Badminton"].id, points=25),
        ClubSkill(club_id=c2.id, skill_id=skill_objs["Sportsmanship"].id, points=10),
        ClubSkill(club_id=c6.id, skill_id=skill_objs["Photography"].id, points=20),
        ClubSkill(club_id=c6.id, skill_id=skill_objs["Photo Editing"].id, points=15),
    ]
    db.session.add_all(club_skills)
    db.session.commit()
    print("Club Skills assigned.")

    # Assign Skills to Users (InitialXP)
    # Amit -> Python, AI/ML
    # Priya -> Photography, Music
    user_skills = [
        UserSkill(user_id=u1.id, skill_id=skill_objs["Python"].id, amount=150),
        UserSkill(user_id=u1.id, skill_id=skill_objs["AI/ML"].id, amount=100),
        UserSkill(user_id=u2.id, skill_id=skill_objs["Photography"].id, amount=120),
        UserSkill(user_id=u2.id, skill_id=skill_objs["Vocals"].id, amount=80),
        UserSkill(user_id=u5.id, skill_id=skill_objs["Debate"].id, amount=90),
    ]
    db.session.add_all(user_skills)
    db.session.commit()
    print("User Skills assigned.")

    # Club memberships
    memberships = [
        UserClub(user_id=u2.id, club_id=c1.id, status='approved'),
        UserClub(user_id=u3.id, club_id=c1.id, status='approved'),
        UserClub(user_id=u4.id, club_id=c4.id, status='approved'),
        UserClub(user_id=u1.id, club_id=c3.id, status='approved'),
        UserClub(user_id=u5.id, club_id=c4.id, status='approved'),
        UserClub(user_id=u3.id, club_id=c2.id, status='approved'),
    ]
    db.session.add_all(memberships)
    db.session.commit()
    print("Memberships created.")

    # Create Events
    now = datetime.utcnow()
    events = [
        Event(title='Hackathon 2026', description='48-hour coding marathon with prizes!',
              club_id=c1.id, event_date=now + timedelta(days=7), difficulty='Advanced', xp_reward=100, creator_id=c1.manager_id),
        Event(title='AI Workshop', description='Hands-on intro to transformers and LLMs.',
              club_id=c4.id, event_date=now + timedelta(days=3), difficulty='Intermediate', xp_reward=50, creator_id=c4.manager_id),
        Event(title='Open Mic Night', description='Sing, rap, or recite poetry. All welcome!',
              club_id=c3.id, event_date=now + timedelta(days=5), difficulty='Beginner', xp_reward=30, creator_id=c3.manager_id),
        Event(title='Badminton Tournament', description='Singles and doubles. Bring your racquets!',
              club_id=c2.id, event_date=now + timedelta(days=10), difficulty='Intermediate', xp_reward=50, creator_id=c2.manager_id),
        Event(title='Debate Championship', description='Topic: "AI will replace all jobs in 10 years"',
              club_id=c5.id, event_date=now + timedelta(days=14), difficulty='Advanced', xp_reward=75, creator_id=c5.manager_id),
        Event(title='Photowalk Downtown', description='Explore the city through your lens.',
              club_id=c6.id, event_date=now + timedelta(days=2), difficulty='Beginner', xp_reward=25, creator_id=c6.manager_id),
    ]
    db.session.add_all(events)
    db.session.commit()
    print("Events created.")

    # Event registrations
    regs = [
        EventRegistration(user_id=u1.id, event_id=events[0].id, registered_at=now - timedelta(days=2)),
        EventRegistration(user_id=u2.id, event_id=events[0].id, registered_at=now - timedelta(days=1)),
        EventRegistration(user_id=u3.id, event_id=events[1].id, registered_at=now - timedelta(days=1)),
        EventRegistration(user_id=u4.id, event_id=events[1].id, registered_at=now - timedelta(days=3)),
        EventRegistration(user_id=u1.id, event_id=events[2].id, registered_at=now - timedelta(days=5)),
    ]
    db.session.add_all(regs)
    db.session.commit()
    print("Registrations created.")

    # Feedback
    feedbacks = [
        Feedback(content='Amazing coding sessions!', sentiment_score=0.8, sentiment_label='Positive',
                 club_id=c1.id, user_id=u2.id),
        Feedback(content='Could improve the timing of events.', sentiment_score=-0.2, sentiment_label='Negative',
                 club_id=c1.id, user_id=u3.id),
        Feedback(content='Love the music nights!', sentiment_score=0.9, sentiment_label='Positive',
                 club_id=c3.id, user_id=u1.id),
    ]
    db.session.add_all(feedbacks)
    db.session.commit()
    print("Feedback created.")

    print("\n✅ Database setup complete with sample data!")
    print("   5 Users | 6 Clubs | 6 Events | 6 Memberships | 5 Registrations | 3 Feedbacks")
    print("\n   Login: amit@example.com / password")
    print("   Login: priya@example.com / password")
