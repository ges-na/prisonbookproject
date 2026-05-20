from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Meta:
        db_table = 'auth_user'

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    email = models.EmailField(verbose_name="email address", max_length=255, unique=True)
    is_contributor = models.BooleanField(default=False)
