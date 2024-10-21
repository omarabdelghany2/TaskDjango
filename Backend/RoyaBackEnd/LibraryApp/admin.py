from django.contrib import admin
from .models import Book, Borrow
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'available_copies')
    search_fields = ('title', 'author')

@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'borrowed_date', 'returned_date')
    search_fields = ('user__username', 'book__title')
    list_filter = ('returned_date',)
