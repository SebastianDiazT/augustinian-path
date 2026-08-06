from decimal import Decimal

from django.db import IntegrityError, transaction
from rest_framework import serializers

from apps.academics.models import CourseOffering
from apps.academics.serializers import SchoolScopedWriteSerializerMixin

from .models import EvaluationComponent, EvaluationScheme


class EvaluationComponentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(
        source='public_id',
        read_only=True,
    )
    component_type_label = serializers.CharField(
        source='get_component_type_display',
        read_only=True,
    )

    class Meta:
        model = EvaluationComponent
        fields = [
            'id',
            'name',
            'component_type',
            'component_type_label',
            'weight',
            'order',
        ]
        read_only_fields = fields


class EvaluationSchemeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(
        source='public_id',
        read_only=True,
    )
    course_offering_id = serializers.UUIDField(
        source='course_offering.public_id',
        read_only=True,
    )
    academic_period_code = serializers.CharField(
        source='course_offering.academic_period.code',
        read_only=True,
    )
    course_code = serializers.CharField(
        source='course_offering.course.code',
        read_only=True,
    )
    course_name = serializers.CharField(
        source='course_offering.course.name',
        read_only=True,
    )
    components = EvaluationComponentSerializer(
        many=True,
        read_only=True,
    )
    total_weight = serializers.SerializerMethodField()

    class Meta:
        model = EvaluationScheme
        fields = [
            'id',
            'course_offering_id',
            'academic_period_code',
            'course_code',
            'course_name',
            'passing_grade',
            'total_weight',
            'components',
        ]
        read_only_fields = fields

    def get_total_weight(self, obj: EvaluationScheme) -> str:
        total = sum(
            (
                component.weight
                for component in obj.components.all()
                if component.component_type
                != EvaluationComponent.ComponentType.SUBSTITUTE
            ),
            start=Decimal('0.00'),
        )
        return f'{total:.2f}'


class EvaluationSchemeWriteSerializer(
    SchoolScopedWriteSerializerMixin,
    serializers.ModelSerializer,
):
    school_scoped_fields = {
        'course_offering_id': 'course__professional_school_id',
    }
    course_offering_id = serializers.SlugRelatedField(
        source='course_offering',
        slug_field='public_id',
        queryset=CourseOffering.objects.all(),
        write_only=True,
    )

    class Meta:
        model = EvaluationScheme
        fields = [
            'course_offering_id',
        ]
        validators = []

    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        offering = attrs.get('course_offering')

        if self.instance is not None:
            if offering is not None and offering.pk != self.instance.course_offering_id:
                raise serializers.ValidationError(
                    {
                        'course_offering_id': (
                            'No se puede cambiar la oferta de un esquema existente.'
                        ),
                    }
                )

            return attrs

        if (
            isinstance(offering, CourseOffering)
            and EvaluationScheme.objects.filter(
                course_offering=offering,
            ).exists()
        ):
            raise serializers.ValidationError(
                {
                    'course_offering_id': (
                        'La oferta ya tiene un esquema de evaluación.'
                    ),
                }
            )

        return attrs

    def create(self, validated_data: dict[str, object]) -> EvaluationScheme:
        try:
            with transaction.atomic():
                return super().create(validated_data)
        except IntegrityError as error:
            raise serializers.ValidationError(
                {
                    'course_offering_id': (
                        'La oferta ya tiene un esquema de evaluación.'
                    ),
                }
            ) from error


