from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, make_response
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from textblob import TextBlob
from datetime import datetime, timedelta
import os, json, math, random
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/club_logos'
app.config['PROFILE_PICS_FOLDER'] = 'static/profile_pics'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ─────────────────────────────────────────────
#  BADGE / ACHIEVEMENT DEFINITIONS
# ─────────────────────────────────────────────
BADGE_DEFINITIONS = {
    'First Club Joined':   {'icon': '🏅', 'desc': 'Joined your first club',            'rarity': 'common',    'xp': 20},
    'Club Leader':         {'icon': '👑', 'desc': 'Created a club',                     'rarity': 'rare',      'xp': 50},
    'Event Speaker':       {'icon': '🎤', 'desc': 'Spoke at an event',                  'rarity': 'rare',      'xp': 40},
    'Hackathon Winner':    {'icon': '🧠', 'desc': 'Won a competition',                  'rarity': 'legendary', 'xp': 100},
    'Streak 7':            {'icon': '🔥', 'desc': '7-day activity streak',              'rarity': 'epic',      'xp': 60},
    'Top Contributor':     {'icon': '🌟', 'desc': 'Reached top 3 on leaderboard',       'rarity': 'legendary', 'xp': 80},
    'Social Butterfly':    {'icon': '🦋', 'desc': 'Joined 5+ events',                   'rarity': 'uncommon',  'xp': 30},
    'Newbie':              {'icon': '🌱', 'desc': 'Attended your first event',           'rarity': 'common',    'xp': 10},
    'Feedback Guru':       {'icon': '📝', 'desc': 'Submitted 5+ feedbacks',             'rarity': 'uncommon',  'xp': 25},
    'Explorer':            {'icon': '🧭', 'desc': 'Visited 10+ clubs',                  'rarity': 'uncommon',  'xp': 20},
}
ITEM_RARITY_HIERARCHY = {
    'legendary': 5,
    'epic': 4,
    'rare': 3,
    'uncommon': 2,
    'common': 1
}

LEVEL_THRESHOLDS = [0, 50, 120, 220, 350, 520, 740, 1020, 1360, 1800, 2500]
LEVEL_NAMES = [
    'Newcomer', 'Explorer', 'Enthusiast', 'Contributor', 'Activist',
    'Champion', 'Mentor', 'Visionary', 'Elite', 'Campus Legend', 'Mythic'
]

def get_level_info(xp):
    """Return (level_number, level_name, xp_in_level, xp_for_next_level, progress_pct)"""
    level = 0
    for i, threshold in enumerate(LEVEL_THRESHOLDS):
        if xp >= threshold:
            level = i
        else:
            break
    if level >= len(LEVEL_THRESHOLDS) - 1:
        level = len(LEVEL_THRESHOLDS) - 1
    
    current_threshold = LEVEL_THRESHOLDS[level]
    next_threshold = LEVEL_THRESHOLDS[level + 1] if level + 1 < len(LEVEL_THRESHOLDS) else LEVEL_THRESHOLDS[level] + 500
    xp_in_level = xp - current_threshold
    xp_needed = next_threshold - current_threshold
    progress = min(int((xp_in_level / xp_needed) * 100), 100) if xp_needed > 0 else 100
    
    return {
        'level': level + 1,
        'name': LEVEL_NAMES[min(level, len(LEVEL_NAMES) - 1)],
        'xp_current': xp,
        'xp_in_level': xp_in_level,
        'xp_for_next': xp_needed,
        'progress': progress,
        'next_level_xp': next_threshold,
    }

