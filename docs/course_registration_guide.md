# Course Registration System Guide

## Overview
This document describes the new semester-based course registration system that allows students to self-register for courses.

## Features Implemented

### 1. **Database Schema Changes**
- **Student.current_semester** (Integer 1-8): Tracks which semester the student is currently in
- **Course.semester** (Integer 1-8): Admin sets which semester a course belongs to
- **Enrollment.enrollment_status** (String): Tracks if enrollment is "ongoing", "passed", or "failed"

### 2. **Backend API Endpoints**
- **GET /course-registration/available-courses**
  - Returns courses for student's current semester
  - Includes failed courses from previous semesters
  - Each course shows: `is_enrolled` and `is_failed` flags

- **POST /course-registration/enroll**
  - Student self-enrolls in a course
  - Validates: semester eligibility, no duplicate enrollments
  - Allows re-enrollment in failed courses

- **DELETE /course-registration/unenroll/{enrollment_id}**
  - Student can drop a course before completion

### 3. **Frontend Components**

#### **CourseRegistrationPage** (New)
- Shows available courses for current semester
- Displays failed courses in a special section with red badge
- Enroll/Unenroll buttons for each course
- Shows total enrolled credits
- Registration guidelines section

#### **StudentHome** (Updated)
- Added "Register Courses" tab between "Courses" and "Enrollments"
- Loads CourseRegistrationPage component when tab is active

#### **CoursesPage** (Updated - Admin)
- Added "Semester (1-8)" dropdown in course form
- Admin can assign courses to specific semesters
- Semester column added to courses table

### 4. **Styling**
New CSS classes added in index.css:
- `.courses-section`: Container for course sections
- `.courses-grid`: Responsive grid layout for course cards
- `.course-card`: Individual course card with hover effects
- `.failed-course`: Red border for failed courses
- `.course-badge`: "Failed" badge on failed course cards
- `.student-info-banner`: Shows current semester and credits
- `.info-section`: Registration guidelines box

## How It Works

### For Students:
1. Navigate to Student Portal → **Register Courses** tab
2. View available courses for your current semester
3. If you failed any courses, they appear in the **"Failed Courses"** section
4. Click **"Enroll"** to register for a course
5. Click **"Drop Course"** to unenroll before semester ends
6. Track total enrolled credit hours at the top

### For Admins/HOD:
1. Navigate to **Courses** page
2. When creating/editing a course, select **Semester (1-8)** from dropdown
3. Students will only see courses matching their current semester
4. Set `Student.current_semester` in database (1-8) for each student

### For Teachers:
1. Mark student enrollments with grades
2. System automatically sets `enrollment_status = "failed"` for failing grades
3. Failed courses appear with next semester courses for re-enrollment

## API Request Examples

### Get Available Courses
```bash
GET /course-registration/available-courses
Authorization: Bearer <student_token>
```

Response:
```json
[
  {
    "course_id": 101,
    "course_name": "Data Structures",
    "course_code": "CS201",
    "credit_hours": 3,
    "semester": 2,
    "is_enrolled": false,
    "is_failed": false,
    "enrollment_id": null
  },
  {
    "course_id": 85,
    "course_name": "Database Systems",
    "course_code": "CS150",
    "credit_hours": 4,
    "semester": 1,
    "is_enrolled": false,
    "is_failed": true,
    "enrollment_id": null
  }
]
```

### Enroll in Course
```bash
POST /course-registration/enroll
Authorization: Bearer <student_token>
Content-Type: application/json

{
  "course_id": 101
}
```

### Unenroll from Course
```bash
DELETE /course-registration/unenroll/42
Authorization: Bearer <student_token>
```

## Database Updates Needed

Before testing, you need to:

1. **Add new columns** (or restart server to auto-create):
   ```sql
   ALTER TABLE students ADD COLUMN current_semester INTEGER DEFAULT 1;
   ALTER TABLE courses ADD COLUMN semester INTEGER;
   ALTER TABLE enrollments ADD COLUMN enrollment_status VARCHAR(20) DEFAULT 'ongoing';
   ```

2. **Set student semesters**:
   ```sql
   UPDATE students SET current_semester = 1 WHERE id = <student_id>;
   ```

3. **Set course semesters** (via admin UI or SQL):
   ```sql
   UPDATE courses SET semester = 1 WHERE id IN (1, 2, 3);  -- First semester courses
   UPDATE courses SET semester = 2 WHERE id IN (4, 5, 6);  -- Second semester courses
   ```

## Testing Steps

1. **Start Backend Server**:
   ```bash
   cd F:\FYP\ACADEXA
   python -m uvicorn backend.main:app --reload
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm start
   ```

3. **Login as Admin**:
   - Go to Courses page
   - Create/edit courses and assign semesters

4. **Update Student Semester** (via database):
   ```sql
   UPDATE students SET current_semester = 2 WHERE email = 'student@test.com';
   ```

5. **Login as Student**:
   - Go to "Register Courses" tab
   - See only semester 2 courses
   - Enroll in courses
   - Check "Enrollments" tab to confirm

6. **Test Failed Course**:
   ```sql
   -- Mark an enrollment as failed
   UPDATE enrollments 
   SET enrollment_status = 'failed', grade = 'F' 
   WHERE id = <enrollment_id>;
   
   -- Move student to next semester
   UPDATE students SET current_semester = 3 WHERE id = <student_id>;
   ```
   - Login as student
   - Failed course should appear in red "Failed Courses" section
   - Student can re-enroll

## Implementation Notes

- **Default semester**: New courses have `semester = NULL` (not assigned)
- **Default student semester**: New students have `current_semester = 1`
- **Enrollment status**: 
  - "ongoing" = currently enrolled
  - "passed" = completed successfully
  - "failed" = needs re-enrollment
- **Re-enrollment**: Students can enroll in failed courses again (creates new enrollment)
- **Credit tracking**: Frontend shows total enrolled credit hours
- **Validation**: Backend prevents duplicate enrollments in same semester

## Future Enhancements

Consider adding:
- Credit hour limits per semester (e.g., max 18 credits)
- Prerequisites system (Course A required before Course B)
- Registration period restrictions (open/close dates)
- Waitlist functionality for full courses
- Advisor approval for registration
- Bulk semester updates (promote all students to next semester)
- Email notifications for registration deadlines

## Files Modified

### Backend:
- `backend/models.py` - Added fields
- `backend/routes/course_registration.py` - New file
- `backend/main.py` - Router registration

### Frontend:
- `frontend/src/CourseRegistrationPage.tsx` - New component
- `frontend/src/StudentHome.tsx` - Added tab
- `frontend/src/CoursesPage.tsx` - Added semester field
- `frontend/src/types.ts` - Updated interfaces
- `frontend/src/index.css` - Added styles

## Support

For issues or questions:
1. Check backend logs: `backend.log`
2. Check browser console for frontend errors
3. Verify database has new columns
4. Ensure student has `current_semester` set
5. Ensure courses have `semester` assigned
