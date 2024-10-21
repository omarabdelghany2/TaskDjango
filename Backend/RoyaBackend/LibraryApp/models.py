from django.db import models
from django.contrib.auth.models import User

class Book(models.Model):
    """
    Model representing a book in the library.
    """
    title = models.CharField(max_length=255)  # Title of the book
    author = models.CharField(max_length=255)  # Author of the book
    description = models.TextField()  # Detailed description of the book
    available_copies = models.IntegerField(default=1)  # Number of available copies for borrowing

    def __str__(self):
        """
        String representation of the Book model.
        """
        return self.title


class Borrow(models.Model):
    """
    Model representing a borrowing record.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who borrowed the book
    book = models.ForeignKey(Book, on_delete=models.CASCADE)  # Book that is borrowed
    borrowed_date = models.DateTimeField(auto_now_add=True)  # Date and time when the book was borrowed
    returned_date = models.DateTimeField(null=True, blank=True)  # Date and time when the book was returned

    def __str__(self):
        """
        String representation of the Borrow model.
        """
        return f"{self.user.username} - {self.book.title}"
