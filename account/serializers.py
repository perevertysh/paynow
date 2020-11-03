from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from .actions import separate_recipients
from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"


# Сериализатор, определяющий поля для метода перевода средств.
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

    def validate_amount(self, value):
        data = self.get_initial()
        sender_account = Account.objects.get(id=data['sender'])
        if sender_account.amount < value:
            raise serializers.ValidationError("Недостаточная сумма на счете!")
        return value

    def validate_recipients(self, value):

        def list_diffs(a, b):
            return "".join(list(set(a).difference(set(b))) +
                           list(set(b).difference(set(a))))

        recipients_input = separate_recipients(value)
        recipients_in_db = [ac[0] for ac in Account.objects.filter(
            inn__in=recipients_input).values_list("inn")]
        if len(recipients_input) == 0:
            raise serializers.ValidationError(
                f"Проверьте значения вводимых ИНН!"
            )
        if len(recipients_input) != len(recipients_in_db):
            raise serializers.ValidationError(
                f"Проверьте значения вводимых ИНН!: "
                f"{list_diffs(recipients_input, recipients_in_db)}"
            )
        return value