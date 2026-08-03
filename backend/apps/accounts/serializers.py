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
