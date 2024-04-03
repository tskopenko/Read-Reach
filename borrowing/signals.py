import asyncio

from django.db.models.signals import post_save
from django.dispatch import receiver

from borrowing.tasks import send_notification_to_telegram_bot


@receiver(post_save, sender="borrowing.Borrowing")
def send_notification(instance, created, **kwargs):
    if created:
        asyncio.run(
            send_notification_to_telegram_bot(
                f"You have successfully borrowed {instance.book.title}. "
                f"Expected return date: {instance.expected_return_date}"
            )
        )
