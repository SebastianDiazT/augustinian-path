import pytest
from rest_framework.exceptions import ValidationError

from apps.offerings.serializers import validate_meeting_count_matches_course_hours


def test_validate_meeting_count_matches(mocker):
    mock_section = mocker.Mock()
    mock_section.expected_meeting_count = 3

    validate_meeting_count_matches_course_hours(mock_section, [1, 2, 3])


def test_validate_meeting_count_fails(mocker):
    mock_section = mocker.Mock()
    mock_section.expected_meeting_count = 4

    with pytest.raises(ValidationError) as exc:
        validate_meeting_count_matches_course_hours(mock_section, [1, 2])

    assert 'Este grupo necesita 4 bloques' in str(exc.value.detail[0])
    assert 'se enviaron 2' in str(exc.value.detail[0])
