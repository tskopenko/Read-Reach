from django.db import models
from rest_framework.exceptions import ValidationError

from book.models import Book
from user.models import User


class Borrowing(models.Model):

    """ Define Borrowing Model for representing a book
    borrowing by a user with borrow and return details."""

    borrow_date = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateTimeField()
    actual_return_date = models.DateTimeField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="borrowings")

    def __str__(self):
        actual_return = (self.actual_return_date.strftime('%Y-%m-%d %H:%M')
                         if self.actual_return_date
                         else "Not returned yet")
        return (f"Borrow date: {self.borrow_date.strftime('%Y-%m-%d %H:%M')}, "
                f"Expected return date: {self.expected_return_date.strftime('%Y-%m-%d %H:%M')}"
                f"Actual return date: {actual_return}")

    def clean(self):
        """
        Performs validation checks on the Borrowing instance.
        """
        super().clean()

        if (self.actual_return_date and self.borrow_date) and self.actual_return_date < self.borrow_date:
            raise ValidationError("Actual return date cannot be before borrow date")

        if self.expected_return_date < self.borrow_date:
            raise ValidationError("Expected return date cannot be before borrow date")
