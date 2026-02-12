@echo off
cd /d "%~dp0"

echo ========================================
echo   CampusConnect - College Event Manager
echo ========================================
echo.

echo [0/5] Stopping existing Python processes...
taskkill /IM python.exe /F >nul 2>&1
echo Processes stopped.
echo.

echo [1/5] Checking Python environment...

if not exist venv (
    echo Virtual environment not found. Creating one...
    python -m venv venv
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate

echo [3/5] Installing/Updating dependencies...
echo This may take a moment...
pip install --quiet Flask Flask-SQLAlchemy Flask-Login Flask-Bcrypt textblob pillow fpdf

echo [4/5] Checking database...
if not exist instance\site.db (
    if not exist site.db (
        echo Database not found. Initializing...
        python setup_db.py
        echo Seeding initial data ^(skills, careers, clubs^)...
        python seed_data.py
    )
)

echo [5/5] Starting CampusConnect Server...
echo.
echo ========================================
echo   Server will start at http://127.0.0.1:5000
echo   Press Ctrl+C to stop the server
echo ========================================
echo.
python app.py
pause
