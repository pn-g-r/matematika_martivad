from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("staff-register/", views.staff_register_view, name="staff_register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]

