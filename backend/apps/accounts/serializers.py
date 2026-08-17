from rest_framework import serializers

from apps.curricula.models import CurriculumPlan
from apps.institution.models import ProfessionalSchool

from .models import MembershipRequest, SupportTicket, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'public_id',
            'email',
            'full_name',
            'picture_url',
            'cui',
            'is_platform_admin',
        ]
        read_only_fields = fields


class StudentOnboardingSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['cui']

    def validate_cui(self, value):
        if not value:
            raise serializers.ValidationError('El CUI es obligatorio.')

        if not value.isdigit() or len(value) != 8:
            raise serializers.ValidationError(
                'El CUI debe contener exactamente 8 dígitos numéricos.'
            )

        return value


class MembershipRequestSerializer(serializers.ModelSerializer):
    """Devuelve el estado de la solicitud al estudiante."""

    school_name = serializers.CharField(source='school.name', read_only=True)
    plan_name = serializers.CharField(source='curriculum_plan.name', read_only=True)

    class Meta:
        model = MembershipRequest
        fields = [
            'public_id',
            'school_name',
            'plan_name',
            'status',
            'resolution_comment',
            'created_at',
        ]
        read_only_fields = fields


class MembershipRequestCreateSerializer(serializers.Serializer):
    """Valida los datos que envía React para crear la solicitud."""

    school_id = serializers.UUIDField()
    curriculum_plan_id = serializers.UUIDField()

    def validate(self, attrs):
        try:
            school = ProfessionalSchool.objects.get(public_id=attrs['school_id'])
            attrs['school'] = school
        except ProfessionalSchool.DoesNotExist as err:
            raise serializers.ValidationError(
                {'school_id': 'La escuela seleccionada no existe.'}
            ) from err

        try:
            plan = CurriculumPlan.objects.get(public_id=attrs['curriculum_plan_id'], school=school)
            attrs['curriculum_plan'] = plan
        except CurriculumPlan.DoesNotExist as err:
            raise serializers.ValidationError(
                {
                    'curriculum_plan_id': (
                        'El plan curricular no existe o no pertenece a esta escuela.'
                    )
                }
            ) from err

        return attrs


class SupportTicketSerializer(serializers.ModelSerializer):
    """Devuelve la lista de tickets y su estado actual al estudiante."""

    school_name = serializers.CharField(source='school.name', read_only=True, allow_null=True)

    class Meta:
        model = SupportTicket
        fields = [
            'public_id',
            'issue_type',
            'message',
            'status',
            'school_name',
            'resolved_at',
            'created_at',
        ]
        read_only_fields = fields


class SupportTicketCreateSerializer(serializers.Serializer):
    """Valida los datos de creación enviados por React."""

    issue_type = serializers.ChoiceField(choices=SupportTicket.IssueType.choices)
    message = serializers.CharField(max_length=1500)
    school_id = serializers.UUIDField(required=False, allow_null=True)

    def validate_school_id(self, value):
        if value:
            try:
                return ProfessionalSchool.objects.get(public_id=value)
            except ProfessionalSchool.DoesNotExist as err:
                raise serializers.ValidationError('La escuela seleccionada no existe.') from err
        return None


class ManagementMembershipRequestSerializer(serializers.ModelSerializer):
    """Serializador rico en datos para que el delegado sepa a quién está aprobando."""

    student_name = serializers.CharField(source='user.full_name', read_only=True)
    student_cui = serializers.CharField(source='user.cui', read_only=True)
    student_email = serializers.EmailField(source='user.email', read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)
    plan_name = serializers.CharField(source='curriculum_plan.name', read_only=True)

    class Meta:
        model = MembershipRequest
        fields = [
            'public_id',
            'student_name',
            'student_cui',
            'student_email',
            'school_name',
            'plan_name',
            'status',
            'created_at',
        ]