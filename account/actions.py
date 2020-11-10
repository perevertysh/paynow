import decimal
import re
from typing import AnyStr, List

from .models import Account
from django.db import transaction


def process_transaction(amount: decimal.Decimal,
                        sender: AnyStr,
                        recipients: AnyStr) -> AnyStr:
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


def decrease_sender_account_amount(sender: AnyStr,
                                   amount: decimal.Decimal) -> AnyStr:
    sender = Account.objects.get(id=sender)
    sender.amount -= amount
    sender.save()
    report = f"{sender}: {sender.amount}"
    return report


def increase_recipients_accounts_amount(recipients: List,
                                        amount: decimal.Decimal) -> AnyStr:
    recipients_for_report = recipients
    recipients = Account.objects.filter(inn__in=recipients)
    for recipient in recipients:
        recipient.amount += amount
        recipient.save()

    recipients = Account.objects.filter(inn__in=recipients_for_report)
    report = "".join(
        [f"{recipient}: {recipient.amount} " for recipient in recipients])
    return report


def separate_recipients(recipients: AnyStr) -> List:
    return re.findall(r'(\d{12})', recipients)
