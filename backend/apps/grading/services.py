from decimal import ROUND_CEILING, ROUND_HALF_UP, Decimal

from .models import EvaluationComponent, EvaluationScheme

TWO_DECIMAL_PLACES = Decimal('0.01')
ONE_HUNDRED = Decimal('100.00')
ZERO = Decimal('0.00')


class GradeSimulationError(ValueError):
    pass


def _rounded(value: Decimal) -> Decimal:
    return value.quantize(
        TWO_DECIMAL_PLACES,
        rounding=ROUND_HALF_UP,
    )


def _serialized(value: Decimal) -> str:
    return f'{_rounded(value):.2f}'


def simulate_grades(
    scheme: EvaluationScheme,
    scores: dict[int, Decimal],
) -> dict[str, object]:
    components = list(scheme.components.all())
    components_by_id = {component.pk: component for component in components}
    unknown_ids = set(scores) - set(components_by_id)

    if unknown_ids:
        raise GradeSimulationError(
            'Todas las notas deben pertenecer al esquema seleccionado.'
        )

    if any(
        score < ZERO or score > scheme.MAXIMUM_GRADE for score in scores.values()
    ):
        raise GradeSimulationError('Las notas deben estar entre 0.00 y 20.00.')

    substitute = next(
        (
            component
            for component in components
            if component.component_type
            == EvaluationComponent.ComponentType.SUBSTITUTE
        ),
        None,
    )
    base_components = [
        component
        for component in components
        if component.component_type
        != EvaluationComponent.ComponentType.SUBSTITUTE
    ]
    total_weight = sum(
        (component.weight for component in base_components),
        start=ZERO,
    )

    if total_weight != ONE_HUNDRED:
        raise GradeSimulationError(
            'Los componentes ponderados del esquema deben sumar 100.00%.'
        )

    special_components = {
        component.component_type: component
        for component in components
        if component.component_type
        != EvaluationComponent.ComponentType.OTHER
    }

    if substitute is not None and (
        EvaluationComponent.ComponentType.EXAM_1 not in special_components
        or EvaluationComponent.ComponentType.EXAM_2 not in special_components
    ):
        raise GradeSimulationError(
            'Un esquema con sustitutorio debe incluir Examen 1 y Examen 2.'
        )

    effective_scores = dict(scores)
    substitution = None

    if substitute is not None and substitute.pk in scores:
        exam_1 = special_components[EvaluationComponent.ComponentType.EXAM_1]
        exam_2 = special_components[EvaluationComponent.ComponentType.EXAM_2]

        if exam_1.pk not in scores or exam_2.pk not in scores:
            raise GradeSimulationError(
                'El sustitutorio requiere notas para Examen 1 y Examen 2.'
            )

        replaced_exam = exam_1 if scores[exam_1.pk] <= scores[exam_2.pk] else exam_2
        effective_scores[replaced_exam.pk] = scores[substitute.pk]
        substitution = {
            'component_id': str(substitute.public_id),
            'score': _serialized(scores[substitute.pk]),
            'replaced_component_id': str(replaced_exam.public_id),
            'replaced_component_name': replaced_exam.name,
            'original_score': _serialized(scores[replaced_exam.pk]),
            'effective_score': _serialized(scores[substitute.pk]),
        }

    weighted_total = sum(
        (
            effective_scores[component.pk] * component.weight / ONE_HUNDRED
            for component in base_components
            if component.pk in effective_scores
        ),
        start=ZERO,
    )
    final_average = _rounded(weighted_total)
    points_missing = max(
        scheme.passing_grade - final_average,
        ZERO,
    )
    used_percentage = sum(
        (
            component.weight
            for component in base_components
            if component.pk in scores
        ),
        start=ZERO,
    )
    remaining_percentage = ONE_HUNDRED - used_percentage
    pending_components = []

    for component in base_components:
        if component.pk in scores:
            continue

        required_score = (
            points_missing * ONE_HUNDRED / component.weight
        ).quantize(
            TWO_DECIMAL_PLACES,
            rounding=ROUND_CEILING,
        )
        achievable = required_score <= scheme.MAXIMUM_GRADE

        pending_components.append(
            {
                'component_id': str(component.public_id),
                'name': component.name,
                'weight': _serialized(component.weight),
                'minimum_score': (
                    _serialized(required_score) if achievable else None
                ),
                'achievable': achievable,
            }
        )

    component_results = []

    for component in base_components:
        original_score = scores.get(component.pk)
        effective_score = effective_scores.get(component.pk)
        contribution = (
            effective_score * component.weight / ONE_HUNDRED
            if effective_score is not None
            else ZERO
        )

        component_results.append(
            {
                'component_id': str(component.public_id),
                'name': component.name,
                'component_type': component.component_type,
                'weight': _serialized(component.weight),
                'score': (
                    _serialized(original_score)
                    if original_score is not None
                    else None
                ),
                'effective_score': (
                    _serialized(effective_score)
                    if effective_score is not None
                    else None
                ),
                'contribution': _serialized(contribution),
            }
        )

    return {
        'passing_grade': _serialized(scheme.passing_grade),
        'maximum_grade': _serialized(scheme.MAXIMUM_GRADE),
        'final_average': _serialized(final_average),
        'passed': final_average >= scheme.passing_grade,
        'points_missing': _serialized(points_missing),
        'used_percentage': _serialized(used_percentage),
        'remaining_percentage': _serialized(remaining_percentage),
        'components': component_results,
        'pending_components': pending_components,
        'substitution': substitution,
    }
