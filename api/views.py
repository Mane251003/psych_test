from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import PsychoTest, TestSession
from core.models import Response as UserResponse
from core.serializers import TestSerializer, SessionSerializer


class TestViewSet(viewsets.ModelViewSet):
    queryset=PsychoTest.objects.filter(is_active=True)
    serializer_class=TestSerializer
    permission_classes=[permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def start_session(self, request, pk=None):
        test=self.get_object()
        session=TestSession.objects.create(
            candidate=request.user,
            test=test
        )
        return Response({
            'session_id': session.id,
            'questions': [
                {
                    'id': q.id,
                    'text': q.text,
                    'options': [
                        {'id': o.id, 'text': o.text}
                        for o in q.options.all()
                    ]
                }
                for q in test.questions.all().order_by('order')
            ]
        })
    
class SessionViewSet(viewsets.ModelViewSet):
    queryset=TestSession.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TestSession.objects.filter(candidate=self.request.user)

    @action(detail=True, methods=['post'])
    def submit_response(self, request, pk=None):
        session = self.get_object()
        if session.is_completed:
            return Response({'error': 'Session already completed'}, status=400)
        
        # Validate and save responses
        # Add proper validation and error handling
        Response.objects.create(
            session=session,
            question_id=request.data['question_id'],
            answer_id=request.data['answer_id']
        )
        return Response({'status': 'response recorded'})