document.addEventListener("DOMContentLoaded", function () {
  const earningsElement = document.querySelector(".earnings-this-month h3");
  let borrowedBooks = JSON.parse(localStorage.getItem("borrowedBooks")) || [];

  let totalEarnings = 0;
  borrowedBooks.forEach(book => {
    if (book.isBorrowed) {
      totalEarnings += (book.price || 0) * (book.count || 1);
    }
  });

  if (earningsElement) {
    earningsElement.textContent = `$${totalEarnings}`;
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const mostBorrowedImage = document.querySelector(".mostbook");
  let borrowedBooks = JSON.parse(localStorage.getItem("borrowedBooks")) || [];

  if (borrowedBooks.length > 0) {
    const mostBorrowed = borrowedBooks.reduce((max, book) => {
      return (book.count || 0) > (max.count || 0) ? book : max;
    });

    if (mostBorrowedImage && mostBorrowed.imagePath) {
      mostBorrowedImage.src = `../User Section/${mostBorrowed.imagePath}`;
      mostBorrowedImage.alt = mostBorrowed.title;

      mostBorrowedImage.onerror = function () {
        this.onerror = null;
        this.src = mostBorrowed.imagePath;
      };
    }
  }
});

