# tests/test_nlp_processor_extended.py

import pytest

from nlp.nlp_processor import parse_command


def test_list_students_basic():
    cmd = "List all students"
    parsed = parse_command(cmd)
    assert parsed["intent"] == "list_students"
    assert parsed["slots"] == {}


def test_list_students_in_course():
    cmd = "list students in course cs101"
    parsed = parse_command(cmd)
    assert parsed["intent"] == "list_students"
    assert parsed["slots"] == {"course": "cs101"}


def test_list_enrollments_for_student():
    cmd = "show enrollments for student 3"
    parsed = parse_command(cmd)
    assert parsed["intent"] == "list_enrollments_for_student"
    assert parsed["slots"]["student_id"] == 3


def test_show_all_courses():
    cmd = "Show all courses"
    parsed = parse_command(cmd)
    assert parsed["intent"] == "list_courses"
    assert parsed["slots"] == {}


def test_show_teachers():
    cmd = "Show teachers"
    parsed = parse_command(cmd)
    assert parsed["intent"] == "list_teachers"
    assert parsed["slots"] == {}


def test_list_courses_in_department():
    cmd = "list courses in department CS"
    parsed = parse_command(cmd)
    assert parsed["intent"] == "list_courses"
    # department normalized to upper case in intents.py
    assert parsed["slots"]["department"] == "CS"


def test_list_courses_for_teacher():
    cmd = "list courses for teacher 2"
    parsed = parse_command(cmd)
    assert parsed["intent"] == "list_courses"
    assert parsed["slots"]["teacher_id"] == 2


def test_unknown_intent():
    cmd = "what is the weather today"
    parsed = parse_command(cmd)
    assert parsed["intent"] == "unknown"
    assert parsed["slots"] == {}


def test_polite_attendance_phrase_maps_to_rule_intent():
    cmd = "would you show me please my attendance"
    parsed = parse_command(cmd)
    assert parsed["intent"] == "show_my_attendance"
    assert parsed["slots"] == {}


def test_list_first_5_students_maps_limit_slot():
    cmd = "list first 5 students"
    parsed = parse_command(cmd)
    assert parsed["intent"] == "list_students"
    assert parsed["slots"]["limit"] == 5


def test_get_me_first_five_students_maps_limit_slot():
    cmd = "get me first five students"
    parsed = parse_command(cmd)
    assert parsed["intent"] == "list_students"
    assert parsed["slots"]["limit"] == 5
