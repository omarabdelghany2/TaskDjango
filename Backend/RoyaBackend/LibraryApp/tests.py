from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import User, Book, Borrow

class BookTests(APITestCase):

    def setUp(self):
        # Create an admin user
        self.admin_user = User.objects.create_superuser(username='adminuser', password='adminpass')
        self.client.login(username='adminuser', password='adminpass')  # Log in the admin user
        
        # Create a normal user
        self.user = User.objects.create_user(username='normaluser', password='userpass')

        # Create a book instance for testing borrowing
        self.book = Book.objects.create(
            title="Sample Book",
            author="Author Name",
            description="A brief description of the book.",
            available_copies=5
        )

        # Obtain access tokens for both users
        self.admin_access_token = self.get_access_token('adminuser', 'adminpass')
        self.user_access_token = self.get_access_token('normaluser', 'userpass')

    def get_access_token(self, username, password):
        """
        Helper method to obtain an access token for a user.
        """
        response = self.client.post(reverse('login'), {
            'username': username,
            'password': password
        })
        return response.data['access']

    def test_add_book(self):
        """
        Test that an admin user can add a new book.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)

        book_data = {
            "title": "New Book Title",
            "author": "Author Name",
            "description": "This is a brief description of the new book.",
            "available_copies": 5
        }

        # Send a POST request to create a new book
        response = self.client.post(reverse('book-list'), book_data)

        # Assert that the book was created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)  # One original book + new book

        # Verify that the new book was created correctly
        new_book = Book.objects.get(title='New Book Title')
        self.assertEqual(new_book.author, 'Author Name')
        self.assertEqual(new_book.available_copies, 5)

    def test_get_all_books(self):
        """
        Test that an admin user can retrieve all books.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)

        # Create additional book instances to test
        Book.objects.create(
            title="Another Sample Book",
            author="Another Author",
            description="Another book description.",
            available_copies=3
        )
        Book.objects.create(
            title="Third Sample Book",
            author="Third Author",
            description="Third book description.",
            available_copies=2
        )

        # Send a GET request to retrieve all books
        response = self.client.get(reverse('book-list'))

        # Assert that the response status code is 200 OK and contains the expected number of books
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # 1 original + 2 new books

        # Assert that the response contains expected book titles
        titles = [book['title'] for book in response.data]
        self.assertIn("Sample Book", titles)
        self.assertIn("Another Sample Book", titles)
        self.assertIn("Third Sample Book", titles)

    def test_borrow_book(self):
        """
        Test that a user can borrow a book.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_access_token)

        borrow_data = {
            'book_id': self.book.id
        }

        # Send a POST request to borrow the book
        response = self.client.post(reverse('borrow-book'), borrow_data)

        # Assert that the book was borrowed successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check the updated available copies of the book
        self.book.refresh_from_db()
        self.assertEqual(Borrow.objects.count(), 1)  # Verify borrow record creation
        self.assertEqual(self.book.available_copies, 4)  # Available copies should decrease by 1

    def test_return_book(self):
        """
        Test that a user can return a borrowed book.
        """
        borrow_record = Borrow.objects.create(user=self.user, book=self.book)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_access_token)

        return_data = {
            'borrow_id': borrow_record.id  # Use the actual ID of the borrow record
        }

        # Send a POST request to return the book
        response = self.client.post(reverse('return-book'), return_data)

        # Assert that the book was returned successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that the borrow record was updated
        borrow_record.refresh_from_db()  # Refresh to get the latest data
        self.assertIsNotNone(borrow_record.returned_date)

        # Refresh the book to check available copies
        self.book.refresh_from_db()  # Get the latest available copies
        self.assertEqual(self.book.available_copies, 6)  # Available copies should increment by 1

    def test_borrowed_books_report(self):
        """
        Test that an admin can access the borrowed books report.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)

        # Ensure a book is borrowed for reporting
        Borrow.objects.create(user=self.user, book=self.book)

        # Send a GET request to the borrowed books report endpoint
        response = self.client.get(reverse('borrowed-report'))

        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response contains the correct data
        self.assertEqual(len(response.data), 1)  # Adjust based on the number of borrowed records expected
        self.assertEqual(response.data[0]['user'], self.user.id)  # User ID check
        self.assertEqual(response.data[0]['book'], self.book.id)  # Book ID check

    def test_popular_books_report(self):
        """
        Test that an admin can access the popular books report.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)

        # Create additional books and borrow them
        book1 = Book.objects.create(title="Book 1", author="Author 1", available_copies=3)
        book2 = Book.objects.create(title="Book 2", author="Author 2", available_copies=2)
        Borrow.objects.create(user=self.user, book=book1)
        Borrow.objects.create(user=self.user, book=book1)  # Borrow the same book twice
        Borrow.objects.create(user=self.user, book=book2)

        # Send a GET request to retrieve popular books
        response = self.client.get(reverse('popular-report'))

        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the expected number of popular books
        self.assertEqual(len(response.data), 3)  # Based on the number of borrows

        # Assert that the most borrowed book is at the top of the list
        self.assertEqual(response.data[0]['title'], "Book 1")
