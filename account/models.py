import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Account(models.Model):
    id = models.UUIDField(default=uuid.uuid4,
                          primary_key=True,
                          editable=False,
                          verbose_name=_('ID'))
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='account_user',
                                verbose_name=_("Пользователь"))
    inn = models.CharField(max_length=12,
                           unique=True,
                           verbose_name=_("ИНН"))
    amount = models.DecimalField(max_digits=100,
                                 decimal_places=2,
                                 verbose_name=_("Величина счета, Rub"))

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}: {self.inn}"
