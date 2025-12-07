from rest_framework import serializers
from .models import Book, Member, Transaction, Fine
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"
class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = "__all__"
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
        read_only_fields = ("borrowed_at", "due_date", "returned_at", "status")
class FineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fine
        fields = "__all__"
        read_only_fields = ("member", "transaction", "amount", "paid_at")