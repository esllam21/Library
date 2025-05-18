from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.views.decorators.http import require_GET, require_POST
from .models import Members, Books, BorrowedBook, Category, FavouriteBooks, OwnedBooks
from collections import Counter
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from .forms import BookForm  # تأكد إنه موجود في forms.py


def categoriesPage(request):
  """View to display all categories and their books"""
  # Get all categories ordered by book count
  categories = Category.objects.annotate(
    book_count=Count('books')
  ).order_by('-book_count')

  # Get the category ID from the request (default to 'all')
  category_id = request.GET.get('category_id', 'all')
  current_path = request.path

  # Initialize variables
  user_image = None
  username = None
  userType = None
  favorite_book_ids = []
  books = []

  if request.session.get('is_logged_in'):
    try:
      user = Members.objects.get(email=request.session.get('user_email'))
      user_image = user.image.url if user.image else '/static/images/default-user.png'
      username = user.username
      userType = user.user_type

      # Get user's favorite books
      favorite_book_ids = FavouriteBooks.objects.filter(member=user).values_list('book_id', flat=True)
    except Members.DoesNotExist:
      pass

  # Get books based on selected category and current path
  if category_id == 'all':
    if '/home/categories/' in current_path:
      # For categories page, load all books with no limit
      books = Books.objects.all().order_by('-rating', '-ratingCount')
    else:
      # For home page, limit to 12 books
      books = Books.objects.all().order_by('-rating', '-ratingCount')[:12]
  else:
    try:
      # First try to get books by category ID
      books = Books.objects.filter(book_category_id=category_id).order_by('-rating', '-ratingCount')

      # If we don't have enough books, also include books with matching category name
      if books.count() < 12:  # Minimum threshold
        category = Category.objects.get(id=category_id)
        additional_books = Books.objects.filter(
          category=category.name
        ).exclude(
          id__in=books.values_list('id', flat=True)
        ).order_by('-rating', '-ratingCount')

        if '/home/categories/' in current_path:
          # For categories page, include all additional books
          books = list(books) + list(additional_books)
        else:
          # For home page, limit additional books to reach 12 total
          books = list(books) + list(additional_books[:12 - books.count()])
    except (ValueError, Category.DoesNotExist):
      books = []

  # Ensure all books have buyPrice values
  for book in books:
    if book.borrowPrice and not book.buyPrice:
      book.save()  # This will trigger the save() method that calculates buyPrice

  return render(request, 'categories.html', {
    'is_logged_in': request.session.get('is_logged_in', False),
    'categories': categories,
    'user_image': user_image,
    'username': username,
    'favorite_book_ids': list(favorite_book_ids),
    'userType': userType,
    'books': books,
    'current_category_id': category_id,
    'is_home_page': '/home/homePage/' in current_path,  # Add this flag
  })


def get_recommended_books(user, limit=20):
  """
    Get recommended books for a user based on borrowing history.

    Logic:
    1. Find the most common categories from user's borrowed books
    2. Recommend highly rated books from those categories
    3. Exclude books the user has already borrowed
    4. Order recommendations by rating
    """
  try:
    # Get all books the user has borrowed (including returned ones)
    borrowed_books = BorrowedBook.objects.filter(member=user)

    # If user has no borrowing history, return empty list
    if not borrowed_books.exists():
      return []

    # Get the book IDs the user has already borrowed
    borrowed_book_ids = borrowed_books.values_list('book_id', flat=True)

    # Get borrowed books
    borrowed_book_objects = Books.objects.filter(id__in=borrowed_book_ids)

    # Get categories of borrowed books - prioritize book_category field but fall back to category field
    category_ids = []
    category_names = []

    for book in borrowed_book_objects:
      if book.book_category_id:
        category_ids.append(book.book_category_id)
      elif book.category:
        category_names.append(book.category)

    # Find most frequent category IDs
    category_id_counter = Counter(category_ids)
    top_category_ids = [cat_id for cat_id, count in category_id_counter.most_common(3)]

    # Find most frequent category names (for backwards compatibility)
    category_name_counter = Counter(category_names)
    top_category_names = [cat for cat, count in category_name_counter.most_common(3) if cat is not None]

    # If no categories found, return empty list
    if not top_category_ids and not top_category_names:
      return []

    # Get recommended books, prioritizing books with matching category IDs
    recommended_books_query = Books.objects.exclude(id__in=borrowed_book_ids)

    if top_category_ids:
      # First try to get books with matching category IDs
      recommended_books = recommended_books_query.filter(
        book_category_id__in=top_category_ids
      ).order_by(
        '-rating', '-ratingCount', 'title'
      )[:limit]

      # If we have enough books, return them
      if recommended_books.count() >= limit:
        return recommended_books

      # Otherwise, we'll also include books with matching category names
      remaining_limit = limit - recommended_books.count()
      recommended_books_from_names = recommended_books_query.filter(
        category__in=top_category_names
      ).exclude(
        id__in=recommended_books.values_list('id', flat=True)
      ).order_by(
        '-rating', '-ratingCount', 'title'
      )[:remaining_limit]

      # Combine the two querysets
      return list(recommended_books) + list(recommended_books_from_names)

    else:
      # Fallback to using just the category names
      return recommended_books_query.filter(
        category__in=top_category_names
      ).order_by(
        '-rating', '-ratingCount', 'title'
      )[:limit]

  except Exception as e:
    print(f"Error generating recommendations: {e}")
    return []


