from rest_framework import generics, status, viewsets, permissions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count

from .models import Book, Borrow
from .serializers import UserSerializer, BookSerializer, BorrowSerializer

# Register new users
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)  # Allow anyone to register
    serializer_class = UserSerializer


# Login users and issue JWT tokens
class LoginView(TokenObtainPairView):
    permission_classes = (AllowAny,)  # Allow anyone to access login


# CRUD operations for books
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        """
        Set custom permissions for different actions.
        Only admins can create, update, or delete books.
        Anyone can view the list of books.
        """
        if self.action in ['create', 'update', 'destroy']:
            return [permissions.IsAdminUser()]  # Admin only for these actions
        return [permissions.AllowAny()]  # Read access for everyone


# Endpoint to borrow a book
class BorrowBookView(APIView):
    def post(self, request):
        book_id = request.data.get('book_id')
        try:
            book = Book.objects.get(id=book_id)
            if book.available_copies > 0:
                # Create a new Borrow record for the user and reduce available copies
                Borrow.objects.create(user=request.user, book=book)
                book.available_copies -= 1
                book.save()
                return Response({"message": "Book borrowed successfully"}, status=status.HTTP_201_CREATED)
            return Response({"error": "No copies available"}, status=status.HTTP_400_BAD_REQUEST)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)


# Endpoint to return a borrowed book
class ReturnBookView(APIView):
    def post(self, request):
        borrow_id = request.data.get('borrow_id')
        try:
            # Find the active borrow record for this user
            borrow = Borrow.objects.get(id=borrow_id, user=request.user, returned_date__isnull=True)
            # Mark the book as returned and update available copies
            borrow.returned_date = timezone.now()
            borrow.save()
            borrow.book.available_copies += 1
            borrow.book.save()
            return Response({"message": "Book returned successfully"}, status=status.HTTP_200_OK)
        except Borrow.DoesNotExist:
            return Response({"error": "Borrow record not found"}, status=status.HTTP_404_NOT_FOUND)


# Admin-only view to get a list of currently borrowed books
class BorrowedBooksReportView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        # Get all books that are currently borrowed (not returned)
        borrowed_books = Borrow.objects.filter(returned_date__isnull=True)
        serializer = BorrowSerializer(borrowed_books, many=True)
        return Response(serializer.data)


# Admin-only view to get the top 5 most borrowed books
class PopularBooksReportView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        # Get books annotated with the number of times they have been borrowed
        popular_books = Book.objects.annotate(
            borrow_count=Count('borrow')
        ).order_by('-borrow_count')[:5]  # Sort by borrow count and get the top 5
        serializer = BookSerializer(popular_books, many=True)
        return Response(serializer.data)


# View for users to see their own borrowing history
class BorrowHistoryView(APIView):
    def get(self, request):
        user = request.user
        # Get all borrow records for the requesting user
        borrow_history = Borrow.objects.filter(user=user)
        serializer = BorrowSerializer(borrow_history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
