from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LessonPlanViewSet

router = DefaultRouter()
router.register(r'lesson-plans', LessonPlanViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
