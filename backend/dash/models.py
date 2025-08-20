from django.db import models

class AlertSwitch(models.Model):
    enabled = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)