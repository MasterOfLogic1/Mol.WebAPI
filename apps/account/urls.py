from django.urls import path
from .views import register_view,MyTokenObtainPairView,send_verification_email_view,reset_password_view,send_password_reset_email_view,verify_account_view,logout_view,account_status_view,change_password_view

urlpatterns = [
    path('auth/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/register/', register_view, name='register'),
    path('account-status/', account_status_view, name='account-status'),
    path("send-verification-email/", send_verification_email_view, name="send-verification-email"),
    path("verify/<str:verification_token>/", verify_account_view, name="verify-account"),
    path("send-password-reset-email/", send_password_reset_email_view, name="send-password-reset-email"),
    path("reset-password/<str:reset_token>/", reset_password_view, name="reset-password"),
    path("auth/logout/", logout_view, name="logout"),
    path('user/change-password/', change_password_view, name='change-password'),
]

