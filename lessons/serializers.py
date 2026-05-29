from rest_framework import serializers
from .models import LessonPlan

class LessonPlanSerializer(serializers.ModelSerializer):
    teacher = serializers.ReadOnlyField(source='teacher.name')

    class Meta:
        model = LessonPlan
        fields = '__all__'
        read_only_fields = ('teacher',)