class EvaluationComponentWriteSerializer(
    SchoolScopedWriteSerializerMixin,
    serializers.ModelSerializer,
):
    school_scoped_fields = {
        'scheme_id': 'course_offering__course__professional_school_id',
    }
    scheme_id = serializers.SlugRelatedField(
        source='scheme',
        slug_field='public_id',
        queryset=EvaluationScheme.objects.all(),
        write_only=True,
    )

    class Meta:
        model = EvaluationComponent
        fields = [
            'scheme_id',
            'name',
            'component_type',
            'weight',
            'order',
        ]
        validators = []
        extra_kwargs = {
            'order': {
                'required': False,
            },
        }

    def validate_name(self, value: str) -> str:
        normalized_name = ' '.join(value.split())

        if not normalized_name:
            raise serializers.ValidationError(
                'El nombre del componente es obligatorio.'
            )

        return normalized_name

    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        if self.partial and not attrs:
            raise serializers.ValidationError('Debes proporcionar al menos un campo.')

        scheme = attrs.get('scheme')
        name = attrs.get('name')
        component_type = attrs.get('component_type')
        weight = attrs.get('weight')

        if self.instance is not None:
            if (
                isinstance(scheme, EvaluationScheme)
                and scheme.pk != self.instance.scheme_id
            ):
                raise serializers.ValidationError(
                    {
                        'scheme_id': (
                            'No se puede cambiar el esquema de un componente existente.'
                        ),
                    }
                )

            if (
                isinstance(component_type, str)
                and component_type != self.instance.component_type
            ):
                raise serializers.ValidationError(
                    {
                        'component_type': (
                            'No se puede cambiar el tipo de un componente existente.'
                        ),
                    }
                )

            scheme = self.instance.scheme
            name = name or self.instance.name
            component_type = self.instance.component_type
            weight = weight if weight is not None else self.instance.weight

        if (
            component_type == EvaluationComponent.ComponentType.SUBSTITUTE
            and weight != 0
        ):
            raise serializers.ValidationError(
                {
                    'weight': ('El sustitutorio debe tener peso 0.'),
                }
            )

        if (
            isinstance(component_type, str)
            and component_type != EvaluationComponent.ComponentType.SUBSTITUTE
            and weight is not None
            and weight <= 0
        ):
            raise serializers.ValidationError(
                {
                    'weight': ('Un componente evaluativo debe tener peso positivo.'),
                }
            )

        if isinstance(scheme, EvaluationScheme) and isinstance(name, str):
            same_name = EvaluationComponent.objects.filter(
                scheme=scheme,
                name__iexact=name,
            )

            if self.instance is not None:
                same_name = same_name.exclude(pk=self.instance.pk)

            if same_name.exists():
                raise serializers.ValidationError(
                    {
                        'name': ('Ya existe un componente con este nombre.'),
                    }
                )

        if (
            isinstance(scheme, EvaluationScheme)
            and isinstance(component_type, str)
            and component_type != EvaluationComponent.ComponentType.OTHER
        ):
            same_type = EvaluationComponent.objects.filter(
                scheme=scheme,
                component_type=component_type,
            )

            if self.instance is not None:
                same_type = same_type.exclude(pk=self.instance.pk)

            if same_type.exists():
                raise serializers.ValidationError(
                    {
                        'component_type': (
                            'El esquema ya tiene un componente de este tipo.'
                        ),
                    }
                )

        return attrs

    def create(self, validated_data: dict[str, object]) -> EvaluationComponent:
        try:
            with transaction.atomic():
                return super().create(validated_data)
        except IntegrityError as error:
            raise serializers.ValidationError(
                'El componente entra en conflicto con el esquema.'
            ) from error


class GradeInputSerializer(serializers.Serializer):
    component_id = serializers.UUIDField()
    score = serializers.DecimalField(
        max_digits=4,
        decimal_places=2,
        min_value=Decimal('0.00'),
        max_value=EvaluationScheme.MAXIMUM_GRADE,
    )


class GradeSimulationRequestSerializer(serializers.Serializer):
    grades = GradeInputSerializer(
        many=True,
        required=False,
        default=list,
    )

    def validate_grades(
        self,
        value: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        component_ids = [grade['component_id'] for grade in value]

        if len(component_ids) != len(set(component_ids)):
            raise serializers.ValidationError(
                'No se puede enviar más de una nota por componente.'
            )

        return value
