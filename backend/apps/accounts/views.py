from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsPlatformAdmin

from .exceptions import ConflictError
from .models import (
    MembershipRequest,
    SchoolDelegation,
    SchoolMembership,
    StudentProfile,
)
from .serializers import (
    MembershipRequestResolveSerializer,
    MembershipRequestSerializer,
    SchoolDelegationSerializer,
    SchoolMembershipSerializer,
    StudentProfileSerializer,
    StudentProfileWriteSerializer,
)


class StudentProfileViewSet(
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = 'public_id'
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StudentProfile.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            return StudentProfileWriteSerializer
        return StudentProfileSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get', 'post', 'patch'], url_path='me')
    def me(self, request):
        profile = StudentProfile.objects.filter(user=request.user).first()

        if request.method == 'GET':
            if profile is None:
                raise NotFound('Todavía no tienes un perfil de estudiante.')
            return Response(StudentProfileSerializer(profile).data)

        if request.method == 'POST':
            if profile is not None:
                raise ConflictError('Tu perfil ya existe. Usa PATCH para actualizarlo.')

            serializer = StudentProfileWriteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(
                StudentProfileSerializer(serializer.instance).data, status=status.HTTP_201_CREATED
            )

        if request.method == 'PATCH':
            if profile is None:
                raise NotFound(
                    'No puedes actualizar porque aún no tienes perfil. Usa POST para crearlo.'
                )

            serializer = StudentProfileWriteSerializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(StudentProfileSerializer(serializer.instance).data)


class SchoolMembershipViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = SchoolMembershipSerializer
    lookup_field = 'public_id'
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = SchoolMembership.objects.select_related(
            'student__user',
            'school',
            'curriculum_plan',
            'verified_by',
        ).order_by('-created_at')
        if user.is_platform_admin:
            return qs
        if hasattr(user, 'student_profile'):
            return qs.filter(student=user.student_profile)
        return qs.none()


class MembershipRequestViewSet(viewsets.ModelViewSet):
    serializer_class = MembershipRequestSerializer
    lookup_field = 'public_id'
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        qs = MembershipRequest.objects.select_related(
            'student__user',
            'school',
            'curriculum_plan',
            'resolved_by',
        ).order_by('-created_at')
        if user.is_platform_admin:
            return qs

        delegated_schools = SchoolDelegation.objects.filter(
            delegate=user,
            is_active=True,
        ).values_list('school_id', flat=True)

        if hasattr(user, 'student_profile'):
            return qs.filter(
                Q(student=user.student_profile) | Q(school_id__in=delegated_schools),
            )
        return qs.filter(school_id__in=delegated_schools)

    def perform_create(self, serializer):
        if not hasattr(self.request.user, 'student_profile'):
            raise serializers.ValidationError(
                'Necesitas registrar tu perfil de estudiante (CUI) antes '
                'de solicitar una membresía. Usa /student-profiles/me/.',
            )
        serializer.save()

    def _can_resolve(self, request, membership_request):
        if request.user.is_platform_admin:
            return True
        return SchoolDelegation.objects.filter(
            delegate=request.user,
            school=membership_request.school,
            is_active=True,
        ).exists()

    @action(detail=True, methods=['post'])
    def approve(self, request, public_id=None):
        return self._resolve(request, MembershipRequest.Status.APPROVED)

    @action(detail=True, methods=['post'])
    def reject(self, request, public_id=None):
        return self._resolve(request, MembershipRequest.Status.REJECTED)

    def _resolve(self, request, new_status):
        membership_request = self.get_object()

        if not self._can_resolve(request, membership_request):
            self.permission_denied(request)

        body = MembershipRequestResolveSerializer(data=request.data)
        body.is_valid(raise_exception=True)

        with transaction.atomic():
            updated = MembershipRequest.objects.filter(
                pk=membership_request.pk,
                status=MembershipRequest.Status.PENDING,
            ).update(
                status=new_status,
                resolved_by=request.user,
                resolved_at=timezone.now(),
                resolution_comment=body.validated_data['resolution_comment'],
            )
            if updated == 0:
                membership_request.refresh_from_db()
                raise ConflictError(
                    'Esta solicitud ya fue resuelta '
                    f'({membership_request.get_status_display()}) — no se '
                    'puede volver a procesar.',
                )

            if new_status == MembershipRequest.Status.APPROVED:
                SchoolMembership.objects.get_or_create(
                    student=membership_request.student,
                    school=membership_request.school,
                    defaults={
                        'curriculum_plan': membership_request.curriculum_plan,
                        'verified_by': request.user,
                        'verified_at': timezone.now(),
                    },
                )

        membership_request.refresh_from_db()
        return Response(MembershipRequestSerializer(membership_request).data)


class SchoolDelegationViewSet(viewsets.ModelViewSet):
    serializer_class = SchoolDelegationSerializer
    lookup_field = 'public_id'
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.action in ('create', 'destroy'):
            return [IsPlatformAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = SchoolDelegation.objects.select_related(
            'delegate',
            'school',
            'assigned_by',
        ).order_by('-created_at')
        if user.is_platform_admin:
            return qs
        return qs.filter(delegate=user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
