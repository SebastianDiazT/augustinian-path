from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsPlatformAdmin, IsSchoolDelegate

from .models import Area, Faculty, ProfessionalSchool
from .serializers import AreaSerializer, FacultySerializer, ProfessionalSchoolSerializer


class AreaViewSet(viewsets.ModelViewSet):
    queryset = Area.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = AreaSerializer
    lookup_field = 'public_id'

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsPlatformAdmin()]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.faculties.filter(is_active=True).exists():
            raise ValidationError(
                {
                    'detail': (
                        'No puedes desactivar esta área porque '
                        'tiene facultades activas relacionadas.'
                    )
                }
            )

        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FacultyViewSet(viewsets.ModelViewSet):
    queryset = Faculty.objects.filter(is_active=True).select_related('area').order_by('-created_at')
    serializer_class = FacultySerializer
    lookup_field = 'public_id'

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsPlatformAdmin()]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.professional_schools.filter(is_active=True).exists():
            raise ValidationError(
                {
                    'detail': (
                        'No puedes desactivar esta facultad porque '
                        'tiene escuelas profesionales activas relacionadas.'
                    )
                }
            )

        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfessionalSchoolViewSet(viewsets.ModelViewSet):
    queryset = (
        ProfessionalSchool.objects.filter(is_active=True)
        .select_related('faculty')
        .order_by('-created_at')
    )
    serializer_class = ProfessionalSchoolSerializer
    lookup_field = 'public_id'

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        if self.action in ('update', 'partial_update'):
            return [IsAuthenticated(), _IsAdminOrDelegateOfThisSchool()]
        return [IsPlatformAdmin()]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class _IsAdminOrDelegateOfThisSchool(IsSchoolDelegate):
    def has_object_permission(self, request, view, obj):
        if request.user.is_platform_admin:
            return True
        return super().has_object_permission(request, view, obj)
