from rest_framework import serializers

from .models import User


class CurrentUserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(
        source='public_id',
        read_only=True,
    )

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
        ]
        read_only_fields = fields


class CSRFDataSerializer(serializers.Serializer):
    csrf_cookie_set = serializers.BooleanField()


class LogoutDataSerializer(serializers.Serializer):
    authenticated = serializers.BooleanField()
