from . import views
from django.urls import path


urlpatterns = [
    path("login", views.login, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout, name="logout"),
    path("get-public-key", views.get_public_key, name="get-public-key"),
    path("receive-public-key", views.receive_public_key, name="receive-public-key"),
    path("receive-registration", views.receive_registration_data,
         name="receive-registration"),
]