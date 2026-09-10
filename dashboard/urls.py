from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.student_list_view, name='students'),
    path('students/<int:user_id>/grant-access/', views.grant_access_view, name='grant_access'),
    path('students/<int:user_id>/comments/', views.add_student_comment_view, name='add_comment'),
    path(
        'students/<int:user_id>/comments/<int:comment_id>/delete/',
        views.delete_student_comment_view,
        name='delete_comment',
    ),
]
