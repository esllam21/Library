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
    const bookDes=bookCard.querySelector('.book-des').textContent;
    
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
    
    // Try to get actual pageCount or use a default
    let pages;
    // Check if there's a pageCount data attribute
    if (bookCard.hasAttribute('data-pages')) {
      pages = bookCard.getAttribute('data-pages');
    } else {
      // Generate a random number for demo purposes
      pages = Math.floor(Math.random() * 400) + 100; // Random number between 100-500
    }
    
    // Get or generate rating count
    let reviewCount;
    if (bookCard.hasAttribute('data-rating-count')) {
      reviewCount = bookCard.getAttribute('data-rating-count');
    } else {
      // Generate a random number for demo purposes  
      reviewCount = Math.floor(Math.random() * 1000) + 50; // Random number of reviews
    }
    
    // Default category
    let bookCategory = "Fiction";
    
    // Try to find the category of this specific book
    // First check if this book has a specific data attribute with its category
    const categoryDataAttr = bookCard.getAttribute('data-category');
    if (categoryDataAttr) {
      bookCategory = categoryDataAttr;
    } else {
      // Try to find the book's category from the current section
      const bookSection = bookCard.closest('.featured, .categories');
      if (bookSection) {
        // Try to get category from tags that might be associated with this book
        const tagsContainer = bookSection.querySelector('.tags');
        if (tagsContainer) {
          // Get the active tag if possible
          const activeTag = tagsContainer.querySelector('.tag.active');
          if (activeTag && activeTag.textContent !== "All") {
            bookCategory = activeTag.textContent.trim();
          } else {
            // If no active tag, get the first non-"All" tag
            const tags = tagsContainer.querySelectorAll('.tag');
            for (const tag of tags) {
              if (tag.textContent.trim() !== "All") {
                bookCategory = tag.textContent.trim();
                break;
              }
            }
          }
        }
        
        // If we still don't have a specific category, try to get the section title
        if (bookCategory === "Fiction") {
          const sectionHeader = bookSection.querySelector('h3');
          if (sectionHeader && sectionHeader.textContent) {
            const headerText = sectionHeader.textContent.trim();
            // Only use section header if it's a likely category name (not "Recommended for You" or "Discover")
            if (headerText !== "Recommended for You" && 
                headerText !== "Discover" && 
                headerText !== "Featured" &&
                headerText !== "New Arrivals") {
              bookCategory = headerText;
            }
          }
        }
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
        <div class="meta"> ${bookDes}</div>
        
        <div class="meta-row">
          <span class="meta">${pages} Pages</span>
          <span class="meta-separator"></span>
          <span class="meta">${reviewCount} Ratings</span>
        </div>
        
        <div class="meta">Borrow: ${borrowPrice}</div>
        <div class="meta">Purchase: ${buyPrice}</div>
        
        <div style="display: flex; gap: 10px; width: 100%; margin-top: 10px;">
                ${
                    document.body.getAttribute('data-user-type') === 'Admin' ? `
<!--                      <a href="/home/edit/${id}">-->
                        <button class="profile-edit-btn" style="flex: 1; background-color:#4361ee ">Edit</button>
<!--                      </a>-->
                      <button class="profile-buy-btn" style="flex: 1; background-color: #ff5151">Delete</button>`
                        : `<button class="profile-borrow-btn" style="flex: 1; background-color: #4361ee">Borrow</button>
                          <button class="profile-buy-btn" style="flex: 1; background-color: #10b981">Buy</button>`}
        </div>
      `;
      document.querySelector(".profile-edit-btn").onclick = function () {
    window.location.href = `/home/edit/${id}`;
};
      // Remove fade class to trigger fade-in animation
      setTimeout(() => {
        profileBox.classList.remove('profile-box-fade');
      }, 50);
      
      // Add event listeners to the new buttons
      const borrowBtn = profileBox.querySelector('.profile-borrow-btn');
      const buyBtn = profileBox.querySelector('.profile-buy-btn');
      
      // Find the original buttons on the book card
      const originalBorrowBtn = bookCard.querySelector('.borrow-btn');
      const originalBuyBtn = bookCard.querySelector('.buy-btn');
      
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
    }, 300); // Match this timing with CSS transition duration
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

