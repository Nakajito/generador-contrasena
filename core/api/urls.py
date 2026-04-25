from django.urls import path

from .views import GeneratePasswordView

app_name = "api"

urlpatterns = [
    path("v1/generate", GeneratePasswordView.as_view(), name="generate"),
]
