from django.urls import path, include

from auth_service.views import *

urlpatterns = [
    path('api/auth/', include([
        path('login/', LoginView.as_view()),
        path('signup/', SignUpView.as_view()),
        path('logout/', LogoutView.as_view()),

        path('otp/', OTPView.as_view()),

        path('token/', TokenView.as_view()),

        path('oauth/', OAuthView.as_view()),
        path('oauth/callback/', OAuthCallbackView.as_view())
    ]))
]
