from rest_framework import viewsets, permissions
from students.models import Student, Prediction
from .serializers import StudentSerializer, PredictionSerializer

class StudentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Multi-tenancy: Only return students created by the current user
        return Student.objects.filter(creator=self.request.user)

    def perform_create(self, serializer):
        # SaaS: Check student limit before allowing creation
        limit = self.request.user.get_student_limit()
        count = Student.objects.filter(creator=self.request.user).count()
        if count >= limit:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(f"Student limit reached for your plan ({limit}). Upgrade to Pro for more.")
        
        serializer.save(creator=self.request.user)

class PredictionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PredictionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Prediction.objects.filter(student__creator=self.request.user)
