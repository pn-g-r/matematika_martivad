from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("staff-register/", views.staff_register_view, name="staff_register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("password-reset/", views.password_reset_request_view, name="password_reset"),
    path("password-reset/verify/", views.password_reset_verify_view, name="password_reset_verify"),
    path("password-reset/resend/", views.password_reset_resend_view, name="password_reset_resend"),
    path("password-reset/confirm/", views.password_reset_confirm_view, name="password_reset_confirm"),
]

