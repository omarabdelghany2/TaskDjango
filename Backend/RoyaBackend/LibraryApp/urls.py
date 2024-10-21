from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, LoginView, BookViewSet, BorrowBookView, 
    ReturnBookView, BorrowedBooksReportView, PopularBooksReportView, BorrowHistoryView
)

# Create a router and register the BookViewSet with it
router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')  # This sets up the CRUD URLs for BookViewSet

# Define URL patterns
urlpatterns = [
    # User registration and login
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),

    # Endpoints for borrowing and returning books
    path('borrow/', BorrowBookView.as_view(), name='borrow-book'),
    path('return/', ReturnBookView.as_view(), name='return-book'),

    # Reports for admin
    path('reports/borrowed/', BorrowedBooksReportView.as_view(), name='borrowed-report'),
    path('reports/popular/', PopularBooksReportView.as_view(), name='popular-report'),

    # Endpoint for users to view their borrowing history
    path('borrow/history/', BorrowHistoryView.as_view(), name='borrow-history'),

    # Include all routes from the DefaultRouter for BookViewSet
    path('', include(router.urls)),
    # Add other URL patterns here if needed
]
