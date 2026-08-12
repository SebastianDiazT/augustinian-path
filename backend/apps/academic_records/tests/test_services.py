import uuid
from collections import namedtuple
from decimal import Decimal

from apps.academic_records.services import build_grade_scenarios

MockComponent = namedtuple('MockComponent', ['public_id', 'weight'])


def test_already_complete_scenario():
    """Prueba cuando el estudiante ya tiene notas en todas las fases."""
    c1 = MockComponent(uuid.uuid4(), Decimal('50.0'))
    c2 = MockComponent(uuid.uuid4(), Decimal('50.0'))

    existing_grades = {
        str(c1.public_id): Decimal('12.0'),
        str(c2.public_id): Decimal('10.0'),
    }

    result = build_grade_scenarios([c1, c2], existing_grades)

    assert result['already_complete'] is True
    assert result['passes'] is True
    assert result['final_score'] == '11.00'
    assert result['scenarios'] == []


def test_scenarios_feasible():
    c1 = MockComponent(uuid.uuid4(), Decimal('60.0'))
    c2 = MockComponent(uuid.uuid4(), Decimal('40.0'))

    existing_grades = {str(c1.public_id): Decimal('12.0')}

    result = build_grade_scenarios([c1, c2], existing_grades)

    assert result['already_complete'] is False
    scenarios = result['scenarios']

    uniform = next(s for s in scenarios if s['key'] == 'uniform')
    assert uniform['required_grades'][str(c2.public_id)] == '8.25'
    assert uniform['feasible'] is True
    assert uniform['passes'] is True


def test_scenarios_infeasible():
    c1 = MockComponent(uuid.uuid4(), Decimal('80.0'))
    c2 = MockComponent(uuid.uuid4(), Decimal('20.0'))

    existing_grades = {str(c1.public_id): Decimal('05.0')}

    result = build_grade_scenarios([c1, c2], existing_grades)
    uniform = result['scenarios'][0]

    assert uniform['required_grades'][str(c2.public_id)] == '20.00'
    assert uniform['passes'] is False


def test_custom_scenario():
    c1 = MockComponent(uuid.uuid4(), Decimal('30.0'))
    c2 = MockComponent(uuid.uuid4(), Decimal('30.0'))
    c3 = MockComponent(uuid.uuid4(), Decimal('40.0'))

    existing_grades = {str(c1.public_id): Decimal('10.0')}
    requested_grades = {str(c2.public_id): Decimal('20.0')}

    result = build_grade_scenarios([c1, c2, c3], existing_grades, requested_grades)

    custom = next(s for s in result['scenarios'] if s['key'] == 'custom')
    assert custom['required_grades'][str(c2.public_id)] == '20.00'
    assert custom['required_grades'][str(c3.public_id)] == '3.75'
    assert custom['projected_final_score'] == '10.50'
