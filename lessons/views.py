from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import LessonPlan
from .serializers import LessonPlanSerializer
from .services import LessonGeneratorService

class LessonPlanViewSet(viewsets.ModelViewSet):
    queryset = LessonPlan.objects.all()
    serializer_class = LessonPlanSerializer

    def get_queryset(self):
        # Only return plans belonging to the authenticated teacher
        return self.queryset.filter(teacher=self.request.user)

    def perform_create(self, serializer):
        # Automatically set the teacher to the authenticated user
        serializer.save(teacher=self.request.user)

    @action(detail=False, methods=['post'])
    def generate(self, request):
        form_data = request.data
        service = LessonGeneratorService()
        
        try:
            generated_plan = service.generate_lesson_plan(form_data)
            return Response(generated_plan, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            print(f"CRITICAL ERROR in LessonPlanViewSet.generate: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"error": "Failed to generate lesson plan", "details": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