def homePage(request):
  userType=None
  user_image = None
  username = None
  user = None
  recommended_books = []
  favorite_book_ids = []

  if request.session.get('is_logged_in'):
    try:
      user = Members.objects.get(email=request.session.get('user_email'))
      user_image = user.image.url if user.image else '/static/images/default-user.png'
      username = user.username
      userType= user.user_type

      # Get personalized book recommendations if user is logged in
      recommended_books = get_recommended_books(user)

      # Ensure all recommended books have buyPrice values
      for book in recommended_books:
        if book.borrowPrice and not book.buyPrice:
          book.save()  # This will trigger the save() method that calculates buyPrice

      # Get user's favorite books
      favorite_book_ids = FavouriteBooks.objects.filter(member=user).values_list('book_id', flat=True)
    except Members.DoesNotExist:
      pass
    except Exception as e:
      print(f"Error getting user details: {e}")
      # Continue with default values

  # Fetch top-rated books from the database (for everyone)
  try:
    books = Books.objects.all().order_by('-rating')[:20]

    # Ensure all books have buyPrice values
    for book in books:
      if book.borrowPrice and not book.buyPrice:
        book.save()  # This will trigger the save() method that calculates buyPrice
  except Exception as e:
    print(f"Error fetching books: {e}")
    books = []

  # Get top 10 categories with most books for display
  try:
    # Annotate categories with book count and order by count (descending)
    categories = Category.objects.annotate(
      book_count=Count('books')
    ).order_by('-book_count')[:10]
  except Exception as e:
    print(f"Error fetching categories: {e}")
    categories = []

  return render(request, 'Home.html', {
    'is_logged_in': request.session.get('is_logged_in', False),
    'user_image': user_image,
    'username': username,
    'books': books,
    'recommended_books': recommended_books,
    'has_recommendations': len(recommended_books) > 0,
    'categories': categories,
    'favorite_book_ids': list(favorite_book_ids),
    'userType': userType,
  })


def login(request):
  if request.method == 'POST':
    email = request.POST.get('email')
    password = request.POST.get('password')

    try:
      user = Members.objects.get(email=email, password=password)
      request.session['is_logged_in'] = True
      request.session['user_email'] = user.email
      request.session['user_type'] = user.user_type
      request.session['userID'] = user.id

      if user.user_type == 'Admin':
        return redirect('/home/adminDashboard/')
      else:
        return redirect('/home/homePage/')
    except Members.DoesNotExist:
      messages.error(request, "Invalid email or password.")

  return render(request, 'login.html')


def Logout(request):
  request.session.flush()
  return redirect('/home/homePage/')


def signup(request):
  if request.method == 'POST':
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    phone = request.POST.get('phone')
    user_type = request.POST.get('user_type')
    image = request.FILES.get('image')

    # تشفير الباسورد

    try:
      member = Members.objects.create(
        first_name=first_name,
        last_name=last_name,
        username=username,
        email=email,
        password=password,
        phone=phone,
        user_type=user_type,
        image=image
      )
      member.save()
      messages.success(request, 'تم التسجيل بنجاح! ادخل على اللوجين.')
      return redirect('login')  # غير دي حسب اسم صفحة اللوجين عندك
    except Exception as e:
      messages.error(request, f'فيه مشكلة في التسجيل: {str(e)}')
      return render(request, 'signup.html')

  return render(request, 'signup.html')


