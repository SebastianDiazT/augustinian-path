from unittest.mock import Mock

import pytest
from rest_framework.serializers import ValidationError

from apps.curricula.models import Course
from apps.curricula.serializers import (
    CourseSerializer,
    PrerequisiteSerializer,
    validate_component_weights_sum_to_100,
)

pytestmark = pytest.mark.django_db


class TestCurriculaSerializers:
    def test_course_serializer_validation(self):
        serializer = CourseSerializer()
        with pytest.raises(ValidationError):
            serializer.validate({'branch': Mock(), 'course_type': Course.CourseType.MANDATORY})

        valid_attrs = {'branch': Mock(), 'course_type': Course.CourseType.ELECTIVE}
        assert serializer.validate(valid_attrs) == valid_attrs

    def test_prerequisite_serializer_validation(self):
        serializer = PrerequisiteSerializer()
        c1 = Mock(curriculum_plan_id=1)
        c2 = Mock(curriculum_plan_id=2)

        with pytest.raises(ValidationError):
            serializer.validate({'course': c1, 'required_course': c2})

        with pytest.raises(ValidationError):
            serializer.validate({'course': c1, 'required_course': c1})

        c3 = Mock(curriculum_plan_id=1)
        valid_attrs = {'course': c1, 'required_course': c3}
        assert serializer.validate(valid_attrs) == valid_attrs

    def test_validate_component_weights_sum_to_100(self):
        with pytest.raises(ValidationError):
            validate_component_weights_sum_to_100([{'weight': 50}, {'weight': 40}])

        validate_component_weights_sum_to_100([{'weight': 50.5}, {'weight': 49.5}])
