# College Event Management System

A comprehensive web application built with **Flask** for managing college clubs, events, and student engagement. 
Features gamification (XP, Badges, Leaderboards), social interactions (Chat, Feeds), and administrative tools for club managers.

## 🚀 Key Features

*   **User Authentication**: Secure login/signup with role-based access.
*   **Club Management**:
    *   Create and manage clubs (Approve/Reject members).
    *   Club-specific chat rooms.
    *   Post events and announcements.
*   **Event Management**:
    *   Create events with difficulty levels and XP rewards.
    *   Register for events and track participation.
    *   Calendar view (upcoming/past events).
*   **Gamification**:
    *   **XP System**: Earn XP by joining clubs, attending events, and adding skills.
    *   **Badges**: Unlock badges like "Club Leader", "Social Butterfly", "Streak 7".
    *   **Leaderboard**: Compete with other students for the top spot.
*   **Profile System**:
    *   Display skills, hobbies, and badges.
    *   Activity heatmap (GitHub-style).
    *   AI-powered Club Recommendations based on interests.
*   **Feedback System**: Submit feedback for clubs with sentiment analysis.

## 🛠️ Tech Stack

*   **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-Bcrypt
*   **Database**: SQLite (Development)
*   **Frontend**: HTML5, CSS3, JavaScript (Jinja2 Templates)
*   **Libraries**:
    *   `TextBlob` (Sentiment Analysis)
    *   `Pillow` (Image Processing)

## ⚙️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/CollegeEventManagement.git
    cd CollegeEventManagement
    ```

2.  **Create a Virtual Environment (Recommended)**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize Database**
    Run the setup script to create the database and populate it with sample data.
    ```bash
    python setup_db.py
    ```

5.  **Run the Application**
    ```bash
    python app.py
    ```
    The app will be available at `http://127.0.0.1:5000`.

## 🧪 Default Credentials (Sample Data)

The `setup_db.py` script creates several test users. You can use these to explore different roles:

*   **Amit** (Club Manager - Coding/AI): `amit@example.com` / `password`
*   **Priya** (Club Manager - Music/Photo): `priya@example.com` / `password`
*   **Rahul** (Student): `rahul@example.com` / `password`

## 🤝 Contributing

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/amazing-feature`).
3.  Commit your changes (`git commit -m 'Add some amazing feature'`).
4.  Push to the branch (`git push origin feature/amazing-feature`).
5.  Open a Pull Request.

