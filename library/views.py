from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Book, Member, Transaction, Fine
from .serializers import (
    BookSerializer,
    MemberSerializer,
    TransactionSerializer,
    FineSerializer,
)
from .services import borrow_book, return_book as return_transaction, pay_fine


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    # GET /api/books/available/
    @action(detail=False, methods=["get"])
    def available(self, request):
        books = Book.objects.filter(status="available", available_copies__gt=0)
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

    # GET /api/members/{id}/borrowed/
    @action(detail=True, methods=["get"])
    def borrowed(self, request, pk=None):
        member = self.get_object()
        borrowed_books = member.transactions.filter(
            status__in=["active", "overdue"]
        )
        serializer = TransactionSerializer(borrowed_books, many=True)
        return Response(serializer.data)


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transaction.objects.select_related("book", "member").all()
    serializer_class = TransactionSerializer

    # POST /api/transactions/borrow/
    @action(detail=False, methods=["post"])
    def borrow(self, request):
        member_id = request.data.get("member_id") or request.data.get("member")
        book_id = request.data.get("book_id") or request.data.get("book")
        tx = borrow_book(member_id, book_id)
        return Response(
            TransactionSerializer(tx).data,
            status=status.HTTP_201_CREATED,
        )

    # POST /api/transactions/{id}/return_book/
    @action(detail=True, methods=["post"])
    def return_book(self, request, pk=None):
        tx = return_transaction(pk)
        return Response(TransactionSerializer(tx).data)

    # GET /api/transactions/overdue/
    @action(detail=False, methods=["get"])
    def overdue(self, request):
        qs = self.get_queryset().filter(status=Transaction.Status.OVERDUE)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class FineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Fine.objects.select_related("member", "transaction").all()
    serializer_class = FineSerializer

    # POST /api/fines/{id}/pay/
    @action(detail=True, methods=["post"])
    def pay(self, request, pk=None):
        fine = pay_fine(pk)
        return Response(FineSerializer(fine).data)