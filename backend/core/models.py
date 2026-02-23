from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ADMIN = 'admin'
    ANALYST = 'analyst'
    CLIENT = 'client'

    ROLE_CHOICES = (
        (ADMIN, 'Administrator'),
        (ANALYST, 'Analist financiar'),
        (CLIENT, 'Client (firma)'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=CLIENT
    )

    def __str__(self):
        return f"{self.username}({self.get_role_display()})"