from rest_framework import serializers

from .models import User


class CurrentUserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(
        source='public_id',
        read_only=True,
    )
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'roles',
        ]
        read_only_fields = fields

    def get_roles(self, user: User) -> list[str]:
        return list(
            user.groups.order_by('name').values_list(
                'name',
                flat=True,
            )
        )


class CSRFDataSerializer(serializers.Serializer):
    csrf_cookie_set = serializers.BooleanField()


class LogoutDataSerializer(serializers.Serializer):
    authenticated = serializers.BooleanField()


class PlatformAdminAccessDataSerializer(serializers.Serializer):
    authorized = serializers.BooleanField()


class PlatformAdminUserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(
        source='public_id',
        read_only=True,
    )
    roles = serializers.SlugRelatedField(
        source='groups',
        many=True,
        read_only=True,
        slug_field='name',
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
        ]
        read_only_fields = fields


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