# ─────────────────────────────────────────────
#  MODELS
# ─────────────────────────────────────────────
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    college = db.Column(db.String(100), nullable=True)
    hobbies = db.Column(db.Text, nullable=True)
    points = db.Column(db.Integer, default=0)       # legacy
    xp = db.Column(db.Integer, default=0)
    badges = db.Column(db.Text, default="")

    streak_count = db.Column(db.Integer, default=0)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    participation_score = db.Column(db.Integer, default=0)
    is_admin = db.Column(db.Boolean, default=False)
    clubs_managed = db.relationship('Club', backref='manager', lazy=True)
    registrations = db.relationship('EventRegistration', backref='user', lazy=True)
    profile_image = db.Column(db.String(20), nullable=False, default='default.jpg')
    skills = db.relationship('UserSkill', backref='user', lazy=True)

    @property
    def level_info(self):
        return get_level_info(self.xp)

    @property
    def badge_list(self):
        if not self.badges:
            return []
        return [b.strip() for b in self.badges.split(',') if b.strip()]

    @property
    def top_badges(self):
        badges = self.badge_list
        if not badges:
            return []
            
        def badge_sort_key(badge_name):
            # 1. "Club Leader" is highest priority
            if badge_name == 'Club Leader':
                return (1, 0, 0)
            
            # 2. Rarity hierarchy
            badge_info = BADGE_DEFINITIONS.get(badge_name)
            if not badge_info:
                return (0, 0, 0)
                
            rarity_score = ITEM_RARITY_HIERARCHY.get(badge_info.get('rarity', 'common'), 0)
            xp_score = badge_info.get('xp', 0)
            
            return (0, rarity_score, xp_score)
            
        # Reverse=True to get highest priority first
        sorted_badges = sorted(badges, key=badge_sort_key, reverse=True)
        return sorted_badges[:3]

    def add_xp(self, amount):
        old_level = self.level_info['level']
        self.xp += amount
        self.points += amount
        new_level = self.level_info['level']
        return new_level > old_level  # True if leveled up

    def add_badge(self, badge_name):
        if badge_name not in self.badge_list:
            self.badges = (self.badges or "") + badge_name + ","
            if badge_name in BADGE_DEFINITIONS:
                self.add_xp(BADGE_DEFINITIONS[badge_name]['xp'])
            return True
        return False

    def update_streak(self):
        now = datetime.utcnow()
        if self.last_active:
            diff = (now.date() - self.last_active.date()).days
            if diff == 1:
                self.streak_count += 1
            elif diff > 1:
                self.streak_count = 1
            # same day = no change
        else:
            self.streak_count = 1
        self.last_active = now
        
        if self.streak_count >= 7:
            self.add_badge('Streak 7')

    def get_skill_stats(self):
        skill_counts = {}
        # Include manually added skills
        for us in UserSkill.query.filter_by(user_id=self.id).all():
            skill_counts[us.skill.name] = skill_counts.get(us.skill.name, 0) + us.amount
        # Include skills from clubs
        for uc in self.clubs_joined:
            if uc.status == 'approved':
                for cs in uc.club.skills:
                    skill_counts[cs.skill.name] = skill_counts.get(cs.skill.name, 0) + cs.points
        # Include skills from events
        for reg in self.registrations:
            if reg.event.event_date < datetime.utcnow(): 
                for cs in reg.event.club.skills:
                    skill_counts[cs.skill.name] = skill_counts.get(cs.skill.name, 0) + int(cs.points * 0.5)
        return skill_counts

    def get_career_alignment(self):
        user_skills = self.get_skill_stats()
        careers = Career.query.all()
        alignment = []
        for career in careers:
            required = json.loads(career.required_skills)
            if not required: continue
            matched = 0
            possible = len(required) * 50
            for req in required:
                matched += min(user_skills.get(req, 0), 50)
            pct = int((matched / possible) * 100) if possible > 0 else 0
            alignment.append({'name': career.name, 'match': pct, 'missing': [s for s in required if s not in user_skills or user_skills[s] < 10]})
        alignment.sort(key=lambda x: x['match'], reverse=True)
        return alignment


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    # e.g., "DSA", "Public Speaking", "Creativity"
    user_skills = db.relationship('UserSkill', backref='skill', lazy=True)
    club_skills = db.relationship('ClubSkill', backref='skill', lazy=True)

class ClubSkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    points = db.Column(db.Integer, default=10) # How much this club contributes to the skill

class UserSkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    amount = db.Column(db.Integer, default=0)
    is_manual = db.Column(db.Boolean, default=False)

