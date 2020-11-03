import decimal
import re

from .models import Account
from django.db import transaction


# Обработка операции по переводу средств.
def process_transaction(amount, sender, recipients):
    with transaction.atomic():

        amount = decimal.Decimal(amount)

        recipients = separate_recipients(recipients)

        sender_report = decrease_sender_account_amount(sender, amount)

        if not isinstance(recipients, str):
            try:
                mount_part = amount / decimal.Decimal(len(recipients))
            except ZeroDivisionError as e:
                raise e
        else:
            mount_part = amount

        recipients_report = increase_recipients_accounts_amount(recipients,
                                                                mount_part)

        return f"Счет отправителя: {sender_report}\n" \
               f"Счета получателей: {recipients_report}"


# Уменьшение значения Суммы счета Отправителя.
def decrease_sender_account_amount(sender, amount):
    sender = Account.objects.get(id=sender)
    sender.amount -= amount
    sender.save()
    report = f"{sender}: {sender.amount}"
    return report


# Увеличение значения Суммы счета получателей.
def increase_recipients_accounts_amount(recipients, amount):
    recipients_for_report = recipients
    recipients = Account.objects.filter(inn__in=recipients)
    for recipient in recipients:
        recipient.amount += amount
        recipient.save()

    recipients = Account.objects.filter(inn__in=recipients_for_report)
    report = "".join(
        [f"{recipient}: {recipient.amount} " for recipient in recipients])
    return report


def separate_recipients(recipients):
    return re.findall(r'(\d{12})', recipients)