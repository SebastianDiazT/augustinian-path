from apps.core.permissions import IsOwnerStudent
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PublicShareLink, ScheduleAlternative, ScheduleSimulation
from .serializers import (
    GenerateSimulationSerializer,
    PublicScheduleViewSerializer,
    PublicShareLinkSerializer,
    ScheduleAlternativeSerializer,
    ScheduleSimulationSerializer,
)
from .services import run_simulation


class _IsOwnerOrPlatformAdmin(IsOwnerStudent):
    def has_object_permission(self, request, view, obj):
        if request.user.is_platform_admin:
            return True
        return super().has_object_permission(request, view, obj)


class _IsSimulationOwnerOrAdmin(BasePermission):
    """Like IsOwnerStudent, but for objects one level removed from
    `student` (ScheduleAlternative -> simulation -> student)."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.is_platform_admin:
            return True
        return obj.simulation.student.user_id == request.user.id


_ALTERNATIVE_PREFETCH = (
    'alternatives__sections__section__offering__course',
    'alternatives__sections__section__instructor',
    'alternatives__sections__section__meetings__time_block',
)


class ScheduleSimulationViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet,
):
    """Read-only through the standard routes: simulations are created
    via the `generate` action, not a plain POST — running the generator
    needs more orchestration than a ModelSerializer.create() expresses
    (validation, the algorithm itself, possibly two variants)."""

    serializer_class = ScheduleSimulationSerializer
    lookup_field = 'public_id'
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = ScheduleSimulation.objects.select_related('academic_term').prefetch_related(
            *_ALTERNATIVE_PREFETCH, 'offerings__course',
        )
        if user.is_platform_admin:
            return qs
        if hasattr(user, 'student_profile'):
            return qs.filter(student=user.student_profile)
        return qs.none()

    def get_permissions(self):
        if self.action == 'retrieve':
            return [IsAuthenticated(), _IsOwnerOrPlatformAdmin()]
        return [IsAuthenticated()]

    @extend_schema(
        request=GenerateSimulationSerializer,
        responses=ScheduleSimulationSerializer(many=True),
    )
    @action(detail=False, methods=['post'])
    def generate(self, request):
        if not hasattr(request.user, 'student_profile'):
            return Response(
                {'detail': 'Necesitas registrar tu perfil de estudiante primero.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        input_serializer = GenerateSimulationSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data

        simulations = run_simulation(
            student=request.user.student_profile,
            academic_term=data['academic_term'],
            offering_ids=[offering.id for offering in data['offerings']],
            excluded_section_ids=data.get('excluded_sections', []),
            excluded_instructor_ids=data.get('excluded_instructors', []),
            preferences=data.get('preferences', {}),
        )

        serialized = ScheduleSimulationSerializer(simulations, many=True)
        return Response(serialized.data, status=status.HTTP_201_CREATED)


class ScheduleAlternativeViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ScheduleAlternativeSerializer
    lookup_field = 'public_id'
    permission_classes = [IsAuthenticated, _IsSimulationOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        qs = ScheduleAlternative.objects.select_related(
            'simulation__student__user',
        ).prefetch_related(
            'sections__section__offering__course',
            'sections__section__instructor',
            'sections__section__meetings__time_block',
        )
        if user.is_platform_admin:
            return qs
        if hasattr(user, 'student_profile'):
            return qs.filter(simulation__student=user.student_profile)
        return qs.none()

    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, public_id=None):
        alternative = self.get_object()
        alternative.is_favorite = not alternative.is_favorite
        alternative.save(update_fields=['is_favorite'])
        return Response(ScheduleAlternativeSerializer(alternative).data)


class PublicShareLinkViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Create/list/revoke a share link — all owner-only. Reading the
    actual shared schedule (no authentication) is a separate view, see
    PublicScheduleView below."""

    serializer_class = PublicShareLinkSerializer
    lookup_field = 'public_id'
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = PublicShareLink.objects.select_related('alternative__simulation__student')
        if user.is_platform_admin:
            return qs
        if hasattr(user, 'student_profile'):
            return qs.filter(alternative__simulation__student=user.student_profile)
        return qs.none()

    def perform_create(self, serializer):
        alternative = serializer.validated_data['alternative']
        is_owner = alternative.simulation.student.user_id == self.request.user.id
        if not (is_owner or self.request.user.is_platform_admin):
            self.permission_denied(self.request)
        serializer.save()

    def perform_destroy(self, instance):
        # "Dejar de compartir": revoke instead of hard-deleting, so the
        # link keeps existing for history but stops resolving publicly.
        instance.is_active = False
        instance.save(update_fields=['is_active'])


class PublicScheduleView(APIView):
    """The actual public page: read-only, no authentication, never
    expires — only `is_active=False` (revoked) stops it from working."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, public_id=None):
        link = PublicShareLink.objects.filter(
            public_id=public_id, is_active=True,
        ).select_related(
            'alternative__simulation__student__user',
        ).prefetch_related(
            'alternative__sections__section__offering__course',
            'alternative__sections__section__instructor',
            'alternative__sections__section__meetings__time_block',
        ).first()

        if link is None:
            return Response(
                {'detail': 'Este enlace no existe o ya no está disponible.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(PublicScheduleViewSerializer(link).data)
