import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Library.settings')  # غيّر "Library" لو اسم مشروعك مختلف
django.setup()
import csv
import requests
from django.core.files.base import ContentFile
from home.models import Books  # غيّر yourapp حسب اسم الأبلكيشن بتاعك


def download_image(url):
  try:
    response = requests.get(url)
    if response.status_code == 200:
      filename = url.split('/')[-1]
      return ContentFile(response.content, name=filename)
  except Exception as e:
    print(f"Error downloading {url}: {e}" )
  return None


with open("filtered-books.csv", newline='', encoding='utf-8') as csvfile:
  reader = csv.DictReader(csvfile)
  for row in reader:
    image_file = download_image(row['thumbnail'])  # غيّر لو اسم العمود مختلف

    book = Books(
      title=row['title'],
      author=row['authors'],
      borrowPrice=row['price'],
      stock=row['stock'],
      pageCount=row['num_pages'],
      image=row['thumbnail'],
      rating=row['average_rating'],
      description=row['description'],
      category=row['categories'],
      published=row['published_year'],
      ratingCount=row['ratings_count'],
    )

    if image_file:
      book.image.save(image_file.name, image_file, save=True)
    else:
      book.save()
