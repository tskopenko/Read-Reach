from enum import Enum

from django.db import models


class CoverType(Enum):
    """ Define Cover type for choice field"""
    HARD = "Hardcover"
    SOFT = "Softcover"


class Book(models.Model):
    """ Define Book Model for representing a book."""

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(
        max_length=10,
        choices=[(tag.name, tag.value) for tag in CoverType]
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=7, decimal_places=2)
