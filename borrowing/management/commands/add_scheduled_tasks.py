from django.core.management.base import BaseCommand
from django_q.models import Schedule


class Command(BaseCommand):
    def handle(self, *args, **options):
        Schedule.objects.create(
            func="borrowing.notifications.check_and_notify_overdue_borrowings",
            schedule_type=Schedule.DAILY,
        )
        self.stdout.write(self.style.SUCCESS("Successfully added scheduled task!"))
