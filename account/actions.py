import decimal
import re
from typing import List

from .models import Account
from django.db import transaction


def process_transaction(amount: decimal.Decimal,
                        sender: str,
                        recipients: str) -> str:
    with transaction.atomic():

        amount = decimal.Decimal(amount)

        recipients_list = separate_recipients(recipients)

        sender_report = decrease_sender_account_amount(sender, amount)

        if not isinstance(recipients_list, str):
            try:
                mount_part = amount / decimal.Decimal(len(recipients_list))
            except ZeroDivisionError as e:
                raise e
        else:
            mount_part = amount

        recipients_report = increase_recipients_accounts_amount(recipients_list,
                                                                mount_part)

        return f"Счет отправителя: {sender_report}\n" \
               f"Счета получателей: {recipients_report}"


def decrease_sender_account_amount(sender_id: str,
                                   amount: decimal.Decimal) -> str:
    sender = Account.objects.get(id=sender_id)
    sender.amount -= amount
    sender.save()
    report = f"{sender}: {sender.amount}"
    return report


def increase_recipients_accounts_amount(recipients: List,
                                        amount: decimal.Decimal) -> str:
    recipients_for_report = recipients
    recipients = Account.objects.filter(inn__in=recipients)
    for recipient in recipients:
        recipient.amount += amount
        recipient.save()

    recipients = Account.objects.filter(inn__in=recipients_for_report)
    report = "".join(
        [f"{recipient}: {recipient.amount} " for recipient in recipients])
    return report


def separate_recipients(recipients: str) -> List:
    return re.findall(r'(\d{12})', recipients)
