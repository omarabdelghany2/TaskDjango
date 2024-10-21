from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import User, Book, Borrow
from django.utils import timezone
from django.db.models import Count


class BookTests(APITestCase):

    def setUp(self):
        # Create an admin user
        self.admin_user = User.objects.create_superuser(username='adminuser', password='adminpass')
        
        # Log in the admin user
        self.client.login(username='adminuser', password='adminpass')
        
        # Create a normal user
        self.user = User.objects.create_user(username='normaluser', password='userpass')
        
        # Create a book instance to borrow
        self.book = Book.objects.create(
            title="Sample Book",
            author="Author Name",
            description="A brief description of the book.",
            available_copies=5
        )

        # Obtain the access token for the admin user
        response = self.client.post(reverse('login'), {
            'username': 'adminuser',
            'password': 'adminpass'
        })
        self.admin_access_token = response.data['access']

        # Obtain the access token for the normal user
        response = self.client.post(reverse('login'), {
            'username': 'normaluser',
            'password': 'userpass'
        })
        self.user_access_token = response.data['access']

    def test_add_book(self):
        # Prepare the request headers with the access token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)

        # Data to create a new book
        book_data = {
            "title": "New Book Title",
            "author": "Author Name",
            "description": "This is a brief description of the new book.",
            "available_copies": 5
        }

        # Send a POST request to create a new book
        response = self.client.post(reverse('book-list'), book_data)  # Use the actual API URL
        
        # Assert that the book was created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify that the book was actually created
        self.assertEqual(Book.objects.count(), 2)  # One original book + new book
        new_book = Book.objects.get(title='New Book Title')
        self.assertEqual(new_book.author, 'Author Name')
        self.assertEqual(new_book.available_copies, 5)

    def test_get_all_books(self):
        # Prepare the request headers with the access token
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

        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response contains the correct number of books
        self.assertEqual(len(response.data), 3)  # 1 original + 2 new books

        # Assert that the response contains expected book details
        titles = [book['title'] for book in response.data]
        self.assertIn("Sample Book", titles)
        self.assertIn("Another Sample Book", titles)
        self.assertIn("Third Sample Book", titles)

    def test_borrow_book(self):
        # Prepare the request headers with the user's access token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_access_token)

        # Data to borrow a book
        borrow_data = {
            'book_id': self.book.id
        }

        # Send a POST request to borrow the book
        response = self.client.post(reverse('borrow-book'), borrow_data)

        # Assert that the book was borrowed successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Re-fetch the book from the database to check the updated available copies
        self.book.refresh_from_db()

        # Verify that the borrow record was created
        self.assertEqual(Borrow.objects.count(), 1)
        self.assertEqual(self.book.available_copies, 4)  # Now it should be 4


    def test_return_book(self):
        # Borrow a book first
        borrow_record = Borrow.objects.create(user=self.user, book=self.book)

        # Prepare the request headers with the user's access token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_access_token)

        # Data to return the book
        return_data = {
            'borrow_id': borrow_record.id  # Use the actual ID of the borrow record
        }

        # Send a POST request to return the book
        response = self.client.post(reverse('return-book'), return_data)

        # Assert that the book was returned successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that the borrow record was updated
        borrow_record.refresh_from_db()  # Refresh to get the latest data from the database
        self.assertIsNotNone(borrow_record.returned_date)
        
        # Refresh the book to check available copies
        self.book.refresh_from_db()  # Refresh to get the latest available copies
        self.assertEqual(self.book.available_copies, 6)  # Check if available copies are incremented


    def test_borrowed_books_report(self):
        # Log in as the admin user to access the borrowed books report
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)

        # Ensure an admin user has borrowed a book (if needed)
        Borrow.objects.create(user=self.user, book=self.book)

        # Send a GET request to the borrowed books report endpoint
        response = self.client.get(reverse('borrowed-report'))

        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response contains the correct data
        self.assertEqual(len(response.data), 1)  # Adjust based on the number of borrowed records expected
        # Optionally check that the response data matches expected values
        self.assertEqual(response.data[0]['user'], self.user.id)  # Assuming the serializer includes the user ID
        self.assertEqual(response.data[0]['book'], self.book.id)  # Assuming the serializer includes the book ID



    def test_popular_books_report(self):
        # Prepare the request headers with the admin user's access token
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

        # Adjust the expected number of popular books
        self.assertEqual(len(response.data), 3)  # Updated based on the number of borrows

        # Assert that the most borrowed book is at the top
        self.assertEqual(response.data[0]['title'], "Book 1")