def borrowedBooksUser(request):
  user_image = None
  username = None
  user = None
  userType=None
  favorite_book_ids = []

  if request.session.get('is_logged_in'):
    try:
      user_email = request.session.get('user_email')
      user = get_object_or_404(Members, email=user_email)
      user_image = user.image.url if user.image else '/static/images/default-user.png'
      username = user.username
      userType= user.user_type

      # Get user's borrowed and owned books
      borrowed_books = BorrowedBook.objects.filter(member=user, returned=False)
      owned_books = OwnedBooks.objects.filter(member=user)

      # Get user's favorite books
      favorite_book_ids = FavouriteBooks.objects.filter(member=user).values_list('book_id', flat=True)
    except Exception as e:
      print(f"Error getting user details: {e}")
      borrowed_books = []
      owned_books = []
  else:
    return redirect('login')  # Redirect to login if not logged in

  # Get top 10 categories with most books for display
  try:
    # Annotate categories with book count and order by count (descending)
    categories = Category.objects.annotate(
      book_count=Count('books')
    ).order_by('-book_count')[:10]
  except Exception as e:
    print(f"Error fetching categories: {e}")
    categories = []

  return render(request, 'borrowed-books-user.html', {
    'is_logged_in': request.session.get('is_logged_in', False),
    'user_image': user_image,
    'username': username,
    'borrowed_books': borrowed_books,
    'owned_books': owned_books,
    'categories': categories,
    'favorite_book_ids': list(favorite_book_ids),
    'userType': userType,
  })


def borrowedBooksAdmin(request):
  user_email = request.session.get('user_email')
  member = get_object_or_404(Members, email=user_email)
  borrowed_books = BorrowedBook.objects.filter(member=member, returned=False)
  all_borrowed_books = Books.objects.all()
  return render(request, 'borrowed-books-admin.html',
                {'borrowed_books': borrowed_books, 'all_borrowed_books': all_borrowed_books})


def adminDashboard(request):
  user_image = None
  username = None
  user=None

  if request.session.get('is_logged_in'):
    try:
      user = Members.objects.get(email=request.session.get('user_email'))
      user_image = user.image.url if user.image else '/static/images/default-user.png'
      username = user.username

      # Get user's favorite books
    except Members.DoesNotExist:
      pass
    except Exception as e:
      print(f"Error getting user details: {e}")
  return render(request, 'admin-dashboard.html', {
    'is_logged_in': request.session.get('is_logged_in', False),
    'user_image': user_image,
    'username': username,
  })


def addBooks(request):
  # Get all categories for the form
  categories = Category.objects.all().order_by('name')

  if request.method == 'POST':
    # Get form data
    title = request.POST.get('title')
    author = request.POST.get('author')
    description = request.POST.get('description')
    pageCount = request.POST.get('pageCount')
    borrowPrice = request.POST.get('borrowPrice')
    stock = request.POST.get('stock')
    category_id = request.POST.get('book_category')
    published = request.POST.get('published')
    image = request.FILES.get('image')

    # Create book (buyPrice will be auto-calculated in save() method)
    if title and author and borrowPrice and stock and category_id:
      try:
        category = Category.objects.get(id=category_id)

        book = Books(
          title=title,
          author=author,
          description=description,
          pageCount=pageCount if pageCount else 0,
          borrowPrice=borrowPrice,
          stock=stock,
          book_category=category,
          category=category.name,  # For backwards compatibility
          published=published if published else None,
        )

        if image:
          book.image = image

        book.save()

        messages.success(request, f"Book '{title}' added successfully!")
        return redirect('/home/availableBooks/')
      except Exception as e:
        messages.error(request, f"Error adding book: {str(e)}")
    else:
      messages.error(request, "Please fill all required fields")

  context = {
    'categories': categories
  }

  template = loader.get_template('add-books.html')
  return HttpResponse(template.render(context, request))


def unauthorized(request):
  return render(request, 'unauthorized.html')


