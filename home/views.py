from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.core.exceptions import MultipleObjectsReturned
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.views.decorators.http import require_GET, require_POST
from django.db import models
from .models import Members, Books, BorrowedBook, Category, FavouriteBooks, OwnedBooks
from collections import Counter
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from .forms import BookForm
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

def categoriesPage(request):
  categories = Category.objects.annotate(
    book_count=Count('books')
  ).order_by('-book_count')
  category_id = request.GET.get('category_id', 'all')
  current_path = request.path
  user_image = None
  username = None
  userType = None
  favorite_book_ids = []
  books = []
  total=0
  if request.session.get('is_logged_in'):
    try:
      user = Members.objects.get(email=request.session.get('user_email'))
      user_image = user.image.url if user.image else '/static/images/default-user.png'
      username = user.username
      userType = user.user_type
      borrowed_book_ids = BorrowedBook.objects.filter(
        member=user, returned=False
      ).values_list('book_id', flat=True)

      owned_book_ids = OwnedBooks.objects.filter(
        member=user
      ).values_list('book_id', flat=True)
      borrowedBooks=BorrowedBook.objects.all()
      ownedBooks=OwnedBooks.objects.all()
      for borrowed in borrowedBooks:
        total+= borrowed.book.borrowPrice
      for owned in ownedBooks:
        total+=owned.book.buyPrice

      favorite_book_ids = FavouriteBooks.objects.filter(member=user).values_list('book_id', flat=True)
    except Members.DoesNotExist:
      pass
  if category_id == 'all':
    if '/home/categories/' in current_path:
      books = Books.objects.all().order_by('-rating', '-ratingCount')
    else:
      books = Books.objects.all().order_by('-rating', '-ratingCount')[:12]
  else:
    try:
      books = Books.objects.filter(book_category_id=category_id).order_by('-rating', '-ratingCount')
      if books.count() < 12:
        category = Category.objects.get(id=category_id)
        additional_books = Books.objects.filter(
          category=category.name
        ).exclude(
          id__in=books.values_list('id', flat=True)
        ).order_by('-rating', '-ratingCount')
        if '/home/categories/' in current_path:
          books = list(books) + list(additional_books)
        else:
          books = list(books) + list(additional_books[:12 - books.count()])
    except (ValueError, Category.DoesNotExist):
      books = []
  for book in books:
    if book.borrowPrice and not book.buyPrice:
      book.save()

  return render(request, 'categories.html', {
    'is_logged_in': request.session.get('is_logged_in', False),
    'categories': categories,
    'user_image': user_image,
    'username': username,
    'favorite_book_ids': list(favorite_book_ids),
    'userType': userType,
    'books': books,
    'current_category_id': category_id,
    'is_home_page': '/home/homePage/' in current_path,
    'borrowed_book_ids': borrowed_book_ids,
    'owned_book_ids': owned_book_ids,
    'total':total,
  })


def get_recommended_books(user, limit=20):
  try:
    borrowed_books = BorrowedBook.objects.filter(member=user)
    owned_books = OwnedBooks.objects.filter(member=user)
    if not borrowed_books.exists() and not owned_books.exists():
      return []
    borrowed_book_ids = borrowed_books.values_list('book_id', flat=True)
    owned_book_ids = owned_books.values_list('book_id', flat=True)
    excluded_book_ids = set(borrowed_book_ids) | set(owned_book_ids)
    user_books = Books.objects.filter(id__in=excluded_book_ids)
    category_ids = []
    category_names = []
    for book in user_books:
      if book.book_category_id:
        category_ids.append(book.book_category_id)
      elif book.category:
        category_names.append(book.category)
    category_id_counter = Counter(category_ids)
    top_category_ids = [cat_id for cat_id, count in category_id_counter.most_common(3)]
    category_name_counter = Counter(category_names)
    top_category_names = [cat for cat, count in category_name_counter.most_common(3) if cat is not None]
    if not top_category_ids and not top_category_names:
      return []
    recommended_books_query = Books.objects.exclude(id__in=excluded_book_ids)
    if top_category_ids:
      recommended_books = recommended_books_query.filter(
        book_category_id__in=top_category_ids
      ).order_by(
        '-rating', '-ratingCount', 'title'
      )[:limit]
      if recommended_books.count() >= limit:
        return recommended_books
      remaining_limit = limit - recommended_books.count()
      recommended_books_from_names = recommended_books_query.filter(
        category__in=top_category_names
      ).exclude(
        id__in=recommended_books.values_list('id', flat=True)
      ).order_by(
        '-rating', '-ratingCount', 'title'
      )[:remaining_limit]
      return list(recommended_books) + list(recommended_books_from_names)
    else:
      return recommended_books_query.filter(
        category__in=top_category_names
      ).order_by(
        '-rating', '-ratingCount', 'title'
      )[:limit]
  except Exception as e:
    print(f"Error generating recommendations: {e}")
    return []


