from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, PredictionViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'predictions', PredictionViewSet, basename='prediction')

urlpatterns = [
    path('', include(router.urls)),
]
