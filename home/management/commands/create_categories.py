from django.core.management.base import BaseCommand
from home.models import Category, Books

class Command(BaseCommand):
    help = 'Creates default categories and updates existing books'

    def handle(self, *args, **options):
        # Default categories to ensure they exist
        default_categories = [
            'Fiction', 'Non-Fiction', 'Sci-Fi', 'Fantasy', 'Mystery', 
            'Thriller', 'Romance', 'Historical', 'Biography', 'Business',
            'Self-Help', 'Education', 'Children', 'Young Adult', 'Science',
            'Technology', 'Art', 'Cooking', 'Travel', 'Religion'
        ]
        
        # Get existing category names
        existing_categories = set(Category.objects.values_list('name', flat=True))
        
        # Create missing categories
        categories_created = 0
        for cat_name in default_categories:
            if cat_name not in existing_categories:
                Category.objects.create(name=cat_name)
                categories_created += 1
                self.stdout.write(f"Created category: {cat_name}")
        
        # Extract unique categories from existing books
        book_categories = set(
            cat for cat in Books.objects.values_list('category', flat=True) 
            if cat is not None and cat.strip() != ''
        )
        
        # Create categories from books if they don't exist
        for cat_name in book_categories:
            if cat_name not in existing_categories and cat_name not in default_categories:
                Category.objects.create(name=cat_name)
                categories_created += 1
                self.stdout.write(f"Created category from book: {cat_name}")
        
        # Update books to use the category relationship
        books_updated = 0
        for book in Books.objects.filter(book_category__isnull=True):
            if book.category:
                try:
                    category = Category.objects.get(name=book.category)
                    book.book_category = category
                    book.save(update_fields=['book_category'])
                    books_updated += 1
                except Category.DoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f"Could not find category '{book.category}' for book '{book.title}'"
                    ))
        
        self.stdout.write(self.style.SUCCESS(
            f"Created {categories_created} categories and updated {books_updated} books"
        ))
