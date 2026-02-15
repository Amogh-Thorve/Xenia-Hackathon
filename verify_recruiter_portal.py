from app import app, db, User
import json

def verify_recruiter():
    with app.app_context():
        # 1. Check if we can create a recruiter
        recruiter_email = "recruiter@test.com"
        rec_user = User.query.filter_by(email=recruiter_email).first()
        if not rec_user:
            rec_user = User(username="test_recruiter", email=recruiter_email, password="password", is_recruiter=True, company="Test Corp")
            db.session.add(rec_user)
            db.session.commit()
            print(f"Created recruiter: {rec_user.username}")
        else:
            print(f"Recruiter exists: {rec_user.username}")

        # 2. Check if recruiter can see students
        students = User.query.filter_by(is_recruiter=False, is_admin=False).limit(3).all()
        print(f"Found {len(students)} students for the talent pool.")

        # 3. Test shortlisting
        if students:
            target_student = students[0]
            print(f"Attempting to shortlist student: {target_student.username}")
            
            if target_student in rec_user.shortlisted:
                print("Student already shortlisted. Removing...")
                rec_user.shortlisted.remove(target_student)
            else:
                print("Adding student to shortlist...")
                rec_user.shortlisted.append(target_student)
            
            db.session.commit()
            
            # Verify shortlist persisted
            is_present = target_student in User.query.filter_by(email=recruiter_email).first().shortlisted
            print(f"Shortlist persistence check: {'SUCCESS' if is_present else 'REMOVED'}")

if __name__ == "__main__":
    verify_recruiter()