class Career(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    required_skills = db.Column(db.Text, nullable=False) # JSON list of skill names e.g. ["DSA", "System Design"]


class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=True, default='General')
    image_file = db.Column(db.String(20), nullable=False, default='default.svg')
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    popularity_score = db.Column(db.Integer, default=0)
    members = db.relationship('UserClub', backref='club', lazy=True)
    events = db.relationship('Event', backref='club', lazy=True)
    feedback = db.relationship('Feedback', backref='club', lazy=True)
    skills = db.relationship('ClubSkill', backref='club', lazy=True)

    @property
    def member_count(self):
        return UserClub.query.filter_by(club_id=self.id, status='approved').count()


class UserClub(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    
    user_rel = db.relationship('User', backref=db.backref('clubs_joined', lazy=True))


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    event_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    difficulty = db.Column(db.String(20), default='Beginner')  # Beginner / Intermediate / Advanced
    xp_reward = db.Column(db.Integer, default=30)
    max_attendees = db.Column(db.Integer, default=100)
    registration_fee = db.Column(db.Float, default=0.0)
    upi_id = db.Column(db.String(100), nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Creator of the event
    registrations = db.relationship('EventRegistration', backref='event', lazy=True)
    creator = db.relationship('User', backref=db.backref('events_created', lazy=True))

    @property
    def attendee_count(self):
        return EventRegistration.query.filter_by(event_id=self.id).count()
    
    @property
    def is_upcoming(self):
        return self.event_date > datetime.utcnow()

    @property
    def time_remaining(self):
        delta = self.event_date - datetime.utcnow()
        if delta.total_seconds() <= 0:
            return "Event ended"
        days = delta.days
        hours = delta.seconds // 3600
        if days > 0:
            return f"{days}d {hours}h"
        return f"{hours}h {(delta.seconds % 3600) // 60}m"

    def is_user_registered(self, user):
        if not user or not user.is_authenticated:
            return False
        return EventRegistration.query.filter_by(user_id=user.id, event_id=self.id).first() is not None


class EventRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    transaction_id = db.Column(db.String(100), nullable=True)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    sentiment_score = db.Column(db.Float, nullable=False)
    sentiment_label = db.Column(db.String(20), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    is_pinned = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref='chat_messages', lazy=True)
    club = db.relationship('Club', backref='chat_messages', lazy=True)







@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─────────────────────────────────────────────
#  CONTEXT PROCESSOR – inject into all templates
# ─────────────────────────────────────────────
@app.context_processor
def inject_globals():
    stats = {
        'total_students': User.query.count(),
        'total_clubs': Club.query.count(),
        'total_events': Event.query.count(),
    }
    return dict(
        global_stats=stats,
        badge_defs=BADGE_DEFINITIONS,
        now=datetime.utcnow(),
    )


# ─────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────
@app.route('/')
def home():
    clubs = Club.query.all()
    events = Event.query.order_by(Event.event_date.asc()).all()
    top_users = User.query.order_by(User.xp.desc()).limit(5).all()
    return render_template('home.html', clubs=clubs, events=events, top_users=top_users)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        interests = request.form.getlist('interests')
        hobbies_str = ",".join(interests) if interests else ""
        user = User(username=username, email=email, password=hashed_password, xp=10, hobbies=hobbies_str)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! Welcome aboard! +10 XP 🎉', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            db.session.remove()
            flash(f'Error creating account: {e}', 'error')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            remember = True if request.form.get('remember-me') else False
            login_user(user, remember=remember)
            user.update_streak()
            db.session.commit()
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/club/new', methods=['GET', 'POST'])
@login_required
def create_club():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category', 'General')
        image_file = 'default.svg'
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_file = filename
        club = Club(name=name, description=description, category=category, image_file=image_file, manager=current_user)
        try:
            leveled = current_user.add_xp(50)
            current_user.add_badge('Club Leader')
            current_user.update_streak()
            db.session.add(club)
            db.session.commit()
            msg = 'Club created! +50 XP & "Club Leader" badge! 🎉'
            if leveled:
                msg += ' 🆙 Level Up!'
            flash(msg, 'success')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            db.session.remove()
            flash(f'Error creating club: {e}', 'error')
    return render_template('create_club.html')


@app.route('/event/new', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        club_id = request.form.get('club_id')
        event_date_str = request.form.get('event_date')
        difficulty = request.form.get('difficulty', 'Beginner')
        xp_reward = int(request.form.get('xp_reward', 30))
        registration_fee = float(request.form.get('registration_fee', 0.0))
        upi_id = request.form.get('upi_id')
        
        event_date = datetime.strptime(event_date_str, '%Y-%m-%dT%H:%M')
        event = Event(title=title, description=description, club_id=club_id,
                      event_date=event_date, difficulty=difficulty, xp_reward=xp_reward,
                      registration_fee=registration_fee, upi_id=upi_id, creator_id=current_user.id)
        try:
            current_user.add_xp(20)
            current_user.update_streak()
            db.session.add(event)
            db.session.commit()
            flash('Event created! +20 XP ✨', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            db.session.remove()
            flash(f'Error creating event: {e}', 'error')
    clubs = Club.query.all()
    return render_template('create_event.html', clubs=clubs)



@app.route('/club/<int:club_id>')
def club_details(club_id):
    club = Club.query.get_or_404(club_id)
    membership_status = None
    if current_user.is_authenticated:
        if club.manager_id == current_user.id:
            membership_status = 'manager'
        else:
            membership = UserClub.query.filter_by(user_id=current_user.id, club_id=club.id).first()
            if membership:
                membership_status = membership.status
    return render_template('club_details.html', club=club, membership_status=membership_status)


@app.route('/club/<int:club_id>/join')
@login_required
def join_club_action(club_id):
    club = Club.query.get_or_404(club_id)
    if club.manager_id == current_user.id:
        flash('You are the manager of this club!', 'info')
        return redirect(url_for('club_details', club_id=club.id))
    existing = UserClub.query.filter_by(user_id=current_user.id, club_id=club.id).first()
    if existing:
        flash('You are already a member or have a pending request.', 'info')
    else:
        # Check if first club BEFORE adding the new membership to session
        club_count = UserClub.query.filter_by(user_id=current_user.id, status='approved').count()
        
        membership = UserClub(user_id=current_user.id, club_id=club.id, status='approved')
        db.session.add(membership)
        
        if club_count == 0:
            current_user.add_badge('First Club Joined')
        
        leveled = current_user.add_xp(25)
        current_user.update_streak()
        club.popularity_score += 1
        db.session.commit()
        msg = f'Joined {club.name}! +25 XP 🎉'
        if leveled:
            msg += ' 🆙 Level Up!'
        flash(msg, 'success')
    return redirect(url_for('club_details', club_id=club.id))


@app.route('/club/<int:club_id>/leave')
@login_required
def leave_club_action(club_id):
    club = Club.query.get_or_404(club_id)
    if club.manager_id == current_user.id:
        flash('Managers cannot leave their own club. You must delete the club or transfer management.', 'error')
        return redirect(url_for('club_details', club_id=club.id))
    
    membership = UserClub.query.filter_by(user_id=current_user.id, club_id=club.id).first()
    if membership:
        db.session.delete(membership)
        club.popularity_score = max(0, club.popularity_score - 1)
        db.session.commit()
        flash(f'You have left {club.name}.', 'info')
    else:
        flash('You are not a member of this club.', 'warning')
        
    return redirect(url_for('home'))


@app.route('/club/<int:club_id>/delete', methods=['POST'])
@login_required
def delete_club(club_id):
    club = Club.query.get_or_404(club_id)
    
    # Security check: Only the manager can delete the club
    if club.manager_id != current_user.id:
        flash('Only the club manager can delete this club.', 'error')
        return redirect(url_for('club_details', club_id=club_id))
        
    # Cascade Deletion
    # 1. Delete Messages
    Message.query.filter_by(club_id=club.id).delete()
    
    # 2. Delete Event Registrations for all club events
    for event in club.events:
        EventRegistration.query.filter_by(event_id=event.id).delete()
        
    # 3. Delete Events
    Event.query.filter_by(club_id=club.id).delete()
    
    # 4. Delete Feedback
    Feedback.query.filter_by(club_id=club.id).delete()
    
    # 5. Delete ClubSkills
    ClubSkill.query.filter_by(club_id=club.id).delete()
    
    # 6. Delete Memberships
    UserClub.query.filter_by(club_id=club.id).delete()
    
    # 7. Delete the Club itself
    db.session.delete(club)
    
    db.session.commit()
    flash(f'Club "{club.name}" and all its associated data have been permanently deleted.', 'success')
    return redirect(url_for('home'))



@app.route('/club/<int:club_id>/chat')
@login_required
def club_chat(club_id):
    club = Club.query.get_or_404(club_id)
    membership_status = None
    if club.manager_id == current_user.id:
        membership_status = 'manager'
    else:
        membership = UserClub.query.filter_by(user_id=current_user.id, club_id=club.id).first()
        if membership:
            membership_status = membership.status
    
    # Only allow members or managers to access chat
    if membership_status not in ['approved', 'manager']:
        flash('You must be a member to access the club chat.', 'error')
        return redirect(url_for('club_details', club_id=club_id))
        
    return render_template('club_chat.html', club=club, membership_status=membership_status)


@app.route('/event/<int:event_id>/join', methods=['POST'])
@login_required
def join_event(event_id):
    event = Event.query.get_or_404(event_id)
    transaction_id = request.form.get('transaction_id')
    
    existing = EventRegistration.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if existing:
        flash('Already registered for this event!', 'info')
        return redirect(request.referrer or url_for('home'))
    
    reg_count = EventRegistration.query.filter_by(user_id=current_user.id).count()
    
    try:
        registration = EventRegistration(user_id=current_user.id, event_id=event.id, transaction_id=transaction_id)
        db.session.add(registration)
        
        xp = event.xp_reward
        leveled = current_user.add_xp(xp)
        current_user.participation_score += 1
        current_user.update_streak()
        
        # Badge checks
        if reg_count == 0:
            current_user.add_badge('Newbie')
        if reg_count + 1 >= 5:
            current_user.add_badge('Social Butterfly')
        
        db.session.commit()
        msg = f'Registered for {event.title}! +{xp} XP ⚡'
        if leveled:
            msg += ' 🆙 Level Up!'
        flash(msg, 'success')
    except Exception as e:
        db.session.rollback()
        db.session.remove()
        flash(f'Error joining event: {e}', 'error')
    return redirect(request.referrer or url_for('home'))


@app.route('/event/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Security check: Only the creator can delete the event
    if event.creator_id != current_user.id:
        flash('Only the creator of the event can delete it.', 'error')
        return redirect(request.referrer or url_for('home'))
        
    try:
        # Cascade Deletion: Delete Event Registrations for this event
        EventRegistration.query.filter_by(event_id=event_id).delete()
        
        # Delete the Event itself
        db.session.delete(event)
        db.session.commit()
        flash(f'Event "{event.title}" has been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        db.session.remove()
        flash(f'Error deleting event: {e}', 'error')
        
    return redirect(request.referrer or url_for('home'))



@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        if 'picture' in request.files:
            file = request.files['picture']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                # Ensure directory exists
                pic_path = os.path.join(app.root_path, 'static/profile_pics')
                if not os.path.exists(pic_path):
                    os.makedirs(pic_path)
                
                # Save
                file.save(os.path.join(pic_path, filename))
                current_user.profile_image = filename
                
        if 'add_skill' in request.form:
             try:
                 skill_names = request.form.getlist('skill_names')
                 added_count = 0
                 for skill_name in skill_names:
                     skill = Skill.query.filter_by(name=skill_name).first()
                     if skill:
                         existing = UserSkill.query.filter_by(user_id=current_user.id, skill_id=skill.id).first()
                         if not existing:
                             # Add skill
                             us = UserSkill(user_id=current_user.id, skill_id=skill.id, amount=10, is_manual=True)
                             db.session.add(us)
                             added_count += 1
                 
                 if added_count > 0:
                     leveled = current_user.add_xp(10 * added_count)
                     current_user.update_streak()
                     db.session.commit()
                     msg = f'{added_count} skills added! +{10 * added_count} XP 🧠'
                     if leveled: msg += ' 🆙 Level Up!'
                     flash(msg, 'success')
                 else:
                     flash('No new skills added (you might already have them).', 'info')
             except Exception as e:
                 db.session.rollback()
                 db.session.remove()
                 flash(f'Error adding skills: {e}', 'error')
             
             return redirect(url_for('profile'))

        if 'college' in request.form:
             current_user.college = request.form.get('college')
        if 'hobbies' in request.form:
             current_user.hobbies = request.form.get('hobbies')
             
        try:
            db.session.commit()
            flash('Profile updated! ✨', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            db.session.rollback()
            db.session.remove()
            flash(f'Error updating profile: {e}', 'error')

    # Track activity
    current_user.update_streak()
    
    # AI Recommendations
    recommended_clubs = []
    user_hobbies = []
    if current_user.hobbies:
        user_hobbies = [h.strip() for h in current_user.hobbies.split(',')]
    
    if user_hobbies:
        all_clubs = Club.query.all()
        
        # Exclude clubs the user already joined or manages
        joined_club_ids = {uc.club_id for uc in UserClub.query.filter_by(user_id=current_user.id).all()}
        managed_club_ids = {c.id for c in Club.query.filter_by(manager_id=current_user.id).all()}
        exclude_ids = joined_club_ids | managed_club_ids
        
        # Interest -> Keywords mapping
        interest_map = {
            'Coding': ['tech', 'code', 'develop', 'hack', 'programming', 'software'],
            'Design': ['art', 'design', 'creative', 'paint', 'ui', 'ux', 'graphic'],
            'Public Speaking': ['debate', 'speak', 'toastmaster', 'orator', 'speech'],
            'Leadership': ['lead', 'manage', 'council', 'entrepreneur', 'business'],
            'Music': ['music', 'band', 'sing', 'instrument', 'jam'],
            'Photography': ['photo', 'camera', 'media', 'film', 'lens'],
            'Gaming': ['game', 'esport', 'play station', 'pc'],
            'Social Service': ['social', 'service', 'ngo', 'help', 'volunteer', 'nss']
        }

        for club in all_clubs:
            if club.id in exclude_ids:
                continue
            match_score = 0
            # text search
            club_text = (club.name + " " + club.description + " " + (club.category or "")).lower()
            
            for hobby in user_hobbies:
                # Direct match
                if hobby.lower() in club_text:
                    match_score += 20
                
                # Semantic match via mapping (case-insensitive lookup)
                keywords = interest_map.get(hobby.strip().title(), [])
                for kw in keywords:
                    if kw in club_text:
                        match_score += 15
                        break # count once per hobby

            if match_score > 0:
                club.match_percentage = min(match_score + 40, 98)
                recommended_clubs.append(club)
    
    recommended_clubs.sort(key=lambda x: x.match_percentage, reverse=True)

    # Profile Completion
    completion_score = 0
    if current_user.username: completion_score += 25
    if current_user.email: completion_score += 25
    if current_user.college: completion_score += 25
    if current_user.hobbies: completion_score += 25

    # Streak heatmap data (last 90 days)
    heatmap_data = {}
    regs = EventRegistration.query.filter_by(user_id=current_user.id).all()
    for r in regs:
        day_key = r.registered_at.strftime('%Y-%m-%d')
        heatmap_data[day_key] = heatmap_data.get(day_key, 0) + 1

    # Retroactive badge checks — award any badges the user should have
    badge_dirty = False
    approved_clubs = UserClub.query.filter_by(user_id=current_user.id, status='approved').count()
    if approved_clubs >= 1 and 'First Club Joined' not in current_user.badge_list:
        current_user.add_badge('First Club Joined'); badge_dirty = True

    reg_count = EventRegistration.query.filter_by(user_id=current_user.id).count()
    if reg_count >= 1 and 'Newbie' not in current_user.badge_list:
        current_user.add_badge('Newbie'); badge_dirty = True
    if reg_count >= 5 and 'Social Butterfly' not in current_user.badge_list:
        current_user.add_badge('Social Butterfly'); badge_dirty = True

    fb_count = Feedback.query.filter_by(user_id=current_user.id).count()
    if fb_count >= 5 and 'Feedback Guru' not in current_user.badge_list:
        current_user.add_badge('Feedback Guru'); badge_dirty = True

    if current_user.streak_count >= 7 and 'Streak 7' not in current_user.badge_list:
        current_user.add_badge('Streak 7'); badge_dirty = True

    managed = Club.query.filter_by(manager_id=current_user.id).count()
    if managed >= 1 and 'Club Leader' not in current_user.badge_list:
        current_user.add_badge('Club Leader'); badge_dirty = True

    if badge_dirty:
        db.session.commit()

    # Achievements
    achievements = []
    for badge_name, info in BADGE_DEFINITIONS.items():
        earned = badge_name in current_user.badge_list
        # Calculate how many users earned it
        total_users = User.query.count()
        earned_count = User.query.filter(User.badges.contains(badge_name)).count()
        pct = int((earned_count / total_users) * 100) if total_users > 0 else 0
        achievements.append({
            'name': badge_name, 'icon': info['icon'], 'desc': info['desc'],
            'rarity': info['rarity'], 'earned': earned, 'earned_pct': pct
        })

    all_skills = Skill.query.all()
    return render_template('profile.html',
                           recommended_clubs=recommended_clubs,
                           user_hobbies=user_hobbies,
                           completion_score=completion_score,
                           heatmap_data=json.dumps(heatmap_data),
                           achievements=achievements,
                           all_skills=all_skills)

@app.route('/portfolio/download')
@login_required
def generate_portfolio():
    from fpdf import FPDF
    
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 15)
            self.cell(80)
            self.cell(30, 10, 'CampusConnect Impact Report', 0, 0, 'C')
            self.ln(20)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    pdf = PDF()
    pdf.add_page()
    
    # Title & User Info
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Student Profile: {current_user.username}", ln=True)
    pdf.cell(200, 10, txt=f"Email: {current_user.email}", ln=True)
    pdf.cell(200, 10, txt=f"College: {current_user.college or 'N/A'}", ln=True)
    pdf.cell(200, 10, txt=f"Level: {current_user.level_info['level']} ({current_user.level_info['name']})", ln=True)
    pdf.ln(10)

    # Skills
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Skill Profile", ln=True)
    pdf.set_font("Arial", size=12)
    skills = current_user.get_skill_stats()
    if skills:
        for s, pts in skills.items():
            pdf.cell(200, 8, txt=f"- {s}: {pts} Points", ln=True)
    else:
        pdf.cell(200, 8, txt="No skills detected yet.", ln=True)
    pdf.ln(10)

    # Badges
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Achievements & Badges", ln=True)
    pdf.set_font("Arial", size=12)
    badges = current_user.badge_list
    if badges:
        for b in badges:
            info = BADGE_DEFINITIONS.get(b, {})
            pdf.cell(200, 8, txt=f"- {info.get('icon','')} {b} ({info.get('rarity','Common')})", ln=True)
    else:
        pdf.cell(200, 8, txt="No badges earned yet.", ln=True)
    pdf.ln(10)

    # Club Participation
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Club Memberships", ln=True)
    pdf.set_font("Arial", size=12)
    for uc in current_user.clubs_joined:
        if uc.status == 'approved':
             pdf.cell(200, 8, txt=f"- {uc.club.name} ({uc.club.category})", ln=True)
    
    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={current_user.username}_Portfolio.pdf'
    return response




@app.route('/leaderboard')
def leaderboard():
    users = User.query.order_by(User.xp.desc()).limit(20).all()
    # Top clubs
    clubs = Club.query.order_by(Club.popularity_score.desc()).limit(10).all()
    return render_template('leaderboard.html', users=users, clubs=clubs)


@app.route('/dashboard')
@login_required
def dashboard():
    # Student dashboard
    my_clubs = UserClub.query.filter_by(user_id=current_user.id, status='approved').all()
    my_events = EventRegistration.query.filter_by(user_id=current_user.id).all()
    upcoming = Event.query.filter(Event.event_date > datetime.utcnow()).order_by(Event.event_date.asc()).limit(5).all()
    
    # Club admin data
    managed_clubs = Club.query.filter_by(manager_id=current_user.id).all()
    club_analytics = []
    for club in managed_clubs:
        total_members = club.member_count
        total_events = len(club.events)
        total_feedback = len(club.feedback)
        pos = sum(1 for f in club.feedback if f.sentiment_label == 'Positive')
        neg = sum(1 for f in club.feedback if f.sentiment_label == 'Negative')
        club_analytics.append({
            'club': club, 'members': total_members, 'events': total_events,
            'feedback': total_feedback, 'positive': pos, 'negative': neg,
        })

    return render_template('dashboard.html',
                           my_clubs=my_clubs,
                           my_events=my_events,
                           upcoming=upcoming,
                           club_analytics=club_analytics)


@app.route('/club/<int:club_id>/feedback', methods=['POST'])
@login_required
def submit_feedback(club_id):
    club = Club.query.get_or_404(club_id)
    content = request.form.get('content')
    if content:
        blob = TextBlob(content)
        sentiment_score = blob.sentiment.polarity
        if sentiment_score > 0.1:
            label = "Positive"
        elif sentiment_score < -0.1:
            label = "Negative"
        else:
            label = "Neutral"
        try:
            feedback = Feedback(content=content, sentiment_score=sentiment_score,
                                sentiment_label=label, club_id=club_id, user_id=current_user.id)
            db.session.add(feedback)
            
            leveled = current_user.add_xp(10)
            current_user.update_streak()
            
            # Badge: Feedback Guru
            fb_count = Feedback.query.filter_by(user_id=current_user.id).count()
            if fb_count >= 4:
                current_user.add_badge('Feedback Guru')
            
            db.session.commit()
            msg = 'Feedback submitted! +10 XP 📝'
            if leveled:
                msg += ' 🆙 Level Up!'
            flash(msg, 'success')
        except Exception as e:
            db.session.rollback()
            db.session.remove()
            flash(f'Error submitting feedback: {e}', 'error')
    return redirect(url_for('club_details', club_id=club.id))


# ─────────────────────────────────────────────
#  API ENDPOINTS (for JS animations / live data)
# ─────────────────────────────────────────────
@app.route('/api/stats')
def api_stats():
    return jsonify({
        'students': User.query.count(),
        'clubs': Club.query.count(),
        'events': Event.query.count(),
    })


@app.route('/api/club/<int:club_id>/messages', methods=['GET', 'POST'])
@login_required
def chat_messages(club_id):
    club = Club.query.get_or_404(club_id)
    membership = UserClub.query.filter_by(user_id=current_user.id, club_id=club_id).first()
    if club.manager_id != current_user.id and (not membership or membership.status != 'approved'):
        return jsonify({'error': 'Membership required to access chat'}), 403

    if request.method == 'POST':
        content = request.json.get('content')
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        message = Message(content=content, user_id=current_user.id, club_id=club_id)
        db.session.add(message)
        db.session.commit()
        return jsonify({
            'id': message.id,
            'content': message.content,
            'username': current_user.username,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'is_pinned': message.is_pinned
        })
    
    messages = Message.query.filter_by(club_id=club_id).order_by(Message.timestamp.asc()).all()
    return jsonify([{
        'id': m.id,
        'content': m.content,
        'username': m.user.username,
        'timestamp': m.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'is_pinned': m.is_pinned
    } for m in messages])



@app.route('/api/messages/<int:message_id>/pin', methods=['POST'])
@login_required
def toggle_pin(message_id):
    message = Message.query.get_or_404(message_id)
    # Check if user is manager of the club
    if message.club.manager_id != current_user.id:
        return jsonify({'error': 'Only club managers can pin messages'}), 403
    
    message.is_pinned = not message.is_pinned
    db.session.commit()
    return jsonify({'id': message.id, 'is_pinned': message.is_pinned})


@app.route('/api/club/<int:club_id>/pinned', methods=['GET'])
@login_required
def get_pinned_messages(club_id):
    club = Club.query.get_or_404(club_id)
    membership = UserClub.query.filter_by(user_id=current_user.id, club_id=club_id).first()
    if club.manager_id != current_user.id and (not membership or membership.status != 'approved'):
        return jsonify({'error': 'Membership required to view pinned messages'}), 403

    messages = Message.query.filter_by(club_id=club_id, is_pinned=True).order_by(Message.timestamp.desc()).all()
    return jsonify([{
        'id': m.id,
        'content': m.content,
        'username': m.user.username,
        'timestamp': m.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for m in messages])




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

