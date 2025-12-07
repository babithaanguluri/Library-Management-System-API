from datetime import timedelta
from decimal import Decimal

from django.db import transaction as db_transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import Book, Member, Transaction, Fine

DAILY_FINE = Decimal("0.50")
MAX_BORROWED_BOOKS = 3
LOAN_DAYS = 14


def _recalculate_member_status(member: Member):
    
    overdue_count = member.transactions.filter(
        status=Transaction.Status.OVERDUE
    ).count()
    has_unpaid_fines = member.fines.filter(paid_at__isnull=True).exists()

    if overdue_count >= 3 or has_unpaid_fines:
        member.status = Member.Status.SUSPENDED
    else:
        member.status = Member.Status.ACTIVE

    member.save(update_fields=["status"])
@db_transaction.atomic
def borrow_book(member_id: int, book_id: int) -> Transaction:
    try:
        member = Member.objects.select_for_update().get(id=member_id)
    except Member.DoesNotExist:
        raise ValidationError("Member not found.")

    try:
        book = Book.objects.select_for_update().get(id=book_id)
    except Book.DoesNotExist:
        raise ValidationError("Book not found.")

    if member.status != Member.Status.ACTIVE:
        raise ValidationError("Member is not active.")

    active_count = member.transactions.filter(
        status__in=[Transaction.Status.ACTIVE, Transaction.Status.OVERDUE]
    ).count()
    if active_count >= MAX_BORROWED_BOOKS:
        raise ValidationError("Member already has 3 borrowed books.")

    if member.fines.filter(paid_at__isnull=True).exists():
        raise ValidationError("Member has unpaid fines.")

    if book.available_copies == 0 or book.status != Book.Status.AVAILABLE:
        raise ValidationError("Book is not available.")

    now = timezone.now()
    due_date = now + timedelta(days=LOAN_DAYS)
    tx = Transaction.objects.create(
        book=book,
        member=member,
        borrowed_at=now,
        due_date=due_date,
        status=Transaction.Status.ACTIVE,
    )

    book.available_copies -= 1
    if book.available_copies == 0:
        book.status = Book.Status.BORROWED
    book.save(update_fields=["available_copies", "status"])

    return tx
@db_transaction.atomic
def return_book(transaction_id: int) -> Transaction:
    try:
        tx = Transaction.objects.select_for_update().select_related(
            "book", "member"
        ).get(id=transaction_id)
    except Transaction.DoesNotExist:
        raise ValidationError("Transaction not found.")

    if tx.status == Transaction.Status.RETURNED:
        raise ValidationError("Book already returned.")

    now = timezone.now()
    tx.returned_at = now
    overdue_days = (now.date() - tx.due_date.date()).days
    if overdue_days > 0:
        amount = DAILY_FINE * overdue_days
        tx.status = Transaction.Status.OVERDUE
        Fine.objects.create(
            member=tx.member,
            transaction=tx,
            amount=amount,
        )
    else:
        tx.status = Transaction.Status.RETURNED
    tx.save()
    book = tx.book
    book.available_copies += 1
    if book.available_copies > 0:
        book.status = Book.Status.AVAILABLE
    book.save(update_fields=["available_copies", "status"])

    _recalculate_member_status(tx.member)

    return tx
@db_transaction.atomic
def pay_fine(fine_id: int) -> Fine:
    try:
        fine = Fine.objects.select_for_update().select_related("member").get(id=fine_id)
    except Fine.DoesNotExist:
        raise ValidationError("Fine not found.")

    if fine.paid_at is not None:
        raise ValidationError("Fine already paid.")

    fine.paid_at = timezone.now()
    fine.save(update_fields=["paid_at"])

    _recalculate_member_status(fine.member)

    return fine