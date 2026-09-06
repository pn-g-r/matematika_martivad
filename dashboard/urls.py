from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.student_list_view, name='students'),
    path('students/<int:user_id>/grant-access/', views.grant_access_view, name='grant_access'),
]
