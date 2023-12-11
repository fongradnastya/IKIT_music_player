from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='home'),
    path('get-username', views.get_home_data, name='get-username'),
    path("login", views.login, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout, name="logout"),
    path("get-public-key", views.get_public_key, name="get-public-key"),
    path("receive-public-key", views.receive_public_key,
         name="receive-public-key"),
    path("receive-registration", views.receive_registration_data,
         name="receive-registration"),
    path("receive-login", views.receive_login_data, name="receive-login"),
]