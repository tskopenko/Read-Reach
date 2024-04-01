from enum import Enum

from django.db import models


class CoverType(Enum):
    HARD = "Hardcover"
    SOFT = "Softcover"


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(
        max_length=10,
        choices=[(tag, tag.value) for tag in CoverType]
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=7, decimal_places=2)
