from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MembershipRequest, SchoolMembership, SupportTicket
from .serializers import (
    MembershipRequestCreateSerializer,
    MembershipRequestSerializer,
    StudentOnboardingSerializer,
    SupportTicketCreateSerializer,
    SupportTicketSerializer,
    UserSerializer,
)


class StudentProfileMeView(APIView):
    """
    GET: Devuelve los datos del estudiante en sesión.
    POST: Registra el CUI por única vez (Onboarding). No se permite PATCH/PUT.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def post(self, request):
        user = request.user

        if user.cui:
            return Response(
                {
                    'detail': 'Tu CUI ya ha sido registrado y no puede ser '
                    'modificado. Si cometiste un error, contacta a soporte.'
                },
                status=status.HTTP_409_CONFLICT,
            )

        serializer = StudentOnboardingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.cui = serializer.validated_data['cui']
        user.save(update_fields=['cui'])

        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


class StudentMembershipRequestView(APIView):
    """
    GET: Lista las solicitudes del estudiante (para saber si está PENDING o REJECTED).
    POST: Crea una nueva solicitud de afiliación a una escuela.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        requests = MembershipRequest.objects.filter(user=request.user)
        return Response(MembershipRequestSerializer(requests, many=True).data)

    def post(self, request):
        user = request.user

        if not user.cui:
            return Response(
                {'detail': 'Debes registrar tu CUI antes de solicitar afiliación a una escuela.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if MembershipRequest.objects.filter(
            user=user, status=MembershipRequest.Status.PENDING
        ).exists():
            return Response(
                {'detail': 'Ya tienes una solicitud en proceso de revisión.'},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = MembershipRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        school = serializer.validated_data['school']
        curriculum_plan = serializer.validated_data['curriculum_plan']

        if SchoolMembership.objects.filter(user=user, school=school).exists():
            return Response(
                {'detail': 'Ya eres miembro oficial de esta escuela.'},
                status=status.HTTP_409_CONFLICT,
            )

        membership_request = MembershipRequest.objects.create(
            user=user,
            school=school,
            curriculum_plan=curriculum_plan,
            status=MembershipRequest.Status.PENDING,
        )

        return Response(
            MembershipRequestSerializer(membership_request).data, status=status.HTTP_201_CREATED
        )


class StudentSupportTicketView(APIView):
    """
    GET: Lista el historial de tickets del estudiante.
    POST: Crea un nuevo ticket de soporte (ej. corrección de CUI).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        tickets = SupportTicket.objects.filter(user=request.user)
        return Response(SupportTicketSerializer(tickets, many=True).data)

    def post(self, request):
        user = request.user

        if SupportTicket.objects.filter(user=user, status=SupportTicket.Status.PENDING).exists():
            return Response(
                {
                    'detail': 'Ya tienes un ticket de soporte en revisión. '
                    'Espera a que sea resuelto antes de abrir otro.'
                },
                status=status.HTTP_409_CONFLICT,
            )

        serializer = SupportTicketCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ticket = SupportTicket.objects.create(
            user=user,
            issue_type=serializer.validated_data['issue_type'],
            message=serializer.validated_data['message'],
            school=serializer.validated_data.get('school_id'),
            status=SupportTicket.Status.PENDING,
        )

        return Response(SupportTicketSerializer(ticket).data, status=status.HTTP_201_CREATED)