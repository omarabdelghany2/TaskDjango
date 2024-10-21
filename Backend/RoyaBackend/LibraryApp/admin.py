from django.contrib import admin
from .models import Book, Borrow

class BookAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Book model.
    """
    # Fields to be displayed in the list view of the admin panel
    list_display = ('title', 'author', 'available_copies')  
    # Fields that can be searched in the admin panel
    search_fields = ('title', 'author')  

# Register the Book model with the custom admin interface
admin.site.register(Book, BookAdmin)

class BorrowAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Borrow model.
    """
    # Fields to be displayed in the list view of the admin panel
    list_display = ('user', 'book', 'borrowed_date', 'returned_date')  
    # Fields that can be searched in the admin panel
    search_fields = ('user__username', 'book__title')  
    # Filter options for the list view in the admin panel
    list_filter = ('returned_date',)  

# Register the Borrow model with the custom admin interface
admin.site.register(Borrow, BorrowAdmin)
