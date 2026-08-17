from django.db import transaction
from django.utils import timezone
from rest_framework import filters, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdminOrDelegate

from .models import MembershipRequest, SchoolDelegation, SchoolMembership, SupportTicket
from .serializers import (
    ManagementMembershipRequestSerializer,
    SupportTicketSerializer,
)

# =====================================================================
# 1. BANDEJA DE SOLICITUDES DE ONBOARDING (Membership Requests)
# =====================================================================


class DelegateMembershipRequestListView(generics.ListAPIView):
    """GET: Lista las solicitudes. Paginada automáticamente por tu configuración base."""

    serializer_class = ManagementMembershipRequestSerializer
    permission_classes = [IsAdminOrDelegate]

    filter_backends = [filters.SearchFilter]
    search_fields = ['user__cui', 'user__full_name']

    def get_queryset(self):
        user = self.request.user
        queryset = MembershipRequest.objects.select_related('user', 'school', 'curriculum_plan')

        if not user.is_platform_admin:
            delegated_schools = SchoolDelegation.objects.filter(delegate=user).values_list(
                'school', flat=True
            )
            queryset = queryset.filter(school__in=delegated_schools)

        status_param = self.request.query_params.get('status', MembershipRequest.Status.PENDING)
        if status_param.lower() != 'all':
            queryset = queryset.filter(status=status_param)

        return queryset.order_by('created_at')


class DelegateMembershipRequestActionView(APIView):
    """POST: Aprueba o rechaza una solicitud."""

    permission_classes = [IsAdminOrDelegate]

    def post(self, request, public_id):
        user = request.user
        action = request.data.get('action')
        comment = request.data.get('comment', '')

        if action not in ['approve', 'reject']:
            return Response(
                {'detail': "Acción inválida. Usa 'approve' o 'reject'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            membership_req = MembershipRequest.objects.select_related('school', 'user').get(
                public_id=public_id, status=MembershipRequest.Status.PENDING
            )
        except MembershipRequest.DoesNotExist:
            return Response(
                {'detail': 'Solicitud no encontrada o ya fue procesada.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(request, membership_req)

        with transaction.atomic():
            if action == 'approve':
                membership_req.status = MembershipRequest.Status.APPROVED

                SchoolMembership.objects.get_or_create(
                    user=membership_req.user,
                    school=membership_req.school,
                    defaults={
                        'curriculum_plan': membership_req.curriculum_plan,
                        'verified_by': user,
                    },
                )
            elif action == 'reject':
                membership_req.status = MembershipRequest.Status.REJECTED

            membership_req.resolution_comment = comment
            membership_req.resolved_by = user
            membership_req.resolved_at = timezone.now()
            membership_req.save()

        return Response(
            {'detail': f'Solicitud procesada con éxito ({action}).'}, status=status.HTTP_200_OK
        )


# =====================================================================
# 2. BANDEJA DE TICKETS DE SOPORTE (Support Tickets)
# =====================================================================


class DelegateSupportTicketListView(generics.ListAPIView):
    """GET: Lista los tickets de soporte dirigidos a las escuelas del delegado."""

    serializer_class = SupportTicketSerializer
    permission_classes = [IsAdminOrDelegate]

    filter_backends = [filters.SearchFilter]
    search_fields = ['user__cui', 'user__full_name', 'message']

    def get_queryset(self):
        user = self.request.user
        queryset = SupportTicket.objects.select_related('user', 'school')

        if not user.is_platform_admin:
            delegated_schools = SchoolDelegation.objects.filter(delegate=user).values_list(
                'school', flat=True
            )
            queryset = queryset.filter(school__in=delegated_schools)

        status_param = self.request.query_params.get('status', SupportTicket.Status.PENDING)
        if status_param.lower() != 'all':
            queryset = queryset.filter(status=status_param)

        return queryset.order_by('created_at')


class DelegateSupportTicketActionView(APIView):
    """POST: Resuelve o rechaza un ticket de soporte."""

    permission_classes = [IsAdminOrDelegate]

    def post(self, request, public_id):
        user = request.user
        action = request.data.get('action')

        if action not in ['resolve', 'reject']:
            return Response({'detail': 'Acción inválida.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ticket = SupportTicket.objects.select_related('school').get(
                public_id=public_id, status=SupportTicket.Status.PENDING
            )
        except SupportTicket.DoesNotExist:
            return Response(
                {'detail': 'Ticket no encontrado o ya procesado.'}, status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, ticket)

        if action == 'resolve':
            ticket.status = SupportTicket.Status.RESOLVED
        else:
            ticket.status = SupportTicket.Status.REJECTED

        ticket.resolved_by = user
        ticket.resolved_at = timezone.now()
        ticket.save(update_fields=['status', 'resolved_by', 'resolved_at'])

        return Response({'detail': 'Ticket actualizado con éxito.'}, status=status.HTTP_200_OK)
