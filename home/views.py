from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.views.decorators.http import require_GET, require_POST
from .models import Members, Books, BorrowedBook, Category, FavouriteBooks, OwnedBooks


from django.db.models import Count
from collections import Counter

def categoriesPage(request):
    """View to display all categories and their books"""
    # Get all categories ordered by name
    categories = Category.objects.annotate(
        book_count=Count('books')
    ).order_by('-book_count')

    user_image = None
    username = None
    favorite_book_ids = []
    
    if request.session.get('is_logged_in'):
        try:
            user = Members.objects.get(email=request.session.get('user_email'))
            user_image = user.image.url if user.image else '/static/images/default-user.png'
            username = user.username
            
            # Get user's favorite books
            favorite_book_ids = FavouriteBooks.objects.filter(member=user).values_list('book_id', flat=True)
        except Members.DoesNotExist:
            pass
        except Exception as e:
            print(f"Error getting user details: {e}")
    
    return render(request, 'categories.html', {
        'is_logged_in': request.session.get('is_logged_in', False),
        'categories': categories,
        'user_image': user_image,
        'username': username,
        'favorite_book_ids': list(favorite_book_ids),
    })

def get_recommended_books(user, limit=12):
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
        books = Books.objects.all().order_by('-rating')[:12]

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
                return redirect('/home/availableBooks/')
        except Members.DoesNotExist:
            messages.error(request, "Invalid email or password.")

    return render(request, 'login.html')


def Logout(request):
    request.session.flush()
    return redirect('/home/homePage/')


def signup(request):
    template = loader.get_template('signup.html')
    return HttpResponse(template.render({}, request))


def borrowedBooksUser(request):
    user_email = request.session.get('user_email')
    member = get_object_or_404(Members, email=user_email)
    borrowed_books = BorrowedBook.objects.filter(member=member, returned=False)

    return render(request, 'borrowed-books-user.html', {'borrowed_books': borrowed_books})


def borrowedBooksAdmin(request):
    user_email = request.session.get('user_email')
    member = get_object_or_404(Members, email=user_email)
    borrowed_books = BorrowedBook.objects.filter(member=member, returned=False)
    all_borrowed_books = Books.objects.all()
    return render(request, 'borrowed-books-admin.html', {'borrowed_books': borrowed_books, 'all_borrowed_books': all_borrowed_books})


def adminDashboard(request):
    template = loader.get_template('admin-dashboard.html')
    return HttpResponse(template.render({}, request))


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


def availableBooks(request):
    # Get all books and ensure they have buyPrice values
    books = Books.objects.all()
    
    # Ensure all books have their buyPrice values
    for book in books:
        if book.borrowPrice and not book.buyPrice:
            book.save()  # This will trigger the save() method that calculates buyPrice
    
    context = {
        'books': books,
        'current_member': None
    }
    
    # Add current member info if logged in
    if request.session.get('is_logged_in'):
        try:
            user_email = request.session.get('user_email')
            current_member = Members.objects.get(email=user_email)
            context['current_member'] = current_member
        except Members.DoesNotExist:
            pass
    
    return render(request, 'available-books.html', context)


def borrowBook(request, book_id):
    if request.method == 'POST':
        if request.session.get('is_logged_in'):
            user_email = request.session.get('user_email')
            member = get_object_or_404(Members, email=user_email)
            book = get_object_or_404(Books, id=book_id)

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
            return redirect('/home/login/')
    return redirect(request.META.get('HTTP_REFERER', '#'))

def buyBook(request, book_id):
    if request.method == 'POST':
        if request.session.get('is_logged_in'):
            user_email = request.session.get('user_email')
            member = get_object_or_404(Members, email=user_email)
            book = get_object_or_404(Books, id=book_id)

            if book.stock > 0:
                # We don't create a BorrowedBook record because the book is purchased, not borrowed
                
                # Update stock
                book.stock -= 1
                book.save()

                # In a real system, you would process payment and create a purchase record
                # For this demo, we'll just show a success message
                messages.success(request, f"You purchased '{book.title}' successfully for ${book.buyPrice or book.calculated_buy_price}.")
            else:
                messages.error(request, f"Sorry, '{book.title}' is out of stock.")
            return redirect('/home/availableBooks/')
        else:
            return redirect('/home/login/')
    return redirect('/home/availableBooks/')

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
    
    try:
        user_email = request.session.get('user_email')
        member = get_object_or_404(Members, email=user_email)
        favorite_books = FavouriteBooks.objects.filter(member=member).select_related('book')
        
        user_image = member.image.url if member.image else '/static/images/default-user.png'
        username = member.username
        
        # Get favorite book IDs for heart icon display
        favorite_book_ids = list(favorite_books.values_list('book_id', flat=True))
        
        return render(request, 'favorites.html', {
            'is_logged_in': True,
            'user_image': user_image,
            'username': username,
            'favorite_books': favorite_books,
            'favorite_book_ids': favorite_book_ids,
        })
        
    except Members.DoesNotExist:
        messages.error(request, "User not found")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
    
    return redirect('/home/homePage/')

