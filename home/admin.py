from django.contrib import admin
from .models import Members, Books, BorrowedBook, Category

class BooksAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'borrowPrice', 'buyPrice', 'stock', 'get_category')
    list_filter = ('book_category', 'author')
    search_fields = ('title', 'author', 'description')
    readonly_fields = ('calculated_buy_price',)
    
    fieldsets = (
        (None, {
            'fields': ('title', 'author', 'description', 'book_category', 'category')
        }),
        ('Pricing', {
            'fields': ('borrowPrice', 'buyPrice', 'calculated_buy_price'),
        }),
        ('Stats', {
            'fields': ('rating', 'ratingCount', 'stock', 'count')
        }),
        ('Other Details', {
            'fields': ('pageCount', 'published', 'image'),
            'classes': ('collapse',)
        }),
    )

    def calculated_buy_price(self, obj):
        return obj.calculated_buy_price

    calculated_buy_price.short_description = "Calculated Buy Price"

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

class BorrowedBookAdmin(admin.ModelAdmin):
    list_display = ('member', 'book', 'borrowed_date', 'returned')
    list_filter = ('returned', 'borrowed_date')
    search_fields = ('member__username', 'book__title')

admin.site.register(Members)
admin.site.register(Books, BooksAdmin)
admin.site.register(BorrowedBook, BorrowedBookAdmin)
admin.site.register(Category, CategoryAdmin)
