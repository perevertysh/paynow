from decimal import Decimal
from typing import List

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from .actions import separate_recipients_inn, get_recipients_inn_list
from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    inn = serializers.CharField(max_length=12, required=True, label="ИНН")

    def validate_inn(self, value: serializers.CharField
                     ) -> serializers.CharField:
        inn = separate_recipients_inn(value)
        if not inn or len(inn) > 1:
            raise serializers.ValidationError("Проверьте корректность "
                                              "вводимого ИНН")
        return value

    class Meta:
        model = Account
        fields = "__all__"


# Serializer for money transaction method
class TransactionSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=100, decimal_places=2,
        required=True,
        label=_("Сумма перевода"))

    recipients = serializers.CharField(
        max_length=1200,
        required=True,
        label=_("Список ИНН получателей (через пробел)"))

    sender = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(),
        required=True,
        label=_("Отправитель"))

    def validate_amount(self, value: Decimal
                        ) -> Decimal:
        data = self.get_initial()
        sender_account = Account.objects.get(id=data['sender'])
        if sender_account.amount < value:
            raise serializers.ValidationError("Недостаточная сумма на счете!")
        return value

    def validate_recipients(self, value: str
                            ) -> str:

        def list_diffs(a: List, b: List) -> str:
            return "".join(list(set(a).difference(set(b))) +
                           list(set(b).difference(set(a))))

        recipients_inn_input = separate_recipients_inn(value)
        recipients_in_db = get_recipients_inn_list(recipients_inn_input)
        if len(recipients_inn_input) == 0:
            raise serializers.ValidationError(
                f"Проверьте значения вводимых ИНН!"
            )
        if len(recipients_inn_input) != len(recipients_in_db):
            raise serializers.ValidationError(
                f"Проверьте значения вводимых ИНН!: "
                f"{list_diffs(recipients_inn_input, recipients_in_db)}"
            )
        return value
