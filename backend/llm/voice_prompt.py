from typing import Dict, List

# ✅ Only intents that your voice.py ACTUALLY handles safely right now
# (and which exist in your nlp/intents.py)
ALLOWED_INTENTS: List[str] = [
    "show_my_cgpa",
    "show_my_courses",
    "show_my_result",
    "show_my_attendance",
    "show_my_attendance_course",
    "list_students",
    "list_courses",
    "list_teachers",
    "list_enrollments_for_student",
    "unknown",
]

# ✅ slots that exist in your intents.py patterns AND used in voice.py
SLOT_KEYS: List[str] = [
    "course_code",     # for show_my_attendance_course (and also list filters)
    "course",          # list_students in course <code>
    "department",      # list_students/list_courses
    "student_id",      # list_enrollments_for_student
    "teacher_id",      # list_courses by teacher_id (even if not handled yet in voice.py)
]

DEFAULT_SLOTS = {k: None for k in SLOT_KEYS}


def build_voice_prompt(text: str, role: str, user_context: Dict) -> str:
    return f"""
You are an intent router for a Voice-Controlled LMS (ACADEXA).
Convert the user's command into STRICT JSON for the backend.

CRITICAL RULES:
- Output ONLY valid JSON. No explanation, no markdown.
- intent MUST be one of: {ALLOWED_INTENTS}
- slots MUST ONLY contain these keys: {SLOT_KEYS}
- If user asks for create/update/delete/assign/enroll/register/drop actions, DO NOT produce those intents.
  Instead set intent="unknown". (Voice console is read-only.)
- If command is ambiguous or missing required info (like course_code), ask a clarification question.

ROLE CONTEXT:
- user role: {role}
- context: {user_context}

NOTES:
- If user says "attendance in CS 101" normalize to course_code "CS-101"
- course_code should be uppercase
- department should be uppercase

JSON SCHEMA (must match exactly):
{{
  "intent": "unknown",
  "slots": {{
    "course_code": null,
    "course": null,
    "department": null,
    "student_id": null,
    "teacher_id": null
  }},
  "needs_clarification": false,
  "clarifying_question": null,
  "confidence": 0.0
}}

USER COMMAND:
{text}
""".strip()