def homePage(request):
  userType = None
  user_image = None
  username = None
  user = None
  recommended_books = []
  favorite_book_ids = []
  borrowed_book_ids = []
  owned_book_ids = []
  total=0
  if request.session.get('is_logged_in'):
    try:
      user = Members.objects.get(email=request.session.get('user_email'))
      user_image = user.image.url if user.image else '/static/images/default-user.png'
      username = user.username
      userType = user.user_type
      borrowed_book_ids = BorrowedBook.objects.filter(returned=False, member=user).values_list('book_id', flat=True)
      owned_book_ids = OwnedBooks.objects.filter(
        member=user
      ).values_list('book_id', flat=True)
      borrowedBooks=BorrowedBook.objects.all()
      ownedBooks=OwnedBooks.objects.all()
      for borrowed in borrowedBooks:
        total+= borrowed.book.borrowPrice
      for owned in ownedBooks:
        total+=owned.book.buyPrice
      recommended_books = get_recommended_books(user)
      for book in recommended_books:
        if book.borrowPrice and not book.buyPrice:
          book.save()
      favorite_book_ids = FavouriteBooks.objects.filter(member=user).values_list('book_id', flat=True)
    except Members.DoesNotExist:
      pass
    except Exception as e:
      print(f"Error getting user details: {e}")
  try:
    books = Books.objects.all().order_by('-rating')[:20]
    for book in books:
      if book.borrowPrice and not book.buyPrice:
        book.save()
  except Exception as e:
    print(f"Error fetching books: {e}")
    books = []
  try:
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
    'borrowed_book_ids': borrowed_book_ids,
    'owned_book_ids': owned_book_ids,
    'total':total,
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
        return redirect('/home/homePage/')
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
      return redirect('login')
    except Exception as e:
      return render(request, 'signup.html')
  return render(request, 'signup.html')



def adminDashboard(request):
  if not request.session.get('is_logged_in') or request.session.get('user_type') != 'Admin':
    return redirect('login')

  try:
    user = Members.objects.get(email=request.session.get('user_email'))
  except Members.DoesNotExist:
    return redirect('login')

  thirty_days_ago = timezone.now() - timedelta(days=30)
  seven_days_ago = timezone.now() - timedelta(days=7)
  borrowedBooks = BorrowedBook.objects.all()
  ownedBooks = OwnedBooks.objects.all()
  total=0
  for borrowed in borrowedBooks:
    total += borrowed.book.borrowPrice
  for owned in ownedBooks:
    total += owned.book.buyPrice

  stats = {
    'total_books': Books.objects.count(),
    'total_members': Members.objects.count(),
    'active_borrows': BorrowedBook.objects.filter(returned=False).count(),
    'total_borrows': BorrowedBook.objects.count(),
    'total_purchases': OwnedBooks.objects.count(),

    'recent_books': Books.objects.order_by('-id')[:5],
    'recent_members': Members.objects.order_by('-id')[:5],
    'recent_borrows': BorrowedBook.objects.select_related('book', 'member')
                      .filter(returned=False)
                      .order_by('-borrowed_date')[:5],

    'categories': Category.objects.annotate(book_count=Count('books'))
                  .order_by('-book_count')[:5],

    'popular_books': Books.objects.annotate(
      total_activity=Count('borrowedbook') + Count('ownedbooks')
    ).order_by('-total_activity')[:5],

    'recent_activity': {
      'books_added': Books.objects.filter(id__gte=Books.objects.last().id - 10).count(),
      'new_members': Members.objects.filter(id__gte=Members.objects.last().id - 10).count(),
      'borrows': BorrowedBook.objects.filter(borrowed_date__gte=thirty_days_ago).count(),
      'purchases': OwnedBooks.objects.filter(purchase_date__gte=thirty_days_ago).count(),
      'recent_borrows': BorrowedBook.objects.filter(borrowed_date__gte=seven_days_ago).count(),
      'recent_purchases': OwnedBooks.objects.filter(purchase_date__gte=seven_days_ago).count()
    },

    'low_stock_books': Books.objects.filter(stock__lte=5).order_by('stock')[:5],

    'active_members': Members.objects.annotate(
      borrow_count=Count('borrowedbook', filter=Q(borrowedbook__returned=False))
    ).order_by('-borrow_count')[:5]
  }

  return render(request, 'admin-dashboard.html', {
    'is_logged_in': True,
    'user_image': user.image.url if user.image else '/static/images/default-user.png',
    'username': user.username,
    'userType': user.user_type,
    'stats': stats,
    'current_page': 'admin_dashboard',
    'total':total,
  })

