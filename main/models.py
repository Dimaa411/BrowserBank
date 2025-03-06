from django.db import models
from django.core.validators import RegexValidator

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9._%+-]+@gmail\.com$',
                message="Введіть email з домену @gmail.com",
                code="invalid_email"
            )
        ]
    )

    def get_user_name(self):
        return self.name
