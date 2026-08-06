from dataclasses import dataclass
from datetime import time
from itertools import combinations
from uuid import UUID

from .models import ClassMeeting, ScheduleScenario


@dataclass(frozen=True)
class ScheduleConflict:
    first_meeting_id: UUID
    first_section_id: UUID
    first_course_code: str
    second_meeting_id: UUID
    second_section_id: UUID
    second_course_code: str
    day_of_week: int
    day_label: str
    overlap_start: time
    overlap_end: time

    def as_dict(self) -> dict[str, object]:
        return {
            'first_meeting_id': str(self.first_meeting_id),
            'first_section_id': str(self.first_section_id),
            'first_course_code': self.first_course_code,
            'second_meeting_id': str(self.second_meeting_id),
            'second_section_id': str(self.second_section_id),
            'second_course_code': self.second_course_code,
            'day_of_week': self.day_of_week,
            'day_label': self.day_label,
            'overlap_start': self.overlap_start.isoformat(
                timespec='minutes',
            ),
            'overlap_end': self.overlap_end.isoformat(
                timespec='minutes',
            ),
        }


def detect_schedule_conflicts(
    scenario: ScheduleScenario,
) -> list[ScheduleConflict]:
    selections = scenario.selections.select_related(
        'theory_section',
        'laboratory_section',
    )
    section_ids = set()

    for selection in selections:
        section_ids.add(selection.theory_section_id)

        if selection.laboratory_section_id is not None:
            section_ids.add(selection.laboratory_section_id)

    meetings = list(
        ClassMeeting.objects.filter(
            section_id__in=section_ids,
        )
        .select_related(
            'section',
            'section__course_offering__course',
        )
        .order_by(
            'day_of_week',
            'start_time',
            'end_time',
            'pk',
        )
    )
    conflicts = []

    for first, second in combinations(meetings, 2):
        if first.section_id == second.section_id:
            continue

        if first.day_of_week != second.day_of_week:
            continue

        overlap_start = max(first.start_time, second.start_time)
        overlap_end = min(first.end_time, second.end_time)

        if overlap_start >= overlap_end:
            continue

        conflicts.append(
            ScheduleConflict(
                first_meeting_id=first.public_id,
                first_section_id=first.section.public_id,
                first_course_code=(first.section.course_offering.course.code),
                second_meeting_id=second.public_id,
                second_section_id=second.section.public_id,
                second_course_code=(second.section.course_offering.course.code),
                day_of_week=first.day_of_week,
                day_label=first.get_day_of_week_display(),
                overlap_start=overlap_start,
                overlap_end=overlap_end,
            )
        )

    return conflicts