def addBooks(request):
  categories = Category.objects.all().order_by('name')
  user_image = None
  username = None
  userType = None
  user = None
  user = Members.objects.get(email=request.session.get('user_email'))
  userType = request.session.get('user_type')
  user_image = user.image.url if user.image else '/static/images/default-user.png'
  username = user.username
  total=0
  borrowedBooks = BorrowedBook.objects.all()
  ownedBooks = OwnedBooks.objects.all()
  for borrowed in borrowedBooks:
    total += borrowed.book.borrowPrice
  for owned in ownedBooks:
    total += owned.book.buyPrice

  if request.method == 'POST':
    title = request.POST.get('title')
    author = request.POST.get('author')
    description = request.POST.get('description')
    pageCount = request.POST.get('pageCount')
    borrowPrice = request.POST.get('borrowPrice')
    stock = request.POST.get('stock')
    category_id = request.POST.get('book_category')
    published = request.POST.get('published')
    image = request.FILES.get('image')
    rating = request.POST.get('rating')
    ratingCount = request.POST.get('ratingCount')
    if title and author and borrowPrice and stock and category_id:
      try:
        category = Category.objects.get(id=category_id)
        book = Books(
          title=title,
          author=author,
          description=description,
          pageCount=pageCount if pageCount else 0,
          borrowPrice=Decimal(borrowPrice),
          stock=int(stock),
          book_category=category,
          category=category.name,
          published=published if published else None,
          rating=rating,
          ratingCount=ratingCount,
        )
        if image:
          book.image = image
        book.save()
        messages.success(request, f"Book '{title}' added successfully!")
        return redirect('/home/homePage/')
      except Exception as e:
        messages.error(request, f"Error adding book: {str(e)}")
    else:
      messages.error(request, "Please fill all required fields")
  context = {
    'categories': categories,
    'is_logged_in': request.session.get('is_logged_in', False),
    'user_image': user_image,
    'username': username,
    'userType': userType,
    'user': user,
    'total':total,
  }
  return render(request, 'add-books.html', context)


def unauthorized(request):
  return render(request, 'unauthorized.html')


def returnBook(request, book_id):
  if not request.session.get('is_logged_in'):
    messages.error(request, "You need to be logged in to return books.")
    return redirect('/home/login/')
  try:
    user_email = request.session.get('user_email')
    member = get_object_or_404(Members, email=user_email)
    book = get_object_or_404(Books, id=book_id)
    if member.user_type == 'Admin':
      borrowed_book = BorrowedBook.objects.filter(
        book=book,
        returned=False
      ).first()
    else:
      borrowed_book = BorrowedBook.objects.filter(
        member=member,
        book=book,
        returned=False
      ).first()
    if not borrowed_book:
      messages.error(request, "No active borrow record found for this book.")
      return redirect(request.META.get('HTTP_REFERER', '/home/borrowedBooks/'))
    borrowed_book.returned = True
    borrowed_book.save()
    book.stock = models.F('stock') + 1
    book.count = models.F('count') - 1
    book.save(update_fields=['stock', 'count'])
    messages.success(request, f"Successfully returned '{book.title}'")
    if member.user_type == 'Admin':
      messages.info(request, f"Returned on behalf of {borrowed_book.member.username}")
    return redirect(request.META.get('HTTP_REFERER', '/home/borrowedBooks/'))
  except Exception as e:
    print(f"Error returning book: {e}")
    messages.error(request, "An error occurred while processing your return.")
    return redirect(request.META.get('HTTP_REFERER', '/home/borrowedBooks/'))


