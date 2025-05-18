from django.core.management.base import BaseCommand
from home.models import Category, Books
from django.db.models import Count


class Command(BaseCommand):
    help = 'Limit each category to have a maximum of 30 books, removing books with lowest ratings'

    def handle(self, *args, **options):
        categories = Category.objects.all()
        total_removed = 0

        for category in categories:
            book_count = Books.objects.filter(book_category=category).count()
            
            self.stdout.write(f"Category: {category.name} - Current book count: {book_count}")
            
            if book_count > 30:
                to_remove = book_count - 30
                
                books_to_remove = Books.objects.filter(
                    book_category=category
                ).order_by('rating', 'id')[:to_remove]
                
                book_ids = list(books_to_remove.values_list('id', flat=True))
                
                Books.objects.filter(id__in=book_ids).delete()
                
                self.stdout.write(self.style.SUCCESS(
                    f"Removed {to_remove} books from '{category.name}' category"
                ))
                total_removed += to_remove
            else:
                self.stdout.write(f"No books removed from '{category.name}' - already at or below 30 books")
        
        self.stdout.write(self.style.SUCCESS(f"Process completed. Total books removed: {total_removed}"))
