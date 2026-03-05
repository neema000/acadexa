from backend.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Add current_semester to students
    try:
        conn.execute(text("ALTER TABLE students ADD COLUMN current_semester INTEGER DEFAULT 1"))
        conn.commit()
        print("✅ Added current_semester column to students")
    except Exception as e:
        print(f"⚠️ current_semester column: {e}")
    
    # Add semester to courses
    try:
        conn.execute(text("ALTER TABLE courses ADD COLUMN semester INTEGER"))
        conn.commit()
        print("✅ Added semester column to courses")
    except Exception as e:
        print(f"⚠️ semester column: {e}")
    
    # Add enrollment_status to enrollments
    try:
        conn.execute(text("ALTER TABLE enrollments ADD COLUMN enrollment_status VARCHAR(20) DEFAULT 'ongoing'"))
        conn.commit()
        print("✅ Added enrollment_status column to enrollments")
    except Exception as e:
        print(f"⚠️ enrollment_status column: {e}")
    
    # Update existing students to have semester 1
    try:
        conn.execute(text("UPDATE students SET current_semester = 1 WHERE current_semester IS NULL"))
        conn.commit()
        print("✅ Updated existing students to semester 1")
    except Exception as e:
        print(f"⚠️ Update students: {e}")
    
    # Update existing enrollments to have 'ongoing' status
    try:
        conn.execute(text("UPDATE enrollments SET enrollment_status = 'ongoing' WHERE enrollment_status IS NULL"))
        conn.commit()
        print("✅ Updated existing enrollments to 'ongoing' status")
    except Exception as e:
        print(f"⚠️ Update enrollments: {e}")

print("\n🎉 Database migration complete!")
