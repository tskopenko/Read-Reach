from borrowing.models import Borrowing
from django.utils.timezone import now


def check_and_notify_overdue_borrowings():
    """Check for overdue borrowings and notify."""
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lt=now(),
        actual_return_date__isnull=True,
    )
    for borrowing in overdue_borrowings:
        notify_user(borrowing.user.id, f"Your borrowing of {borrowing.book.title} is overdue!")


def notify_new_borrowing(borrowing_id):
    """Notify about a new borrowing."""
    borrowing = Borrowing.objects.get(id=borrowing_id)
    notify_user(borrowing.user.id, f"You have successfully borrowed {borrowing.book.title}.")


def notify_user(user_id, message):
    """Placeholder function to send notifications."""
    print(f"Notify user {user_id}: {message}")
