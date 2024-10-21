# API Documentation for Roya Backend


Deployment URL :
http://165.232.126.71:8000/



Postman Collection

A Postman collection is provided to facilitate testing of the API endpoints. You can import the collection and make requests as described above.

How to Import the Postman Collection
Open Postman.
Click on "Import" in the top left corner.
Select "Upload Files" and choose the exported Postman collection JSON file from MY repository.
its name is :Royabackend-LibraryApp.postman_collection.json
After importing, you will find all the defined API endpoints in your Postman workspace.
The Postman collection includes examples for all available API endpoints, making it easy to test the functionalities without manual setup.


## Overview

This documentation outlines the available API endpoints for the Roya Backend application. The API is built using Django REST Framework and provides functionalities for user authentication, book management, and borrowing reports.

## Base URL

All endpoints can be accessed through the following base URL:

http://165.232.126.71:8000/api/


## Authentication

To access certain API endpoints, you need to authenticate as a user. Follow these steps to authenticate:

1. **Login** to obtain the access token:
   - **Endpoint:** `/login/`
   - **Method:** `POST`
   - **Body:**
   ```json
   {
       "username": "your_username",
       "password": "your_password"
   }

   Response:
   {
       "refresh": "your_refresh_token",
       "access": "your_access_token"
   }

Use the Access Token: For endpoints that require authorization, include the token in the Authorization header:

Authorization: Bearer your_access_token


## API Endpoints

User Management
   ### Register a New User
        Endpoint: /register/
        Method: POST
        Body:
        ```json
              
              {
                  "username": "new_user",
                  "password": "new_password"
              }
              Response: Returns details of the created user.
  
  
  ### Login User
        Endpoint: /login/
        Method: POST
         Body:
         ```json
         
        {
            "username": "your_username",
            "password": "your_password"
        }

## Book Management
   ### Get All Books
        Endpoint: /books/
        Method: GET
        Authorization: Required
        Response: Returns a list of books.
    Create a New Book
        Endpoint: /books/
        Method: POST
        Authorization: Required
        Body:
        ```json
        
           {
              "title": "New Book Title",
              "author": "Author Name",
              "description": "Description of the book.",
              "available_copies": 5
           }

   Update an Existing Book
        Endpoint: /books/{id}/
        Method: PATCH
        Authorization: Required
        Body:     
        ```json
        
        {
          "title": "Updated Book Title",
          "author": "Updated Author Name"
        }
        Response: Returns updated details of the book.


   Delete a Book
        Endpoint: /books/{id}/
        Method: DELETE
        Authorization: Required
        Response: Returns status code 204 No Content.     


   Borrow Management
        Borrow a Book
        Endpoint: /borrow/
        Method: POST
        Authorization: Required
        Body:
        ```json
        
        {
           "book_id": 1
        }
        Response: Returns a success message.



   Reports
        Get Borrowed Books Report
        Endpoint: /reports/borrowed/
        Method: GET
        Authorization: Admin Required
        Response: Returns a list of borrowed books.
        Get Popular Books Report
        Endpoint: /reports/popular/
        Method: GET
        Authorization: Admin Required
        Response: Returns a list of popular books.     





              


