from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Book, Borrow
from rest_framework import viewsets, permissions
from .serializers import UserSerializer, BookSerializer, BorrowSerializer
from django.contrib.auth.models import User


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer


class LoginView(TokenObtainPairView):
    permission_classes = (AllowAny,)

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
    



class BorrowBookView(APIView):
    def post(self, request):
        book_id = request.data.get('book_id')
        try:
            book = Book.objects.get(id=book_id)
            if book.available_copies > 0:
                Borrow.objects.create(user=request.user, book=book)
                book.available_copies -= 1
                book.save()
                return Response({"message": "Book borrowed successfully"}, status=status.HTTP_201_CREATED)
            return Response({"error": "No copies available"}, status=status.HTTP_400_BAD_REQUEST)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

class ReturnBookView(APIView):
    def post(self, request):
        borrow_id = request.data.get('borrow_id')
        try:
            borrow = Borrow.objects.get(id=borrow_id, user=request.user, returned_date__isnull=True)
            borrow.returned_date = timezone.now()
            borrow.save()
            borrow.book.available_copies += 1
            borrow.book.save()
            return Response({"message": "Book returned successfully"}, status=status.HTTP_200_OK)
        except Borrow.DoesNotExist:
            return Response({"error": "Borrow record not found"}, status=status.HTTP_404_NOT_FOUND)


class BorrowedBooksReportView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        borrowed_books = Borrow.objects.filter(returned_date__isnull=True)
        serializer = BorrowSerializer(borrowed_books, many=True)
        return Response(serializer.data)

class PopularBooksReportView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        popular_books = Book.objects.annotate(
            borrow_count=Count('borrow')
        ).order_by('-borrow_count')[:5]
        serializer = BookSerializer(popular_books, many=True)
        return Response(serializer.data)