def borrowBook(request, book_id):
  if request.session.get('is_logged_in'):
    user_email = request.session.get('user_email')
    member = get_object_or_404(Members, email=user_email)
    book = get_object_or_404(Books, id=book_id)
    borrowed_books = BorrowedBook.objects.filter(member=member, returned=False)
    already_borrowed = BorrowedBook.objects.filter(member=member, book=book, returned=False).exists()
    if not already_borrowed:
      if book.stock > 0:
        BorrowedBook.objects.create(member=member, book=book)
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


def search_books(request):
  borrowed_book_ids = []
  owned_book_ids = []
  userType = None
  user_image = None
  username = None
  favorite_book_ids = []
  user = None
  stock = None
  total=0
  query = request.GET.get('q', '')
  if query:
    books = Books.objects.filter(
      Q(title__icontains=query) |
      Q(author__icontains=query)
    ).distinct()
    if request.session.get('is_logged_in'):
      user = Members.objects.get(email=request.session.get('user_email'))
      favorite_book_ids = list(FavouriteBooks.objects.filter(member=user).values_list('book_id', flat=True))
      userType = user.user_type
      user_image = user.image.url if user.image else '/static/images/default-user.png'
      username = user.username
      stock = request.session.get('stock')
      borrowed_book_ids = BorrowedBook.objects.filter(
        member=user, returned=False
      ).values_list('book_id', flat=True)
      owned_book_ids = OwnedBooks.objects.filter(
        member=user
      ).values_list('book_id', flat=True)
      borrowedBooks=BorrowedBook.objects.all()
      ownedBooks=OwnedBooks.objects.all()
      for borrowed in borrowedBooks:
        total+= borrowed.book.borrowPrice
      for owned in ownedBooks:
        total+=owned.book.buyPrice

    return render(request, 'search_results.html', {
      'books': books,
      'query': query,
      'favorite_book_ids': favorite_book_ids,
      'is_logged_in': request.session.get('is_logged_in', False),
      'username': username,
      'user_image': user_image,
      'stock': stock,
      'userType': userType,
      'borrowed_book_ids': borrowed_book_ids,
      'owned_book_ids': owned_book_ids,
      'total':total,
    })
  else:
    return redirect('/home/homePage/')


def buyBook(request, book_id):
  if request.session.get('is_logged_in'):
    user_email = request.session.get('user_email')
    member = get_object_or_404(Members, email=user_email)
    book = get_object_or_404(Books, id=book_id)
    already_owned = OwnedBooks.objects.filter(member=member, book=book).exists()
    if already_owned:
      messages.info(request, f"You already own '{book.title}'.")
      return redirect(request.META.get('HTTP_REFERER', '/home/homePage/'))
    borrowed_book = BorrowedBook.objects.filter(member=member, book=book, returned=False).first()
    if borrowed_book:
      borrowed_book.returned = True
      borrowed_book.save()
      OwnedBooks.objects.create(member=member, book=book)
      messages.success(request, f"You purchased '{book.title}' successfully for ${book.buyPrice or book.calculated_buy_price}.")
    elif book.stock > 0:
      OwnedBooks.objects.create(member=member, book=book)
      book.count = (book.count or 0) + 1
      book.stock -= 1
      book.save()
      messages.success(request, f"You purchased '{book.title}' successfully for ${book.buyPrice or book.calculated_buy_price}.")
    else:
      messages.error(request, f"Sorry, '{book.title}' is out of stock.")
    return redirect(request.META.get('HTTP_REFERER', '/home/homePage/'))
  else:
    return redirect('/home/login/')


@require_POST
def addFavorite(request, book_id):
  if not request.session.get('is_logged_in'):
    messages.error(request, "Please log in to add favorites")
    return redirect('/home/login/')
  try:
    user_email = request.session.get('user_email')
    member = get_object_or_404(Members, email=user_email)
    book = get_object_or_404(Books, id=book_id)
    favorite_exists = FavouriteBooks.objects.filter(member=member, book=book).exists()
    if favorite_exists:
      FavouriteBooks.objects.filter(member=member, book=book).delete()
      messages.success(request, f"'{book.title}' removed from your favorites.")
    else:
      FavouriteBooks.objects.create(member=member, book=book)
      messages.success(request, f"'{book.title}' added to your favorites!")
    return redirect(request.META.get('HTTP_REFERER', '/home/homePage/'))
  except Members.DoesNotExist:
    messages.error(request, "User not found")
  except Books.DoesNotExist:
    messages.error(request, "Book not found")
  except Exception as e:
    messages.error(request, f"An error occurred: {str(e)}")
  return redirect(request.META.get('HTTP_REFERER', '/home/homePage/'))


