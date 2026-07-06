from django.urls import path

from .views import LoginView, RefreshTokenView, RegisterView

urlpatterns = [
    path("login/", LoginView.as_view(), name="auth-login"),
    path("refresh/", RefreshTokenView.as_view(), name="auth-refresh"),
    path("register/", RegisterView.as_view(), name="auth-register"),
]
