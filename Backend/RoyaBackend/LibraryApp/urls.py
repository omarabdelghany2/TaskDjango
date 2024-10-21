from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, BookViewSet, BorrowBookView, ReturnBookView, BorrowedBooksReportView, PopularBooksReportView ,BorrowHistoryView



router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book') 
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('borrow/', BorrowBookView.as_view(), name='borrow-book'),
    path('return/', ReturnBookView.as_view(), name='return-book'),
    path('reports/borrowed/', BorrowedBooksReportView.as_view(), name='borrowed-report'),
    path('reports/popular/', PopularBooksReportView.as_view(), name='popular-report'),
    path('borrow/history/', BorrowHistoryView.as_view(), name='borrow-history'),  # Add this line
    path('', include(router.urls)),
    # Add other URL patterns here if needed
]
    