from django.db import models
from django.utils import timezone
from decimal import Decimal


class Book(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        BORROWED = "borrowed", "Borrowed"
        RESERVED = "reserved", "Reserved"
        MAINTENANCE = "maintenance", "Maintenance"

    isbn = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.AVAILABLE
    )
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)

    def _str_(self):
        return self.title


class Member(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    membership_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )

    def _str_(self):
        return self.name


class Transaction(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        RETURNED = "returned", "Returned"
        OVERDUE = "overdue", "Overdue"

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="transactions")
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="transactions"
    )
    borrowed_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices)

    def _str_(self):
        return f"{self.member} borrowed {self.book}"


class Fine(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="fines")
    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="fines"
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    paid_at = models.DateTimeField(null=True, blank=True)

    def _str_(self):
        return f"Fine: {self.amount}"