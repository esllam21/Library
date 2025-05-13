#!/usr/bin/env python
"""
Script to populate Category model and update Books with proper category relationships.
Run this from your Django project root with:
python populate_categories.py
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Library.settings')
django.setup()

from home.models import Category, Books

def populate_categories():
    """Populate the Category model with default categories."""
    # Default categories
    default_categories = [
        'Fiction', 'Non-Fiction', 'Sci-Fi', 'Fantasy', 'Mystery', 
        'Thriller', 'Romance', 'Historical', 'Biography', 'Business',
        'Self-Help', 'Education', 'Children', 'Young Adult', 'Science',
        'Technology', 'Art', 'Cooking', 'Travel', 'Religion'
    ]
    
    # Create default categories
    categories_created = 0
    for cat_name in default_categories:
        _, created = Category.objects.get_or_create(name=cat_name)
        if created:
            categories_created += 1
            print(f"Created category: {cat_name}")
    
    # Get unique categories from existing books
    book_categories = set(
        cat for cat in Books.objects.values_list('category', flat=True)
        if cat is not None and cat.strip() != ''
    )
    
    # Create additional categories from existing books
    for cat_name in book_categories:
        if cat_name not in default_categories:
            _, created = Category.objects.get_or_create(name=cat_name)
            if created:
                categories_created += 1
                print(f"Created category from book: {cat_name}")
    
    # Link books to categories
    books_updated = 0
    for book in Books.objects.filter(book_category__isnull=True):
        if book.category:
            try:
                category = Category.objects.get(name=book.category)
                book.book_category = category
                book.save(update_fields=['book_category'])
                books_updated += 1
            except Category.DoesNotExist:
                # If category doesn't exist (which shouldn't happen at this point), create it
                category = Category.objects.create(name=book.category)
                book.book_category = category
                book.save(update_fields=['book_category'])
                books_updated += 1
    
    print(f"Created {categories_created} categories and updated {books_updated} books")

if __name__ == "__main__":
    populate_categories()
