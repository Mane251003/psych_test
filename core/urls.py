from django.urls import path
from  . import views
urlpatterns = [
    path('test/', views.take_test, name='take_test'),
    path('result/', views.result, name='result'),
    path('chat/', views.ai_chat, name='ai_chat'),]

