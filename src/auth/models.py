from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Meta:
        db_table = "auth_user"
        permissions = [
            ("change_is_active", "Can change a user's active status"),
            ("change_is_contrib", "Can change a user's contributor status"),
            ("change_is_staff", "Can change a user's staff status"),
        ]

    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    email = models.EmailField(verbose_name="email address", max_length=255, unique=True)
    is_contributor = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into the contributor-facing site.",
    )
