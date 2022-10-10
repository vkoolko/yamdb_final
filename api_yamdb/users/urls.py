from django.urls import path

from users import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('token/', views.get_token, name='token'),
]
