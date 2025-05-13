from django.db import models


from django.db import models

class Category(models.Model):
  name = models.CharField(max_length=255, unique=True)
  description = models.TextField(blank=True, null=True)
  
  def __str__(self):
    return self.name
    
  class Meta:
    verbose_name_plural = "Categories"

import random
from decimal import Decimal

class Books(models.Model):
  title = models.CharField(max_length=255)
  author = models.CharField(max_length=255)
  pageCount = models.IntegerField()
  borrowPrice = models.DecimalField(max_digits=10, decimal_places=2)
  buyPrice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
  rating = models.DecimalField(max_digits=10, decimal_places=2, null=True)
  stock = models.IntegerField()
  count = models.IntegerField(null=True, default=0)
  image = models.ImageField(upload_to='book-images/', null=True, blank=True)
  # Keep the old field for compatibility during migration
  category = models.CharField(max_length=255, null=True)
  # New field that references the Category model
  book_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='books')
  description = models.TextField(null=True)
  published = models.IntegerField(null=True)
  ratingCount = models.IntegerField(null=True)

  def __str__(self):
    return self.title
    
  @property
  def get_image_url(self):
    """Return image URL or a default placeholder if image is missing"""
    if self.image and hasattr(self.image, 'url'):
      return self.image.url
    return "https://via.placeholder.com/150x200/e0e0e0/808080?text=No+Image"
    
  @property
  def get_category(self):
    """Return category name, prioritizing the relationship field"""
    if self.book_category:
      return self.book_category.name
    return self.category
    
  @property
  def calculated_buy_price(self):
    """Calculate buy price based on borrow price + random value"""
    if self.borrowPrice:
      # If buyPrice is not set, calculate it on the fly
      if not self.buyPrice:
        random_addition = random.randint(20, 50)
        return self.borrowPrice + Decimal(random_addition)
      return self.buyPrice
    return Decimal('0.00')
    
  def save(self, *args, **kwargs):
    # Auto-calculate buyPrice if it's not already set
    if self.borrowPrice and not self.buyPrice:
      random_addition = random.randint(20, 50)
      self.buyPrice = self.borrowPrice + Decimal(random_addition)
    super().save(*args, **kwargs)


class Members(models.Model):
  USER_TYPES = (
    ('Admin', 'Admin'),
    ('Customer', 'Customer'),
  )

  first_name = models.CharField(max_length=255)
  last_name = models.CharField(max_length=255)
  username = models.CharField(max_length=255, unique=True)
  email = models.EmailField(unique=True)
  password = models.CharField(max_length=255)
  phone = models.CharField(max_length=20, unique=True)
  image = models.ImageField(upload_to='user-images/', blank=True, null=True)
  user_type = models.CharField(max_length=10, choices=USER_TYPES)

  def __str__(self):
    return f"{self.first_name} {self.last_name} ({self.user_type})"


class BorrowedBook(models.Model):
  member = models.ForeignKey(Members, on_delete=models.CASCADE)
  book = models.ForeignKey(Books, on_delete=models.CASCADE)
  borrowed_date = models.DateTimeField(auto_now_add=True)
  returned = models.BooleanField(default=False)

  def __str__(self):
    return f"{self.member} borrowed {self.book}"


class FavouriteBooks(models.Model):
  member = models.ForeignKey(Members, on_delete=models.CASCADE)
  book = models.ForeignKey(Books, on_delete=models.CASCADE)


class OwnedBooks(models.Model):
  member = models.ForeignKey(Members, on_delete=models.CASCADE)
  book = models.ForeignKey(Books, on_delete=models.CASCADE)