def returnBook(request, book_id):
  if request.method == 'POST':
    if request.session.get('is_logged_in'):
      user_email = request.session.get('user_email')
      member = get_object_or_404(Members, email=user_email)
      book = get_object_or_404(Books, id=book_id)

      # Find the borrowed book record
      borrowed_book = get_object_or_404(BorrowedBook, member=member, book=book, returned=False)

      # Mark as returned
      borrowed_book.returned = True
      borrowed_book.save()

      # Increase the book count
      book.count = (book.count or 0) - 1
      book.stock += 1
      book.save()

      messages.success(request, f"You have successfully returned '{book.title}'.")
      return redirect(request.META.get('HTTP_REFERER', '/home/borrowedBooks/'))
    else:
      return redirect('/home/login/')
  return redirect(request.META.get('HTTP_REFERER', '/home/borrowedBooks/'))


def borrowBook(request, book_id):
  if request.method == 'POST':
    if request.session.get('is_logged_in'):
      user_email = request.session.get('user_email')
      member = get_object_or_404(Members, email=user_email)
      book = get_object_or_404(Books, id=book_id)
      borrowed_books = BorrowedBook.objects.filter(member=member, returned=False)

      # Check if already borrowed
      already_borrowed = BorrowedBook.objects.filter(member=member, book=book, returned=False).exists()
      if not already_borrowed:
        if book.stock > 0:
          # Create borrowed book
          BorrowedBook.objects.create(member=member, book=book)

          # Update count and stock
          book.count = (book.count or 0) + 1
          book.stock -= 1
          book.save()

          messages.success(request, f"You borrowed '{book.title}' successfully.")
        else:
          messages.error(request, f"Sorry, '{book.title}' is out of stock.")
      else:
        messages.warning(request, "You already borrowed this book.")
      return redirect(request.META.get('HTTP_REFERER', '/home/homePage/'))
    else:
      return render(request, 'Home.html')
  return redirect(request.META.get('HTTP_REFERER', '#'))




def search_books(request):
  userType = None
  user_image = None
  username = None
  favorite_book_ids = []
  user = None
  stock=None
  query = request.GET.get('q', '')

  if query:
    # Search for books matching the query in title or author
    books = Books.objects.filter(
      Q(title__icontains=query) |
      Q(author__icontains=query)
    ).distinct()

    # Get favorite books if user is logged in
    if request.session.get('is_logged_in'):
      user = Members.objects.get(email=request.session.get('user_email'))
      favorite_book_ids = list(FavouriteBooks.objects.filter(member=user).values_list('book_id', flat=True))
      userType=user.user_type
      user_image = user.image.url if user.image else '/static/images/default-user.png'
      username = user.username
      stock=request.session.get('stock')
    return render(request, 'search_results.html', {
      'books': books,
      'query': query,
      'favorite_book_ids': favorite_book_ids,
      'is_logged_in': request.session.get('is_logged_in', False),
      'username': username,
      'user_image': user_image,
      'stock': stock,
      'userType': userType,
    })
  else:
    # If no query provided, redirect to home
    return redirect('/home/homePage/')


def buyBook(request, book_id):
  if request.method == 'POST':
    if request.session.get('is_logged_in'):
      user_email = request.session.get('user_email')
      member = get_object_or_404(Members, email=user_email)
      book = get_object_or_404(Books, id=book_id)

      # Check if already owned
      already_owned = OwnedBooks.objects.filter(member=member, book=book).exists()
      if already_owned:
        messages.info(request, f"You already own '{book.title}'.")
        return redirect(request.META.get('HTTP_REFERER', '/home/homePage/'))

      # Check if this is a purchase from borrowed books
      borrowed_book = BorrowedBook.objects.filter(member=member, book=book, returned=False).first()

      if borrowed_book:
        # If buying a borrowed book, mark it as returned and create an owned record
        borrowed_book.returned = True
        borrowed_book.save()

        # Create an OwnedBooks record for this purchase
        OwnedBooks.objects.create(member=member, book=book)

        # Note: We don't increase the count when buying a borrowed book
        # We also don't decrease stock since the book was already borrowed

        messages.success(request,
                         f"You purchased '{book.title}' successfully for ${book.buyPrice or book.calculated_buy_price}.")

      elif book.stock > 0:
        # Regular purchase flow (not from borrowed books)
        # Create an OwnedBooks record for this purchase
        OwnedBooks.objects.create(member=member, book=book)
        book.count = (book.count or 0) + 1
        # Update stock
        book.stock -= 1
        book.save()

        # In a real system, you would process payment
        # For this demo, we'll just show a success message
        messages.success(request,
                         f"You purchased '{book.title}' successfully for ${book.buyPrice or book.calculated_buy_price}.")
      else:
        messages.error(request, f"Sorry, '{book.title}' is out of stock.")

      # Redirect back to the page they came from
      return redirect(request.META.get('HTTP_REFERER', '/home/homePage/'))
    else:
      return redirect('/home/login/')
  return redirect(request.META.get('HTTP_REFERER', '/home/homePage/'))


