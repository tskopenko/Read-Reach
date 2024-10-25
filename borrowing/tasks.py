import asyncio

from celery import shared_task
from django.utils.timezone import now

from .models import Borrowing
from .utils import send_notification_to_telegram_bot


@shared_task
def check_and_notify_overdue_borrowings() -> None:
    """Checks for overdue borrowings and notifies the users via Telegram bot"""
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lt=now(), actual_return_date__isnull=True
    )

    if not overdue_borrowings.exists():
        asyncio.run(
            send_notification_to_telegram_bot("No overdue borrowings for today!")
        )
    else:
        for borrowing in overdue_borrowings:
            text = (
                f"Notify user {borrowing.user.email}: "
                f'{f"Your borrowing of {borrowing.book.title} is overdue!"}'
            )
            asyncio.run(send_notification_to_telegram_bot(text))
