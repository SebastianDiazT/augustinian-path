from unittest.mock import patch

import pytest

# from apps.curricula.models import Prerequisite
from apps.schedules.services import SimulationInputError, run_simulation

pytestmark = pytest.mark.django_db


@patch('apps.schedules.services.student_has_verified_membership', return_value=True)
@patch('apps.schedules.services.pick_course_to_drop')
def test_run_simulation_success(
    mock_pick,
    mock_membership,
    student_profile_factory,
    offering_factory,
    section_factory,
    meeting_factory,
):
    student = student_profile_factory()
    offering = offering_factory()
    section = section_factory(offering=offering)
    meeting_factory(section=section)

    simulations = run_simulation(
        student=student, academic_term=offering.academic_term, offering_ids=[offering.id]
    )

    assert len(simulations) == 1
    assert simulations[0].alternatives.count() >= 1


@patch('apps.schedules.services.student_has_verified_membership', return_value=False)
def test_run_simulation_unverified_membership(
    mock_membership, student_profile_factory, offering_factory
):
    student = student_profile_factory()
    offering = offering_factory()

    with pytest.raises(SimulationInputError, match='todavía no está verificada'):
        run_simulation(student, offering.academic_term, [offering.id])


# @pytest.mark.skip(reason="Validación de prerrequisitos desactivada temporalmente para la V1")
# @patch('apps.schedules.services.student_has_verified_membership', return_value=True)
# def test_run_simulation_unmet_prereq(
#     mock_membership, student_profile_factory, course_factory, offering_factory
# ):
#     student = student_profile_factory()
#     course = course_factory()
#     prereq = course_factory(curriculum_plan=course.curriculum_plan)
#     Prerequisite.objects.create(course=course, required_course=prereq)

#     offering = offering_factory(course=course)

#     with pytest.raises(SimulationInputError, match='te falta aprobar el prerrequisito'):
#         run_simulation(student, offering.academic_term, [offering.id])


@patch('apps.schedules.services.student_has_verified_membership', return_value=True)
def test_run_simulation_no_valid_theory_group(
    mock_membership, student_profile_factory, offering_factory, section_factory
):
    student = student_profile_factory()
    offering = offering_factory()
    section = section_factory(offering=offering)

    with pytest.raises(SimulationInputError, match='ningún grupo de teoría disponible'):
        run_simulation(
            student,
            offering.academic_term,
            [offering.id],
            excluded_section_ids=[str(section.public_id)],
        )
