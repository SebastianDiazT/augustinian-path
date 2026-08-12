from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from apps.curricula.models import CurriculumPlan
from apps.institution.models import ProfessionalSchool

from .models import (
    MembershipRequest,
    SchoolDelegation,
    SchoolMembership,
    StudentProfile,
    User,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['public_id', 'email', 'full_name', 'is_platform_admin']
        read_only_fields = fields


class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = StudentProfile
        fields = ['public_id', 'user', 'cui', 'created_at', 'updated_at']
        read_only_fields = ['public_id', 'user', 'created_at', 'updated_at']


class StudentProfileWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['cui']


class SchoolMembershipSerializer(serializers.ModelSerializer):
    student = serializers.SlugRelatedField(slug_field='public_id', read_only=True)
    school = serializers.SlugRelatedField(
        slug_field='public_id',
        queryset=ProfessionalSchool.objects.filter(is_active=True),
    )
    curriculum_plan = serializers.SlugRelatedField(
        slug_field='public_id',
        queryset=CurriculumPlan.objects.filter(is_active=True),
    )
    verified_by = serializers.SlugRelatedField(slug_field='public_id', read_only=True)

    class Meta:
        model = SchoolMembership
        fields = [
            'public_id',
            'student',
            'school',
            'curriculum_plan',
            'verified_by',
            'verified_at',
            'is_active',
            'created_at',
        ]
        read_only_fields = fields


class MembershipRequestSerializer(serializers.ModelSerializer):
    student = serializers.SlugRelatedField(slug_field='public_id', read_only=True)
    school = serializers.SlugRelatedField(
        slug_field='public_id',
        queryset=ProfessionalSchool.objects.filter(is_active=True),
    )
    curriculum_plan = serializers.SlugRelatedField(
        slug_field='public_id',
        queryset=CurriculumPlan.objects.filter(is_active=True),
    )
    resolved_by = serializers.SlugRelatedField(slug_field='public_id', read_only=True)

    class Meta:
        model = MembershipRequest
        fields = [
            'public_id',
            'student',
            'school',
            'curriculum_plan',
            'request_type',
            'status',
            'evidence_url',
            'resolution_comment',
            'resolved_by',
            'resolved_at',
            'created_at',
        ]
        read_only_fields = [
            'public_id',
            'student',
            'status',
            'resolution_comment',
            'resolved_by',
            'resolved_at',
            'created_at',
        ]

    def validate(self, attrs):
        request = self.context['request']

        if not hasattr(request.user, 'student_profile'):
            return attrs

        student = request.user.student_profile
        school = attrs.get('school')

        if SchoolMembership.objects.filter(student=student, school=school, is_active=True).exists():
            raise serializers.ValidationError(
                {'school': 'Ya tienes una membresía activa en esta escuela profesional.'}
            )

        if MembershipRequest.objects.filter(
            student=student, school=school, status=MembershipRequest.Status.PENDING
        ).exists():
            raise serializers.ValidationError(
                {'school': 'Ya tienes una solicitud pendiente de revisión para esta escuela.'}
            )

        return attrs

    def create(self, validated_data):
        request = self.context['request']
        validated_data['student'] = request.user.student_profile
        return super().create(validated_data)


class MembershipRequestResolveSerializer(serializers.Serializer):
    """Optional body for the approve/reject actions."""

    resolution_comment = serializers.CharField(
        required=False,
        allow_blank=True,
        default='',
    )


class SchoolDelegationSerializer(serializers.ModelSerializer):
    delegate = serializers.SlugRelatedField(
        slug_field='public_id',
        queryset=User.objects.filter(is_active=True),
    )
    school = serializers.SlugRelatedField(
        slug_field='public_id',
        queryset=ProfessionalSchool.objects.filter(is_active=True),
    )
    assigned_by = serializers.SlugRelatedField(slug_field='public_id', read_only=True)

    class Meta:
        model = SchoolDelegation
        fields = [
            'public_id',
            'delegate',
            'school',
            'assigned_by',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['public_id', 'assigned_by', 'created_at']
        validators = [
            UniqueTogetherValidator(
                queryset=SchoolDelegation.objects.all(),
                fields=['delegate', 'school'],
                message='Este usuario ya ha sido asignado como delegado de esta escuela profesional.',
            )
        ]

    def create(self, validated_data):
        request = self.context['request']
        validated_data['assigned_by'] = request.user
        return super().create(validated_data)
