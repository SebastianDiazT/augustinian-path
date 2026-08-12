import datetime

import pytest

from apps.offerings.models import Section

pytestmark = pytest.mark.django_db


def test_expected_meeting_count_theory(course_factory, section_factory):
    course = course_factory(
        theory_hours=2, practice_hours=1, seminar_hours=1, theory_practice_hours=0, lab_hours=2
    )
    section = section_factory(offering__course=course, section_type=Section.SectionType.THEORY)
    assert section.expected_meeting_count == 4


def test_expected_meeting_count_lab(course_factory, section_factory):
    course = course_factory(lab_hours=3, theory_hours=5)
    section = section_factory(offering__course=course, section_type=Section.SectionType.LAB)
    assert section.expected_meeting_count == 3


def test_timeblock_str_representation(time_block_factory):
    tb = time_block_factory(start_time=datetime.time(7, 0), end_time=datetime.time(7, 50))
    assert str(tb) == '07:00-07:50'


def test_offering_methods(offering_factory):
    offering = offering_factory()
    assert str(offering.course) in str(offering)
    assert str(offering.academic_term) in str(offering)
    assert offering.get_school() == offering.course.get_school()


def test_section_methods(section_factory):
    section = section_factory(section_type=Section.SectionType.THEORY, number='A')
    assert 'Teoría' in str(section)
    assert 'A' in str(section)
    assert section.get_school() == section.offering.get_school()


def test_meeting_methods(meeting_factory):
    meeting = meeting_factory()
    assert str(meeting.section) in str(meeting)
    assert meeting.get_day_of_week_display() in str(meeting)
