import React, { useState, useEffect } from 'react';
import { api } from './api/client';

interface AvailableCourse {
  course_id: number;
  course_name: string;
  course_code: string;
  credit_hours: number;
  semester: number;
  is_enrolled: boolean;
  is_failed: boolean;
  enrollment_id: number | null;
}

interface StudentInfo {
  id: number;
  name: string;
  department: string;
  gpa: number;
  current_semester: number;
}

const CourseRegistrationPage: React.FC = () => {
  const [courses, setCourses] = useState<AvailableCourse[]>([]);
  const [studentInfo, setStudentInfo] = useState<StudentInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch student info
      const studentResponse = await api.get('/students/me');
      setStudentInfo(studentResponse.data);

      // Fetch available courses
      const coursesResponse = await api.get('/course-registration/available-courses');
      setCourses(coursesResponse.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load courses');
    } finally {
      setLoading(false);
    }
  };

  const handleEnroll = async (courseId: number) => {
    setError(null);
    setSuccessMessage(null);
    try {
      await api.post('/course-registration/enroll', { course_id: courseId });
      setSuccessMessage('Successfully enrolled in course!');
      // Refresh courses list
      await fetchData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to enroll in course');
    }
  };

  const handleUnenroll = async (enrollmentId: number) => {
    setError(null);
    setSuccessMessage(null);
    try {
      await api.delete(`/course-registration/unenroll/${enrollmentId}`);
      setSuccessMessage('Successfully dropped course!');
      // Refresh courses list
      await fetchData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to drop course');
    }
  };

  const currentSemesterCourses = courses.filter(c => 
    c.semester === studentInfo?.current_semester && !c.is_failed
  );
  
  const failedCourses = courses.filter(c => c.is_failed);

  const totalEnrolledCredits = courses
    .filter(c => c.is_enrolled)
    .reduce((sum, c) => sum + c.credit_hours, 0);

  if (loading) {
    return (
      <div className="container">
        <div className="loading-spinner">Loading courses...</div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1>Course Registration</h1>
        {studentInfo && (
          <div className="student-info-banner">
            <p>
              <strong>Student:</strong> {studentInfo.name}
            </p>
            <p>
              <strong>Current Semester:</strong> {studentInfo.current_semester}
            </p>
            <p>
              <strong>Total Credits Enrolled:</strong> {totalEnrolledCredits}
            </p>
          </div>
        )}
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      {successMessage && (
        <div className="alert alert-success">
          {successMessage}
        </div>
      )}

      {failedCourses.length > 0 && (
        <div className="courses-section failed-section">
          <h2 className="section-title">📌 Failed Courses - Re-enrollment Required</h2>
          <div className="courses-grid">
            {failedCourses.map(course => (
              <div key={course.course_id} className="course-card failed-course">
                <div className="course-badge">Failed</div>
                <h3>{course.course_name}</h3>
                <p className="course-code">{course.course_code}</p>
                <p className="course-semester">Originally from Semester {course.semester}</p>
                <p className="course-credits">{course.credit_hours} Credit Hours</p>
                {course.is_enrolled ? (
                  <button
                    className="btn btn-secondary"
                    onClick={() => course.enrollment_id && handleUnenroll(course.enrollment_id)}
                  >
                    Drop Course
                  </button>
                ) : (
                  <button
                    className="btn btn-primary"
                    onClick={() => handleEnroll(course.course_id)}
                  >
                    Re-enroll
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="courses-section">
        <h2 className="section-title">
          📚 Semester {studentInfo?.current_semester} Courses
        </h2>
        {currentSemesterCourses.length === 0 ? (
          <div className="empty-state">
            <p>No courses available for your current semester.</p>
            <p className="hint">Contact your HOD if you think this is an error.</p>
          </div>
        ) : (
          <div className="courses-grid">
            {currentSemesterCourses.map(course => (
              <div key={course.course_id} className="course-card">
                <h3>{course.course_name}</h3>
                <p className="course-code">{course.course_code}</p>
                <p className="course-semester">Semester {course.semester}</p>
                <p className="course-credits">{course.credit_hours} Credit Hours</p>
                {course.is_enrolled ? (
                  <button
                    className="btn btn-secondary"
                    onClick={() => course.enrollment_id && handleUnenroll(course.enrollment_id)}
                  >
                    Drop Course
                  </button>
                ) : (
                  <button
                    className="btn btn-primary"
                    onClick={() => handleEnroll(course.course_id)}
                  >
                    Enroll
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="info-section">
        <h3>📋 Registration Guidelines</h3>
        <ul>
          <li>You can only enroll in courses for your current semester</li>
          <li>Failed courses from previous semesters must be re-registered</li>
          <li>You can drop courses before the semester ends</li>
          <li>Make sure to register for all required courses</li>
        </ul>
      </div>
    </div>
  );
};

export default CourseRegistrationPage;
