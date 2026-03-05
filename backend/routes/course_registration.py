# backend/routes/course_registration.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database import get_db_connection
from backend.models import Student, Course, Enrollment, User, UserRole
from backend.security import get_current_user

router = APIRouter(prefix="/course-registration", tags=["Course Registration"])


def _role_value(role):
    return role.value if hasattr(role, "value") else role


# Response models
class AvailableCourse(BaseModel):
    course_id: int
    course_name: str
    course_code: str
    credit_hours: int
    semester: int | None
    is_enrolled: bool
    is_failed: bool = False  # True if student failed this course before
    enrollment_id: int | None = None  # ID if already enrolled
    
    class Config:
        from_attributes = True


class SelfEnrollRequest(BaseModel):
    course_id: int


@router.get("/available-courses")
def get_available_courses(
    db: Session = Depends(get_db_connection),
    current_user: User = Depends(get_current_user),
):
    """
    Get available courses for student based on their current semester.
    Also includes failed courses from previous semesters.
    """
    role_value = _role_value(current_user.role)
    if role_value != UserRole.student:
        raise HTTPException(status_code=403, detail="Student access required")
    
    if not current_user.student:
        raise HTTPException(status_code=404, detail="Student record not linked")
    
    student = current_user.student
    current_semester = student.current_semester or 1
    
    # Get all courses for current semester
    semester_courses = db.query(Course).filter(Course.semester == current_semester).all()
    
    # Get student's enrollments
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student.id
    ).all()
    
    enrolled_course_ids = {e.course_id for e in enrollments if e.enrollment_status != "failed"}
    failed_enrollments = [e for e in enrollments if e.enrollment_status == "failed"]
    
    # Get failed courses
    failed_course_ids = {e.course_id for e in failed_enrollments}
    failed_courses = db.query(Course).filter(Course.id.in_(failed_course_ids)).all() if failed_course_ids else []
    
    # Build available courses list
    available = []
    
    # Current semester courses
    for course in semester_courses:
        enrollment_id = None
        if course.id in enrolled_course_ids:
            enrollment = next((e for e in enrollments if e.course_id == course.id and e.enrollment_status != "failed"), None)
            enrollment_id = enrollment.id if enrollment else None
            
        available.append(AvailableCourse(
            course_id=course.id,
            course_name=course.title,
            course_code=course.code,
            credit_hours=course.credit_hours,
            semester=course.semester,
            is_enrolled=course.id in enrolled_course_ids,
            is_failed=False,
            enrollment_id=enrollment_id
        ))
    
    # Failed courses from previous semesters
    for course in failed_courses:
        if course.id not in [c.course_id for c in available]:  # Avoid duplicates
            available.append(AvailableCourse(
                course_id=course.id,
                course_name=course.title,
                course_code=course.code,
                credit_hours=course.credit_hours,
                semester=course.semester,
                is_enrolled=False,
                is_failed=True,
                enrollment_id=None
            ))
    
    return available


@router.post("/enroll")
def self_enroll_course(
    payload: SelfEnrollRequest,
    db: Session = Depends(get_db_connection),
    current_user: User = Depends(get_current_user),
):
    """
    Allow student to self-register for a course.
    """
    role_value = _role_value(current_user.role)
    if role_value != UserRole.student:
        raise HTTPException(status_code=403, detail="Student access required")
    
    if not current_user.student:
        raise HTTPException(status_code=404, detail="Student record not linked")
    
    student = current_user.student
    current_semester = student.current_semester or 1
    
    # Check if course exists
    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if course is for current semester or if it's a failed course
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student.id,
        Enrollment.course_id == course.id
    ).first()
    
    if existing_enrollment and existing_enrollment.enrollment_status != "failed":
        raise HTTPException(status_code=400, detail="Already enrolled in this course")
    
    # Verify course is available (current semester or previously failed)
    is_current_semester = course.semester == current_semester
    is_failed_course = existing_enrollment and existing_enrollment.enrollment_status == "failed"
    
    if not is_current_semester and not is_failed_course:
        raise HTTPException(
            status_code=400, 
            detail=f"This course is for semester {course.semester}. You are in semester {current_semester}."
        )
    
    # Create or update enrollment
    if existing_enrollment:
        # Re-enrolling in failed course
        existing_enrollment.status = "enrolled"
        existing_enrollment.enrollment_status = "ongoing"
        existing_enrollment.grade = None
        db.commit()
        db.refresh(existing_enrollment)
        return {
            "message": "Successfully re-enrolled in course",
            "enrollment_id": existing_enrollment.id,
            "course": course.title
        }
    else:
        # New enrollment
        new_enrollment = Enrollment(
            student_id=student.id,
            course_id=course.id,
            semester=f"Semester {current_semester}",
            status="enrolled",
            enrollment_status="ongoing"
        )
        db.add(new_enrollment)
        db.commit()
        db.refresh(new_enrollment)
        
        return {
            "message": "Successfully enrolled in course",
            "enrollment_id": new_enrollment.id,
            "course": course.title
        }


@router.delete("/unenroll/{enrollment_id}")
def unenroll_course(
    enrollment_id: int,
    db: Session = Depends(get_db_connection),
    current_user: User = Depends(get_current_user),
):
    """
    Allow student to drop a course (before it's marked as completed).
    """
    role_value = _role_value(current_user.role)
    if role_value != UserRole.student:
        raise HTTPException(status_code=403, detail="Student access required")
    
    if not current_user.student:
        raise HTTPException(status_code=404, detail="Student record not linked")
    
    student = current_user.student
    
    enrollment = db.query(Enrollment).filter(
        Enrollment.id == enrollment_id,
        Enrollment.student_id == student.id
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    if enrollment.enrollment_status in ("passed", "failed"):
        raise HTTPException(status_code=400, detail="Cannot drop a completed course")
    
    db.delete(enrollment)
    db.commit()
    
    return {"message": "Successfully dropped course"}
