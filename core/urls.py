from django.urls import path, include
from  . import views
from rest_framework import routers
from api.views import TestViewSet, SessionViewSet

router=routers.DefaultRouter()
router.register(r'tests', TestViewSet)
router.register(r'sessons', SessionViewSet, basename='session')


urlpatterns = [
    path('', views.test_list, name='test_list'),
    path('test/<int:test_id>/', views.start_test, name='start_test'),
    path('submit_response/', views.submit_response, name='submit_response'),
    path('result/<int:session_id>/', views.result, name='result'),
    path('test/', views.take_test, name='take_test'),
    
    path('result/', views.result, name='result'),
    path('chat/', views.ai_chat, name='ai_chat'),
    path('', include(router.urls)),
    ]

