from django.core.management.base import BaseCommand
from home.models import Category, Books
from django.db.models import Count


class Command(BaseCommand):
    help = 'Limit each category to have a maximum of 30 books, removing books with lowest ratings'

    def handle(self, *args, **options):
        # Get all categories
        categories = Category.objects.all()
        total_removed = 0

        for category in categories:
            # Count books in this category
            book_count = Books.objects.filter(book_category=category).count()
            
            self.stdout.write(f"Category: {category.name} - Current book count: {book_count}")
            
            # If the category has more than 30 books
            if book_count > 30:
                # Find how many books we need to remove
                to_remove = book_count - 30
                
                # Get the books with the lowest ratings
                # We order by rating (ascending), then by id to ensure consistent results for books with same rating
                books_to_remove = Books.objects.filter(
                    book_category=category
                ).order_by('rating', 'id')[:to_remove]
                
                # Get the IDs of books to remove
                book_ids = list(books_to_remove.values_list('id', flat=True))
                
                # Delete these books
                Books.objects.filter(id__in=book_ids).delete()
                
                self.stdout.write(self.style.SUCCESS(
                    f"Removed {to_remove} books from '{category.name}' category"
                ))
                total_removed += to_remove
            else:
                self.stdout.write(f"No books removed from '{category.name}' - already at or below 30 books")
        
        self.stdout.write(self.style.SUCCESS(f"Process completed. Total books removed: {total_removed}"))
