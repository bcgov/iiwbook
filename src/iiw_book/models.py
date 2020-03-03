from django.db import models


class Attendee(models.Model):
    connection_id = models.UUIDField()
    email = models.EmailField(unique=True)
    full_name = models.TextField(default=None, blank=True, null=True)
    conference = models.TextField(default=None, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


class SessionState(models.Model):
    connection_id = models.UUIDField()
    state = models.TextField()
