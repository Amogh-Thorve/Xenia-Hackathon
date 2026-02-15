from app import app, db, User, Club, Event, UserClub, EventRegistration, Feedback, Skill, ClubSkill, UserSkill
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta

bcrypt_obj = Bcrypt(app)

with app.app_context():
    # print("Dropping all tables...")
    # db.drop_all()
    print("Checking/Creating all tables...")
    db.create_all()

    # Create Test Users with XP (Only if they don't exist)
    pw = bcrypt_obj.generate_password_hash('password').decode('utf-8')

    def get_or_create_user(username, email, **kwargs):
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(username=username, email=email, password=pw, **kwargs)
            db.session.add(user)
            db.session.commit()
            print(f"User {username} created.")
        return user

    u1 = get_or_create_user('Amit', 'amit@example.com', college='IIT Bombay', 
                            hobbies='Coding, AI, Chess', xp=350, points=350, 
                            streak_count=5, badges='Club Leader,First Club Joined,Newbie,Social Butterfly,', is_admin=True)
    u2 = get_or_create_user('Priya', 'priya@example.com', college='BITS Pilani', 
                            hobbies='Music, Dance, Photography', xp=220, points=220, 
                            streak_count=3, badges='Club Leader,First Club Joined,Newbie,')
    u3 = get_or_create_user('Rahul', 'rahul@example.com', college='NIT Trichy', 
                            hobbies='Sports, Badminton, Gaming', xp=180, points=180, 
                            streak_count=7, badges='First Club Joined,Newbie,Streak 7,')
    u4 = get_or_create_user('Sneha', 'sneha@example.com', college='VIT', 
                            hobbies='AI, Machine Learning, Data Science', xp=150, points=150, 
                            streak_count=2, badges='First Club Joined,Newbie,')
    u5 = get_or_create_user('Karthik', 'karthik@example.com', college='MIT', 
                            hobbies='Debate, Writing, Public Speaking', xp=120, points=120, 
                            streak_count=0, badges='Club Leader,Newbie,')

    # Create Clubs (Only if they don't exist)
    def get_or_create_club(name, **kwargs):
        club = Club.query.filter_by(name=name).first()
        if not club:
            club = Club(name=name, **kwargs)
            db.session.add(club)
            db.session.commit()
            print(f"Club {name} created.")
        return club

    c1 = get_or_create_club('Coding Club', description='A place for competitive programming and hackathons.',
                            category='Technology', manager_id=u1.id, popularity_score=12)
    c2 = get_or_create_club('Badminton Club', description='Smash hard, play hard. Join us on the court every weekend!',
                            category='Sports', manager_id=u3.id, popularity_score=8)
    c3 = get_or_create_club('Music Society', description='Jamming sessions every Friday. Open mic nights monthly.',
                            category='Music', manager_id=u2.id, popularity_score=10)
    c4 = get_or_create_club('AI Enthusiasts', description='Exploring the future of Artificial Intelligence and ML.',
                            category='Technology', manager_id=u1.id, popularity_score=15)
    c5 = get_or_create_club('Debate Club', description='Voice your opinion. Monthly parliamentary debates.',
                            category='Social', manager_id=u5.id, popularity_score=6)
    c6 = get_or_create_club('Photography Club', description='Capture moments. Weekly photowalks and editing workshops.',
                            category='Arts', manager_id=u2.id, popularity_score=9)

    # Create Skills (Only if they don't exist)
    skills_list = [
        "Python", "DSA", "Web Development", "AI/ML", "Data Science",
        "Public Speaking", "Debate", "Leadership", "Communication",
        "Music Theory", "Instrumental", "Vocals",
        "Photography", "Photo Editing", "Visual Arts",
        "Badminton", "Sportsmanship", "Teamwork"
    ]
    skill_objs = {}
    for s_name in skills_list:
        skill = Skill.query.filter_by(name=s_name).first()
        if not skill:
            skill = Skill(name=s_name)
            db.session.add(skill)
            db.session.commit()
        skill_objs[s_name] = skill
    print("Skills check complete.")

    # Assign Skills to Clubs (If not already assigned)
    def assign_club_skill(club_id, skill_id, points):
        exists = ClubSkill.query.filter_by(club_id=club_id, skill_id=skill_id).first()
        if not exists:
            db.session.add(ClubSkill(club_id=club_id, skill_id=skill_id, points=points))

    assign_club_skill(c1.id, skill_objs["DSA"].id, 20)
    assign_club_skill(c1.id, skill_objs["Python"].id, 15)
    assign_club_skill(c4.id, skill_objs["AI/ML"].id, 25)
    assign_club_skill(c4.id, skill_objs["Data Science"].id, 20)
    assign_club_skill(c5.id, skill_objs["Public Speaking"].id, 20)
    assign_club_skill(c5.id, skill_objs["Debate"].id, 25)
    assign_club_skill(c3.id, skill_objs["Music Theory"].id, 15)
    assign_club_skill(c3.id, skill_objs["Vocals"].id, 15)
    assign_club_skill(c2.id, skill_objs["Badminton"].id, 25)
    assign_club_skill(c2.id, skill_objs["Sportsmanship"].id, 10)
    assign_club_skill(c6.id, skill_objs["Photography"].id, 20)
    assign_club_skill(c6.id, skill_objs["Photo Editing"].id, 15)
    db.session.commit()

    # Assign Skills to Users (InitialXP - If not exists)
    def assign_user_skill(user_id, skill_id, amount):
        exists = UserSkill.query.filter_by(user_id=user_id, skill_id=skill_id).first()
        if not exists:
            db.session.add(UserSkill(user_id=user_id, skill_id=skill_id, amount=amount))

    assign_user_skill(u1.id, skill_objs["Python"].id, 150)
    assign_user_skill(u1.id, skill_objs["AI/ML"].id, 100)
    assign_user_skill(u2.id, skill_objs["Photography"].id, 120)
    assign_user_skill(u2.id, skill_objs["Vocals"].id, 80)
    assign_user_skill(u5.id, skill_objs["Debate"].id, 90)
    db.session.commit()

    # Club memberships (If not exists)
    def join_club_if_not(user_id, club_id):
        exists = UserClub.query.filter_by(user_id=user_id, club_id=club_id).first()
        if not exists:
            db.session.add(UserClub(user_id=user_id, club_id=club_id, status='approved'))

    join_club_if_not(u2.id, c1.id)
    join_club_if_not(u3.id, c1.id)
    join_club_if_not(u4.id, c4.id)
    join_club_if_not(u1.id, c3.id)
    join_club_if_not(u5.id, c4.id)
    join_club_if_not(u3.id, c2.id)
    db.session.commit()

    # Create Events (Only if they don't exist by title)
    now = datetime.utcnow()
    def get_or_create_event(title, **kwargs):
        event = Event.query.filter_by(title=title).first()
        if not event:
            event = Event(title=title, **kwargs)
            db.session.add(event)
            db.session.commit()
            print(f"Event {title} created.")
        return event

    e1 = get_or_create_event('Hackathon 2026', description='48-hour coding marathon with prizes!',
                             club_id=c1.id, event_date=now + timedelta(days=7), difficulty='Advanced', xp_reward=100, creator_id=c1.manager_id)
    e2 = get_or_create_event('AI Workshop', description='Hands-on intro to transformers and LLMs.',
                             club_id=c4.id, event_date=now + timedelta(days=3), difficulty='Intermediate', xp_reward=50, creator_id=c4.manager_id)
    e3 = get_or_create_event('Open Mic Night', description='Sing, rap, or recite poetry. All welcome!',
                             club_id=c3.id, event_date=now + timedelta(days=5), difficulty='Beginner', xp_reward=30, creator_id=c3.manager_id)
    e4 = get_or_create_event('Badminton Tournament', description='Singles and doubles. Bring your racquets!',
                             club_id=c2.id, event_date=now + timedelta(days=10), difficulty='Intermediate', xp_reward=50, creator_id=c2.manager_id)
    e5 = get_or_create_event('Debate Championship', description='Topic: "AI will replace all jobs in 10 years"',
                             club_id=c5.id, event_date=now + timedelta(days=14), difficulty='Advanced', xp_reward=75, creator_id=c5.manager_id)
    e6 = get_or_create_event('Photowalk Downtown', description='Explore the city through your lens.',
                             club_id=c6.id, event_date=now + timedelta(days=2), difficulty='Beginner', xp_reward=25, creator_id=c6.manager_id)

    # Event registrations (If not exists)
    def register_event_if_not(user_id, event_id, registered_at):
        exists = EventRegistration.query.filter_by(user_id=user_id, event_id=event_id).first()
        if not exists:
            db.session.add(EventRegistration(user_id=user_id, event_id=event_id, registered_at=registered_at))

    register_event_if_not(u1.id, e1.id, now - timedelta(days=2))
    register_event_if_not(u2.id, e1.id, now - timedelta(days=1))
    register_event_if_not(u3.id, e2.id, now - timedelta(days=1))
    register_event_if_not(u4.id, e2.id, now - timedelta(days=3))
    register_event_if_not(u1.id, e3.id, now - timedelta(days=5))
    db.session.commit()

    # Feedback (If not exists)
    def add_feedback_if_not(content, sentiment_score, sentiment_label, club_id, user_id):
        exists = Feedback.query.filter_by(content=content, user_id=user_id, club_id=club_id).first()
        if not exists:
            db.session.add(Feedback(content=content, sentiment_score=sentiment_score,
                                    sentiment_label=sentiment_label, club_id=club_id, user_id=user_id))

    add_feedback_if_not('Amazing coding sessions!', 0.8, 'Positive', c1.id, u2.id)
    add_feedback_if_not('Could improve the timing of events.', -0.2, 'Negative', c1.id, u3.id)
    add_feedback_if_not('Love the music nights!', 0.9, 'Positive', c3.id, u1.id)
    db.session.commit()
    print("Feedback created.")

    print("\n✅ Database check complete!")
    print("   Existing data preserved. New tables created if missing.")
    print("   5 Users | 6 Clubs | 6 Events | 6 Memberships | 5 Registrations | 3 Feedbacks")
    print("\n   Login: amit@example.com / password")
    print("   Login: priya@example.com / password")