def getFavoriteBooks(request):
  if not request.session.get('is_logged_in'):
    messages.error(request, "Please log in to view favorites")
    return redirect('/home/login/')
  try:
    user = Members.objects.get(email=request.session.get('user_email'))
    total=0
    favorite_books = FavouriteBooks.objects.filter(member=user).select_related('book')
    borrowed_book_ids = BorrowedBook.objects.filter(
      member=user, returned=False
    ).values_list('book_id', flat=True)
    owned_book_ids = OwnedBooks.objects.filter(
      member=user
    ).values_list('book_id', flat=True)
    borrowedBooks = BorrowedBook.objects.all()
    ownedBooks = OwnedBooks.objects.all()
    for borrowed in borrowedBooks:
      total += borrowed.book.borrowPrice
    for owned in ownedBooks:
      total += owned.book.buyPrice
    favorite_book_ids = list(favorite_books.values_list('book_id', flat=True))
    return render(request, 'favorites.html', {
      'is_logged_in': True,
      'user_image': user.image.url if user.image else '/static/images/default-user.png',
      'username': user.username,
      'favorite_books': favorite_books,
      'favorite_book_ids': favorite_book_ids,
      'userType': user.user_type,
      'borrowed_book_ids': list(borrowed_book_ids),
      'owned_book_ids': list(owned_book_ids),
      'total':total,
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
  total=0
  if request.session.get('is_logged_in'):
    try:
      user = Members.objects.get(email=request.session.get('user_email'))
      user_image = user.image.url if user.image else '/static/images/default-user.png'
      username = user.username
      userType = user.user_type
      borrowedBooks=BorrowedBook.objects.all()
      ownedBooks=OwnedBooks.objects.all()
      for borrowed in borrowedBooks:
        total+= borrowed.book.borrowPrice
      for owned in ownedBooks:
        total+=owned.book.buyPrice

    except Members.DoesNotExist:
      return None
    except Exception as e:
      print(f"Error getting user details: {e}")
  book = get_object_or_404(Books, id=book_id)
  if request.method == 'POST':
    form = BookForm(request.POST, instance=book)
    if form.is_valid():
      form.save()
      return redirect('homepage')
  else:
    form = BookForm(instance=book)
  return render(request, 'edit-book.html', {
    'form': form,
    'is_logged_in': request.session.get('is_logged_in', False),
    'user_image': user_image,
    'username': username,
    'userType': userType,
    'total':total,
  })


def delete_books(request, book_id):
  book = Books.objects.get(id=book_id)
  book.delete()
  return redirect(request.META.get('HTTP_REFERER', '/home/homePage/'))


def borrowed_books_view(request):
  userType = None
  user_image = None
  username = None
  user = None
  favorite_book_ids = []
  total=0
  if request.session.get('is_logged_in'):
    try:
      user = Members.objects.get(email=request.session.get('user_email'))
      user_image = user.image.url if user.image else '/static/images/default-user.png'
      username = user.username
      userType = user.user_type
      favorite_book_ids = FavouriteBooks.objects.filter(member=user).values_list('book_id', flat=True)
      borrowedBooks=BorrowedBook.objects.all()
      ownedBooks=OwnedBooks.objects.all()
      for borrowed in borrowedBooks:
        total+= borrowed.book.borrowPrice
      for owned in ownedBooks:
        total+=owned.book.buyPrice

    except Members.DoesNotExist:
      pass
    except Exception as e:
      print(f"Error getting user details: {e}")
  member_data = []
  try:
    if userType == 'Admin':
      members = Members.objects.all()
      for member in members:
        borrowed = BorrowedBook.objects.filter(member=member, returned=False)
        owned = OwnedBooks.objects.filter(member=member)
        member_data.append({
          'member': member,
          'borrowed_books': borrowed,
          'owned_books': owned
        })
    else:
      if user:
        borrowed = BorrowedBook.objects.filter(member=user, returned=False)
        owned = OwnedBooks.objects.filter(member=user)
        member_data.append({
          'member': user,
          'borrowed_books': borrowed,
          'owned_books': owned
        })
  except Exception as e:
    print(f"Error fetching borrowed/owned books: {e}")
  return render(request, 'borrowed-books.html', {
    'is_logged_in': request.session.get('is_logged_in', False),
    'user_image': user_image,
    'username': username,
    'member_data': member_data,
    'favorite_book_ids': list(favorite_book_ids),
    'userType': userType,
    'total':total,
  })
