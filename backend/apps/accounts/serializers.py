from rest_framework import serializers

from apps.academics.models import ProfessionalSchool

from .models import User


class CurrentUserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(
        source='public_id',
        read_only=True,
    )
    avatar_url = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'avatar_url',
            'roles',
        ]
        read_only_fields = fields

    def get_avatar_url(self, user: User) -> str | None:
        return user.avatar_url or None

    def get_roles(self, user: User) -> list[str]:
        return list(
            user.groups.order_by('name').values_list(
                'name',
                flat=True,
            )
        )


class GoogleLoginRequestSerializer(serializers.Serializer):
    credential = serializers.CharField(
        write_only=True,
        allow_blank=False,
        trim_whitespace=True,
    )


class GoogleLoginDataSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = CurrentUserSerializer()
    is_new_user = serializers.BooleanField()


class RefreshTokenRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        write_only=True,
        allow_blank=False,
        trim_whitespace=True,
    )


class RefreshTokenDataSerializer(serializers.Serializer):
    access = serializers.CharField(
        read_only=True,
    )
    refresh = serializers.CharField(
        read_only=True,
    )


class CSRFDataSerializer(serializers.Serializer):
    csrf_cookie_set = serializers.BooleanField()


class LogoutDataSerializer(serializers.Serializer):
    authenticated = serializers.BooleanField()


class PlatformAdminAccessDataSerializer(serializers.Serializer):
    authorized = serializers.BooleanField()


class AcademicAdminSchoolSerializer(
    serializers.ModelSerializer,
):
    id = serializers.UUIDField(
        source='public_id',
        read_only=True,
    )

    class Meta:
        model = ProfessionalSchool
        fields = [
            'id',
            'name',
        ]
        read_only_fields = fields


class AcademicAdminAssignmentWriteSerializer(
    serializers.Serializer,
):
    professional_school_id = serializers.UUIDField()


class PlatformAdminUserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(
        source='public_id',
        read_only=True,
    )
    roles = serializers.SerializerMethodField()
    academic_admin_school = AcademicAdminSchoolSerializer(
        source='academic_admin_assignment.professional_school',
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'roles',
            'academic_admin_school',
        ]
        read_only_fields = fields

    def get_roles(self, user: User) -> list[str]:
        prefetched_roles = getattr(
            user,
            'ordered_roles',
            None,
        )

        if prefetched_roles is not None:
            return [role.name for role in prefetched_roles]

        return list(
            user.groups.order_by('name').values_list(
                'name',
                flat=True,
            )
        )


class PlatformAdminUserPaginationSerializer(
    serializers.Serializer,
):
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_items = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    has_next = serializers.BooleanField()
    has_previous = serializers.BooleanField()


class PlatformAdminUserListDataSerializer(
    serializers.Serializer,
):
    users = PlatformAdminUserSerializer(many=True)
    pagination = PlatformAdminUserPaginationSerializer()