@require_GET
def all_filter_books_by_category(request, category_id=None):
    """
    Returns books filtered by category in JSON format.
    
    Can be called in two ways:
    1. /api/books/?category_id=X - category_id comes from query parameters
    2. /api/books-by-category/X/ - category_id comes from URL path
    
    If category_id is 'all', returns all books
    """
    try:
        # If category_id is not in path params, get from query params
        if category_id is None:
            category_id = request.GET.get('category_id', 'all')
            

        if category_id == 'all':
            books = Books.objects.all().order_by('-rating', '-ratingCount')
        else:
            # Try to get books by category ID first
            try:
                category_id = int(category_id)
                books = Books.objects.filter(book_category_id=category_id).order_by('-rating', '-ratingCount')
                
            except (ValueError, Category.DoesNotExist):
                # If category_id is not a valid integer or category doesn't exist,
                # return an empty list
                books = []
        
        # Prepare the data for JSON response
        books_data = []
        for book in books:
            # Ensure buyPrice is set
            if book.borrowPrice and not book.buyPrice:
                book.save()  # This will trigger the save() method that calculates buyPrice
                
            # Get category name
            category_name = book.get_category or "Uncategorized"
            
            books_data.append({
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'image': book.get_image_url,
                'rating': float(book.rating) if book.rating else 0,
                'borrowPrice': float(book.borrowPrice) if book.borrowPrice else 0,
                'buyPrice': float(book.buyPrice) if book.buyPrice else 0,
                'category': category_name,
                'pageCount': book.pageCount,
                'ratingCount': book.ratingCount or 0
            })
        
        return JsonResponse({
            'success': True,
            'books': books_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def filter_books_by_category(request, category_id=None):
    """
    Returns books filtered by category in JSON format.

    Can be called in two ways:
    1. /api/books/?category_id=X - category_id comes from query parameters
    2. /api/books-by-category/X/ - category_id comes from URL path

    If category_id is 'all', returns all books
    """
    try:
        # If category_id is not in path params, get from query params
        if category_id is None:
            category_id = request.GET.get('category_id', 'all')

        limit = 20  # Default limit for category-specific books

        # If "all" is requested, show more books
        if category_id == 'all':
            limit = 50
            books = Books.objects.all().order_by('-rating', '-ratingCount')[:limit]
        else:
            # Try to get books by category ID first
            try:
                category_id = int(category_id)
                books = Books.objects.filter(book_category_id=category_id).order_by('-rating', '-ratingCount')[:limit]

                # If we don't have enough books, we might need to use the string category field too
                if books.count() < limit:
                    # Get the category name
                    category_name = Category.objects.get(id=category_id).name
                    # Get additional books using the string category field
                    more_books = Books.objects.filter(
                        category=category_name
                    ).exclude(
                        id__in=books.values_list('id', flat=True)
                    ).order_by(
                        '-rating', '-ratingCount'
                    )[:limit - books.count()]

                    # Combine the querysets
                    books = list(books) + list(more_books)
            except (ValueError, Category.DoesNotExist):
                # If category_id is not a valid integer or category doesn't exist,
                # return an empty list
                books = []

        # Get favorite books if user is logged in
        favorite_book_ids = []
        if request.session.get('is_logged_in'):
            try:
                user_email = request.session.get('user_email')
                member = Members.objects.get(email=user_email)
                favorite_book_ids = list(FavouriteBooks.objects.filter(member=member).values_list('book_id', flat=True))
            except:
                # If there's an error, just continue without favorites
                pass

        # Prepare the data for JSON response
        books_data = []
        for book in books:
            # Ensure buyPrice is set
            if book.borrowPrice and not book.buyPrice:
                book.save()  # This will trigger the save() method that calculates buyPrice

            # Get category name
            category_name = book.get_category or "Uncategorized"

            # Check if this book is in user's favorites
            is_favorite = book.id in favorite_book_ids

            books_data.append({
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'image': book.get_image_url,
                'rating': float(book.rating) if book.rating else 0,
                'borrowPrice': float(book.borrowPrice) if book.borrowPrice else 0,
                'buyPrice': float(book.buyPrice) if book.buyPrice else 0,
                'category': category_name,
                'pageCount': book.pageCount,
                'ratingCount': book.ratingCount or 0,
                'is_favorite': is_favorite
            })

        return JsonResponse({
            'success': True,
            'books': books_data,
            'is_logged_in': request.session.get('is_logged_in', False)
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

