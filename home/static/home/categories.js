document.addEventListener("DOMContentLoaded", function () {
  // Book preview in profile box functionality
  const bookCards = document.querySelectorAll('.book-card');
  const profileBox = document.querySelector('.profile-box');
  let activeBookCard = null; // Track active book card

  // Function to update profile box with book details
  function updateProfileBox(bookCard) {
    // Skip if same book is clicked again
    if (activeBookCard === bookCard) return;

    // Remove active class from previous active book card
    if (activeBookCard) {
      activeBookCard.classList.remove('book-card-active');
    }

    // Mark the new clicked card as active
    activeBookCard = bookCard;
    bookCard.classList.add('book-card-active');

    // Get book info from the clicked card
    const bookImage = bookCard.querySelector('img').src;
    const bookTitle = bookCard.querySelector('.book-title').textContent;
    const bookAuthor = bookCard.querySelector('.book-author').textContent;
    const bookDes = bookCard.querySelector('.book-des').textContent;
    const stock = bookCard.querySelector('.stock')?.textContent || "0";
    const count = bookCard.querySelector('.count')?.textContent || "0";

    // Get rating if available, otherwise use placeholder
    let bookRating = "N/A";
    const ratingElement = bookCard.querySelector('.book-rating span');
    if (ratingElement) {
      bookRating = ratingElement.textContent;
    }

    // Get prices
    const borrowPrice = bookCard.querySelector('.book-price')?.textContent || "$0.00";
    const buyPrice = bookCard.querySelector('.buy-price')?.textContent || "$0.00";
    const id = bookCard.querySelector('.book-id')?.textContent || "0";

    // Create star rating display
    let stars = "";
    if (bookRating !== "N/A") {
      const ratingNum = parseFloat(bookRating);
      for (let i = 1; i <= 5; i++) {
        if (i <= Math.floor(ratingNum)) {
          stars += "★"; // Full star
        } else if (i === Math.ceil(ratingNum) && ratingNum % 1 !== 0) {
          stars += "★"; // Half star (approximating with full star for simplicity)
        } else {
          stars += "☆"; // Empty star
        }
      }
      stars += ` ${bookRating}`;
    } else {
      stars = "★☆☆☆☆ Not rated";
    }

    // Create animation effect - fade out
    profileBox.classList.add('profile-box-fade');

    // Get page count
    let pages = bookCard.hasAttribute('data-pages')
      ? bookCard.getAttribute('data-pages')
      : Math.floor(Math.random() * 400) + 100;

    // Get rating count
    let reviewCount = bookCard.hasAttribute('data-rating-count')
      ? bookCard.getAttribute('data-rating-count')
      : Math.floor(Math.random() * 1000) + 50;

    // Get category name - NEW IMPROVED VERSION
    let bookCategory = "Uncategorized";

    // First try to get from hidden category element
    const categoryElement = bookCard.querySelector('.book-category');
    if (categoryElement) {
      bookCategory = categoryElement.textContent.trim();
    }
    // Then try data-category-name attribute
    else if (bookCard.hasAttribute('data-category-name')) {
      bookCategory = bookCard.getAttribute('data-category-name');
    }
    // Then try active tag
    else {
      const activeTag = document.querySelector('.tag.active');
      if (activeTag && !activeTag.textContent.includes('All')) {
        bookCategory = activeTag.textContent.split('(')[0].trim();
      }
    }

    // After fade out completes, update content and fade in
    setTimeout(() => {
      // Update profile box content
      profileBox.innerHTML = `
        <img src="${bookImage}" alt="${bookTitle}">
        <div class="title">${bookTitle}</div>
        <div class="category">${bookCategory}</div>
        <div class="rating">${stars}</div>
        <div class="meta">Author: ${bookAuthor}</div>
        <div class="meta">${bookDes}</div>
        
        <div class="meta-row">
          <span class="meta">${pages} Pages</span>
          <span class="meta-separator"></span>
          <span class="meta">${reviewCount} Ratings</span>
        </div>
        ${ document.body.getAttribute('data-user-type') === 'Admin' ? `<div class="meta-row">
            <div class="meta">Stock: ${stock}</div>
            <span class="meta-separator"></span>
            <div class="meta">Count: ${count}</div>
          </div>` 
          : `<div class="meta">Borrow: ${borrowPrice}</div>
            <span class="meta-separator"></span>
            <div class="meta">Buy: ${buyPrice}</div>`}

        
        <div style="display: flex; gap: 10px; width: 100%; margin-top: 10px;">
          ${
            document.body.getAttribute('data-user-type') === 'Admin' 
              ? `
                <button class="profile-edit-btn" style="flex: 1; background-color:#4361ee">Edit</button>
                <button class="profile-delete-btn" style="flex: 1; background-color: #ff5151">Delete</button>
              `
              : `
                <button class="profile-borrow-btn" style="flex: 1; background-color: #4361ee">Borrow</button>
                <button class="profile-buy-btn" style="flex: 1; background-color: #10b981">Buy</button>
              `
          }
        </div>
      `;



      // Remove fade class to trigger fade-in animation
      setTimeout(() => {
        profileBox.classList.remove('profile-box-fade');
      }, 50);

      // Add event listeners to the new buttons
      const borrowBtn = profileBox.querySelector('.profile-borrow-btn');
      const buyBtn = profileBox.querySelector('.profile-buy-btn');
      const editBtn = profileBox.querySelector('.profile-edit-btn');
      const deleteBtn = profileBox.querySelector('.profile-delete-btn');

      // Find the original buttons on the book card
      const originalBorrowBtn = bookCard.querySelector('.borrow-btn');
      const originalBuyBtn = bookCard.querySelector('.buy-btn');
      const originalEditBtn = bookCard.querySelector('.edit-btn');
      const originalDeleteBtn = bookCard.querySelector('.delete-btn');

      if(deleteBtn && originalDeleteBtn){
        deleteBtn.addEventListener('click', () => {
          originalDeleteBtn.click();
        });
      }

      if(editBtn && originalEditBtn){
        editBtn.addEventListener('click', () => {
          originalEditBtn.click();
        });
      }

      // Link the new buttons to the original buttons' actions
      if (borrowBtn && originalBorrowBtn) {
        borrowBtn.addEventListener('click', () => {
          originalBorrowBtn.click();
        });
      }

      if (buyBtn && originalBuyBtn) {
        buyBtn.addEventListener('click', () => {
          originalBuyBtn.click();
        });
      }
    }, 300);
  }

  // Initialize with the first book
  const initializeFirstBook = () => {
    if (bookCards.length > 0) {
      updateProfileBox(bookCards[0]);
    }
  };

  // Add click event to all book cards
  bookCards.forEach(bookCard => {
    bookCard.addEventListener('click', function(e) {
      // Only trigger if click wasn't on a button
      if (!e.target.classList.contains('borrow-btn') &&
          !e.target.classList.contains('buy-btn')) {
        updateProfileBox(this);
      }
    });
  });

  // Initialize with a small delay to ensure DOM is fully loaded
  setTimeout(initializeFirstBook, 500);
});
