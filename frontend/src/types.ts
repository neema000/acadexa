// src/types.ts

// ---- Students ----
export interface Student {
  id: number;
  name: string;
  department: string;
  gpa: string; // backend se "3.40" string aati hai
  current_semester?: number; // ✅ NEW (1-8)
}

export interface StudentCreatePayload {
  name: string;
  department: string;
  gpa: number;

  // ✅ NEW (optional)
  email?: string;
  password?: string;
  current_semester?: number;
}

// ---- Auth ----
export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// ---- Teachers ----
export interface Teacher {
  id: number;
  name: string;
  department: string;
  email: string;
  expertise: string | null;
}

export interface TeacherPayload {
  name: string;
  department: string;
  email: string;
  expertise?: string | null;
}

// ---- Courses ----
export interface Course {
  id: number;
  title: string;
  code: string;
  credit_hours: number;
  teacher_id: number | null;
  semester?: number | null; // ✅ NEW (1-8)
}

export interface CoursePayload {
  title: string;
  code: string;
  credit_hours: number;
  teacher_id?: number | null;
  semester?: number | null; // ✅ NEW (1-8)
}

// ---- Enrollments ----
export interface Enrollment {
  id: number;
  student_id: number;
  course_id: number;
  semester: string | null;
  status: string | null; // "enrolled" | "dropped" | "completed" etc.
  grade: string | null;  // backend se Numeric string
  enrollment_status?: string; // ✅ NEW "ongoing" | "passed" | "failed"
}

export interface EnrollmentPayload {
  student_id: number;
  course_id: number;
  semester?: string;
  status?: string;
  grade?: number | null;
  enrollment_status?: string; // ✅ NEW
}


export type UserRole = "admin" | "student" | "teacher" | "hod" | "user";

export interface MeResponse {
  id: number;
  name: string;
  email: string;
  role: UserRole;
}
