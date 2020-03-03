from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("get-invite", views.invite, name="invite"),
    path("state/<str:connection_id>", views.state, name="state"),
    path("submit-name/<str:connection_id>", views.submit_name, name="submit_name"),
    path("in-progress/<str:connection_id>", views.in_progress, name="in_progress"),
    path("backend", views.backend, name="backend"),
    # path("backend/denied", views.backend_denied, name="backend_denied"),
    # path("backend/approved", views.backend_approved, name="backend_approved"),
    # path("attendees/submit", views.attendees_submit, name="attendees_submit"),
    path("webhooks/topic/<str:topic>/", views.webhooks, name="webhooks"),
]
