from django.db import models


class Attendee(models.Model):
    connection_id = models.UUIDField()
    approved = models.BooleanField(default=False)
    denied = models.BooleanField(default=False)
    email = models.EmailField(unique=True)
    full_name = models.TextField(default=None, blank=True, null=True)
