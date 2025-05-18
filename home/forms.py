# books/forms.py
from django import forms
from .models import Books


class BookForm(forms.ModelForm):
    class Meta:
        model = Books
        fields = ['title', 'author', 'pageCount', 'description', 'book_category', 'borrowPrice', 'buyPrice', 'stock', 'image']
