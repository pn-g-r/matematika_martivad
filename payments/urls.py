from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('pricing/', views.pricing_view, name='pricing'),
    path('checkout/<str:plan_type>/', views.checkout_init_view, name='checkout_init'),
    path('pay/<str:order_id>/', views.checkout_pay_view, name='checkout_pay'),
    path('callback/', views.flitt_callback_view, name='flitt_callback'),
    path('response/', views.payment_response_view, name='payment_response'),
]
