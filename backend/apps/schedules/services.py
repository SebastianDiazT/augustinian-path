from django.db import transaction
from rest_framework import serializers as drf_serializers

from apps.academic_records.criticality import pick_course_to_drop
from apps.academic_records.models import CourseEnrollment
from apps.core.permissions import student_has_verified_membership
from apps.curricula.models import Prerequisite
from apps.offerings.models import Offering, Section

from . import generator
from .models import ScheduleAlternative, ScheduleAlternativeSection, ScheduleSimulation


class SimulationInputError(drf_serializers.ValidationError):
    """Raised for anything that should stop the simulation before it
    even starts (unmet prerequisite, unverified membership, a course
    with zero selectable options, etc.) — surfaces as the usual
    VALIDATION_ERROR envelope."""


def _unmet_prerequisites(student, course):
    passed_ids = set(
        CourseEnrollment.objects.filter(
            student=student, status=CourseEnrollment.Status.PASSED,
        ).values_list('offering__course_id', flat=True),
    )
    required = Prerequisite.objects.filter(course=course).select_related('required_course')
    return [r.required_course for r in required if r.required_course_id not in passed_ids]


def _validate_can_take(student, offerings):
    for offering in offerings:
        course = offering.course
        school = course.get_school()
        if not student_has_verified_membership(student.user, school):
            raise SimulationInputError(
                f'Tu membresía para la escuela de "{course.name}" todavía no '
                'está verificada.',
            )
        # TODO (V2): Reactivar la validación de prerrequisitos cuando se migre
        # el historial completo de notas de los estudiantes de años superiores.
        #
        # missing = _unmet_prerequisites(student, course)
        # if missing:
        #     names = ', '.join(c.name for c in missing)
        #     raise SimulationInputError(
        #         f'No puedes seleccionar "{course.name}": te falta aprobar '
        #         f'el prerrequisito {names}.',
        #     )


def _section_tuple(section, excluded_section_ids, excluded_instructor_ids):
    if str(section.public_id) in excluded_section_ids:
        return None
    instructor_public_id = str(section.instructor.public_id)
    if instructor_public_id in excluded_instructor_ids:
        return None
    meetings = [(m.day_of_week, m.time_block.order) for m in section.meetings.all()]
    mask = generator.bitmask_from_meetings(meetings)
    return section.id, instructor_public_id, mask


def _build_course_options_for_offering(offering, excluded_section_ids, excluded_instructor_ids):
    theory, lab = [], []
    for section in offering.sections.all():
        item = _section_tuple(section, excluded_section_ids, excluded_instructor_ids)
        if item is None:
            continue
        if section.section_type == Section.SectionType.THEORY:
            theory.append(item)
        else:
            lab.append(item)

    if not theory:
        raise SimulationInputError(
            f'"{offering.course.name}" no tiene ningún grupo de teoría '
            'disponible con los filtros aplicados.',
        )
    if offering.course.has_lab and not lab:
        raise SimulationInputError(
            f'"{offering.course.name}" tiene laboratorio, pero no quedó '
            'ningún grupo de laboratorio disponible con los filtros aplicados.',
        )

    return generator.build_course_options(
        offering.id, offering.course.name, theory, lab if offering.course.has_lab else [],
    )


def _persist_simulation(student, academic_term, offering_ids, preferences, notes, top):
    """top: list of (combination, score, description) tuples, already
    ranked. Creates the ScheduleSimulation + its alternatives inside one
    transaction."""

    with transaction.atomic():
        simulation = ScheduleSimulation.objects.create(
            student=student,
            academic_term=academic_term,
            preferences=preferences,
            notes='\n'.join(notes),
        )
        simulation.offerings.set(offering_ids)

        for rank, (combination, score, description) in enumerate(top, start=1):
            alternative = ScheduleAlternative.objects.create(
                simulation=simulation, score=score, description=description, rank=rank,
            )
            section_ids = [
                section_id for option in combination.values() for section_id in option.section_ids
            ]
            ScheduleAlternativeSection.objects.bulk_create([
                ScheduleAlternativeSection(alternative=alternative, section_id=section_id)
                for section_id in section_ids
            ])

    return simulation


def run_simulation(
    student,
    academic_term,
    offering_ids,
    excluded_section_ids=None,
    excluded_instructor_ids=None,
    preferences=None,
):
    """Entry point used by the view. Returns a list of ScheduleSimulation
    — normally one, two only when an unresolvable "curso crítico" tie
    forced branching into two variants (see generator.resolve_conflicts_and_branch)."""

    excluded_section_ids = set(excluded_section_ids or [])
    excluded_instructor_ids = set(excluded_instructor_ids or [])
    preferences = preferences or {}

    offerings = list(
        Offering.objects.filter(id__in=offering_ids, academic_term=academic_term)
        .select_related('course')
        .prefetch_related('sections__meetings__time_block', 'sections__instructor'),
    )
    if len(offerings) != len(set(offering_ids)):
        raise SimulationInputError(
            'Una o más de las asignaturas seleccionadas no existen en este periodo.'
        )

    _validate_can_take(student, offerings)

    course_options_list = [
        _build_course_options_for_offering(offering, excluded_section_ids, excluded_instructor_ids)
        for offering in offerings
    ]
    offerings_by_id = {o.id: o for o in offerings}

    def pick_fn(offering_id_a, offering_id_b):
        course_a = offerings_by_id[offering_id_a].course
        course_b = offerings_by_id[offering_id_b].course
        result = pick_course_to_drop(student, course_a, course_b)
        if result is None:
            return None
        _kept, dropped, reason = result
        dropped_offering_id = offering_id_a if dropped == course_a else offering_id_b
        return dropped_offering_id, reason

    variants = generator.resolve_conflicts_and_branch(course_options_list, pick_fn)

    simulations = []
    for variant_options, notes in variants:
        top = generator.top_alternatives(variant_options, preferences)
        variant_offering_ids = [c.offering_id for c in variant_options]
        if not top:
            notes = notes + [
                'No se encontró ninguna combinación de horario sin cruces con '
                'las asignaturas y filtros seleccionados.',
            ]
        simulation = _persist_simulation(
            student, academic_term, variant_offering_ids, preferences, notes, top,
        )
        simulations.append(simulation)

    return simulations
