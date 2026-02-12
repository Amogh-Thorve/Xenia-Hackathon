import requests

# 1. Login
session = requests.Session()
login_url = 'http://127.0.0.1:5000/login'
profile_url = 'http://127.0.0.1:5000/profile'

# First get to get the CSRF token if needed (Flask-WTF usually needs it but this app doesn't seem to use it explicitly in forms)
response = session.get(login_url)

login_data = {
    'email': 'amit@example.com',
    'password': 'password'
}

print(f"Logging in to {login_url}...")
response = session.post(login_url, data=login_data)

if response.url == 'http://127.0.0.1:5000/':
    print("Login successful! Redirected to home.")
else:
    print(f"Login failed? Current URL: {response.url}")

# 2. Get Profile Page
print(f"Fetching profile from {profile_url}...")
response = session.get(profile_url)

if response.status_code == 200:
    content = response.text
    print("\n--- Profile Page Content Check ---")
    
    # Check for User Details
    if "Amit" in content:
        print("[PASS] Username 'Amit' found.")
    else:
        print("[FAIL] Username 'Amit' NOT found.")
        
    if "IIT Bombay" in content:
        print("[PASS] College 'IIT Bombay' found.")
    else:
        print("[FAIL] College 'IIT Bombay' NOT found.")

    # Check for Two-Column Layout Markers (Approximate)
    if "My Profile" in content:
         print("[PASS] 'My Profile' section found.")
    else:
         print("[FAIL] 'My Profile' section NOT found.")

    if "Clubs You'll Love" in content:
        print("[PASS] 'Clubs You'll Love' section found.")
    else:
        print("[FAIL] 'Clubs You'll Love' section NOT found.")

    # Check for Recommendations (Coding Club, AI Enthusiasts)
    if "Coding Club" in content:
        print("[PASS] Recommendation 'Coding Club' found.")
    else:
        print("[FAIL] Recommendation 'Coding Club' NOT found.")
        
    if "AI Enthusiasts" in content:
        print("[PASS] Recommendation 'AI Enthusiasts' found.")
    else:
        print("[FAIL] Recommendation 'AI Enthusiasts' NOT found.")

    # Check for Fonts
    if "Inter" in content and "Poppins" in content:
        print("[PASS] Fonts 'Inter' and 'Poppins' found in HTML.")
    else:
        print("[FAIL] Fonts NOT found.")
        
else:
    print(f"Failed to fetch profile page. Status Code: {response.status_code}")
