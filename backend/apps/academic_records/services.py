from decimal import ROUND_HALF_UP, Decimal

PASSING_GRADE_THRESHOLD = Decimal('10.5')
MAX_GRADE = Decimal('20')
MIN_GRADE = Decimal('0')


def _quantize(value):
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def _clamp(value):
    return max(MIN_GRADE, min(MAX_GRADE, value))


def _weighted_points(score, weight):
    return score * weight / Decimal('100')


def _component_key(component):
    return str(component.public_id)


def _scenario_result(key, label, grades, pending_components, known_points):
    projected = known_points + sum(
        (_weighted_points(grades[_component_key(c)], c.weight) for c in pending_components),
        Decimal('0'),
    )
    feasible = all(MIN_GRADE <= g <= MAX_GRADE for g in grades.values())
    return {
        'key': key,
        'label': label,
        'required_grades': {
            key_: str(_quantize(value)) for key_, value in grades.items()
        },
        'projected_final_score': str(_quantize(projected)),
        'passes': projected >= PASSING_GRADE_THRESHOLD,
        'feasible': feasible,
    }


def build_grade_scenarios(components, existing_grades, requested_grades=None):
    completed = [c for c in components if _component_key(c) in existing_grades]
    pending = [c for c in components if _component_key(c) not in existing_grades]

    known_points = sum(
        (_weighted_points(existing_grades[_component_key(c)], c.weight) for c in completed),
        Decimal('0'),
    )

    if not pending:
        return {
            'already_complete': True,
            'final_score': str(_quantize(known_points)),
            'passes': known_points >= PASSING_GRADE_THRESHOLD,
            'scenarios': [],
        }

    remaining_needed = PASSING_GRADE_THRESHOLD - known_points
    scenarios = []

    total_pending_weight = sum((c.weight for c in pending), Decimal('0'))
    required_uniform = (
        (remaining_needed * Decimal('100')) / total_pending_weight
        if total_pending_weight > 0 else Decimal('0')
    )
    scenarios.append(_scenario_result(
        key='uniform',
        label='Reparto uniforme',
        grades={_component_key(c): _clamp(required_uniform) for c in pending},
        pending_components=pending,
        known_points=known_points,
    ))

    pending_by_weight = sorted(pending, key=lambda c: c.weight)
    heaviest = pending_by_weight[-1]
    rest = pending_by_weight[:-1]
    rest_weight = sum((c.weight for c in rest), Decimal('0'))

    points_rest_at_max = sum((_weighted_points(MAX_GRADE, c.weight) for c in rest), Decimal('0'))
    required_heaviest = (
        ((remaining_needed - points_rest_at_max) * Decimal('100')) / heaviest.weight
        if heaviest.weight > 0 else Decimal('0')
    )
    grades_2 = {_component_key(c): MAX_GRADE for c in rest}
    grades_2[_component_key(heaviest)] = _clamp(required_heaviest)
    scenarios.append(_scenario_result(
        key='cushion_on_heaviest',
        label='Colchón en el componente de mayor peso',
        grades=grades_2,
        pending_components=pending,
        known_points=known_points,
    ))

    points_heaviest_at_max = _weighted_points(MAX_GRADE, heaviest.weight)
    required_rest = (
        ((remaining_needed - points_heaviest_at_max) * Decimal('100')) / rest_weight
        if rest_weight > 0 else Decimal('0')
    )
    grades_3 = {_component_key(c): _clamp(required_rest) for c in rest}
    grades_3[_component_key(heaviest)] = MAX_GRADE
    scenarios.append(_scenario_result(
        key='cushion_on_the_rest',
        label='Colchón en los demás componentes',
        grades=grades_3,
        pending_components=pending,
        known_points=known_points,
    ))

    historical_average = (
        sum((existing_grades[_component_key(c)] for c in completed), Decimal('0')) / len(completed)
        if completed else Decimal('14')
    )
    points_rest_at_historical = sum(
        (_weighted_points(historical_average, c.weight) for c in rest), Decimal('0'),
    )
    required_heaviest_hist = (
        ((remaining_needed - points_rest_at_historical) * Decimal('100')) / heaviest.weight
        if heaviest.weight > 0 else Decimal('0')
    )
    grades_4 = {_component_key(c): _clamp(historical_average) for c in rest}
    grades_4[_component_key(heaviest)] = _clamp(required_heaviest_hist)
    scenarios.append(_scenario_result(
        key='based_on_history',
        label='Basado en tu historial',
        grades=grades_4,
        pending_components=pending,
        known_points=known_points,
    ))

    if requested_grades:
        pending_keys = {_component_key(c) for c in pending}
        specified = {k: v for k, v in requested_grades.items() if k in pending_keys}
        unspecified = [c for c in pending if _component_key(c) not in specified]

        points_specified = sum(
            (_weighted_points(
                specified[_component_key(c)],
                c.weight,
            ) for c in pending if _component_key(c) in specified),
            Decimal('0'),
        )
        unspecified_weight = sum((c.weight for c in unspecified), Decimal('0'))
        required_unspecified = (
            ((remaining_needed - points_specified) * Decimal('100')) / unspecified_weight
            if unspecified and unspecified_weight > 0 else Decimal('0')
        )
        grades_5 = dict(specified)
        for c in unspecified:
            grades_5[_component_key(c)] = _clamp(required_unspecified)
        scenarios.append(_scenario_result(
            key='custom',
            label='Personalizado',
            grades=grades_5,
            pending_components=pending,
            known_points=known_points,
        ))

    return {'already_complete': False, 'scenarios': scenarios}
