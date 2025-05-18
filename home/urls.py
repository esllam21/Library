from tkinter.font import names
from django.urls import path
from . import views

urlpatterns = [
    path('', views.homePage, name='default'),
    path('homePage/', views.homePage, name='homepage'),
    path('login/', views.login, name="login"),
    path('logout/', views.Logout, name="logout"),
    path('signup/', views.signup, name="signup"),
    path('addBooks/', views.addBooks, name="addBook"),
    path('borrowedBooks/', views.borrowed_books_view, name="borrowBookAdmin"),
    path('adminDashboard/', views.adminDashboard, name="adminDashboard"),
    path('unauthorized/', views.unauthorized, name="unauthorized"),
    path('borrow/<int:book_id>/', views.borrowBook, name='borrowBook'),
    path('buy/<int:book_id>/', views.buyBook, name='buyBook'),
    path('return/<int:book_id>/', views.returnBook, name='returnBook'),
    path('add-favorite/<int:book_id>/', views.addFavorite, name='addFavorite'),
    path('favorites/', views.getFavoriteBooks, name='favorites'),
    path('search/', views.search_books, name='search_books'),
    path('categories/', views.categoriesPage, name='categories'),
    path('edit/<int:book_id>/', views.edit_books, name='editBook'),
    path('delete/<int:book_id>/', views.delete_books, name='deleteBook'),

]