@require_POST
def addFavorite(request, book_id):
  """Add a book to the user's favorites"""
  if not request.session.get('is_logged_in'):
    messages.error(request, "Please log in to add favorites")
    return redirect('/home/login/')

  try:
    # Get the user and book
    user_email = request.session.get('user_email')
    member = get_object_or_404(Members, email=user_email)
    book = get_object_or_404(Books, id=book_id)

    # Check if the book is already in favorites
    favorite_exists = FavouriteBooks.objects.filter(member=member, book=book).exists()

    if favorite_exists:
      # If already favorited, remove from favorites (toggle behavior)
      FavouriteBooks.objects.filter(member=member, book=book).delete()
      messages.success(request, f"'{book.title}' removed from your favorites.")
    else:
      # Add to favorites
      FavouriteBooks.objects.create(member=member, book=book)
      messages.success(request, f"'{book.title}' added to your favorites!")

    # Redirect back to the page the user was on
    return redirect(request.META.get('HTTP_REFERER', '/home/homePage/'))

  except Members.DoesNotExist:
    messages.error(request, "User not found")
  except Books.DoesNotExist:
    messages.error(request, "Book not found")
  except Exception as e:
    messages.error(request, f"An error occurred: {str(e)}")

  # If anything goes wrong, redirect back to the page the user was on
  return redirect(request.META.get('HTTP_REFERER', '/home/homePage/'))


def getFavoriteBooks(request):
  """Get the list of books favorited by the user"""
  if not request.session.get('is_logged_in'):
    messages.error(request, "Please log in to view favorites")
    return redirect('/home/login/')
  userType=None
  user_image = None
  username = None
  user = None
  try:
    user = Members.objects.get(email=request.session.get('user_email'))
    favorite_books = FavouriteBooks.objects.filter(member=user).select_related('book')
    userType=user.user_type
    user_image = user.image.url if user.image else '/static/images/default-user.png'
    username = user.username
    # Get favorite book IDs for heart icon display
    favorite_book_ids = list(favorite_books.values_list('book_id', flat=True))

    return render(request, 'favorites.html', {
      'is_logged_in': True,
      'user_image': user_image,
      'username': username,
      'favorite_books': favorite_books,
      'favorite_book_ids': favorite_book_ids,
      'userType': userType,
    })

  except Members.DoesNotExist:
    messages.error(request, "User not found")
  except Exception as e:
    messages.error(request, f"An error occurred: {str(e)}")

  return redirect('/home/homePage/')


def edit_books(request, book_id):
    userType = None
    user_image = None
    username = None
    user = None

    # نجيب بيانات اليوزر لو لوج إن
    if request.session.get('is_logged_in'):
        try:
            user = Members.objects.get(email=request.session.get('user_email'))
            user_image = user.image.url if user.image else '/static/images/default-user.png'
            username = user.username
            userType = user.user_type
        except Members.DoesNotExist:
            return None
        except Exception as e:
            print(f"Error getting user details: {e}")

    # نجيب الكتاب المطلوب تعديله
    book = get_object_or_404(Books, id=book_id)

    # لو الفورم submitted
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('homepage')  # غيرها حسب اسم صفحة التفاصيل عندك
    else:
        form = BookForm(instance=book)

    return render(request, 'edit-book.html', {
        'form': form,
        'is_logged_in': request.session.get('is_logged_in', False),
        'user_image': user_image,
        'username': username,
        'userType': userType,
    })

