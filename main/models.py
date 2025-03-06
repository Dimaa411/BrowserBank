from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class User(AbstractUser):
    email = models.EmailField(
        validators=[RegexValidator(
            regex=r'^[a-zA-Z0-9._%+-]+@gmail\.com$',
            message="Введіть email з домену @gmail.com",
            code="invalid_email"
        )]
    )
