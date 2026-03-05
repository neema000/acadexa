"""
Quick setup script to configure course registration data
"""
from backend.database import SessionLocal
from backend.models import Student, Course
from sqlalchemy import text

db = SessionLocal()

print("🔧 Setting up course registration data...\n")

# 1. Set all students to semester 1 (or their appropriate semester)
students = db.query(Student).all()
print(f"📚 Found {len(students)} students")
for student in students:
    if student.current_semester is None:
        student.current_semester = 1
        print(f"  ✓ Set {student.name} to Semester 1")
db.commit()

# 2. Display courses and ask to set semesters
courses = db.query(Course).all()
print(f"\n📖 Found {len(courses)} courses:")
for course in courses:
    print(f"  - ID {course.id}: {course.title} (Code: {course.code}) - Current Semester: {course.semester or 'Not Set'}")

print("\n" + "="*60)
print("IMPORTANT: Assign semesters to courses!")
print("="*60)
print("\nOption 1: Use Admin UI (Recommended)")
print("  1. Login as admin")
print("  2. Go to Courses page")
print("  3. Edit each course and select a semester (1-8)")
print()
print("Option 2: Set all courses to Semester 1 automatically")
response = input("Set all courses to Semester 1? (yes/no): ").strip().lower()

if response == 'yes':
    for course in courses:
        if course.semester is None:
            course.semester = 1
            print(f"  ✓ Set '{course.title}' to Semester 1")
    db.commit()
    print("\n✅ All courses set to Semester 1!")
else:
    print("\n⚠️ Please set course semesters manually via Admin UI")

print("\n" + "="*60)
print("📊 Current Status:")
print("="*60)
students = db.query(Student).all()
for s in students:
    print(f"Student: {s.name} → Semester {s.current_semester}")

courses = db.query(Course).all()
for c in courses:
    print(f"Course: {c.title} ({c.code}) → Semester {c.semester or 'NOT SET'}")

db.close()

print("\n✅ Setup complete! Refresh your browser and try course registration.")
print("   Student can now see courses for their semester!")
