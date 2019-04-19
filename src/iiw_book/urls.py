from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("get-invite", views.invite, name="invite"),
    path("webhooks/topic/<str:topic>/", views.webhooks, name="webhooks"),
]
