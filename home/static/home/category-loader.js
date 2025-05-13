// Category Book Loader
document.addEventListener("DOMContentLoaded", function() {
  // Get elements
  const categoryTags = document.querySelectorAll('.tag');
  const profileBox = document.querySelector('.profile-box');
  let activeBookCard = null; // Track active book card
  const booksContainer = document.getElementById('category-books-container');
  if (!booksContainer) {
    console.error('Category books container not found!');
    return;
  }
  function loadCategoryBooks(categoryId) {
    // Show loading spinner
    booksContainer.innerHTML = `
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p>Loading books...</p>
      </div>
    `;
    
    // Define the API endpoint
    const currentPath = window.location.pathname;
    let url;
    if (currentPath.includes('home/categories/')) {
      url = `/home/api/all_filter-books-by-category/?category_id=${categoryId}`;
    } else if (currentPath.includes('home/homePage/')) {
      url = `/home/api/filter-books-by-category/?category_id=${categoryId}`;
    }
    
    // Fetch books from the API
    fetch(url)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Network error: ${response.status} ${response.statusText}`);
        }
        return response.json();
      })
      .then(data => {
        // Clear loading spinner
        booksContainer.innerHTML = '';
        
        // Check if we have books
        if (data.success && data.books && data.books.length > 0) {
          // Create and append book cards
          data.books.forEach(book => {
            const bookCard = createBookCard(book);
            booksContainer.appendChild(bookCard);
          });
          
          console.log(`Loaded ${data.books.length} books for category ${categoryId}`);
        } else {
          // No books found
          booksContainer.innerHTML = `
            <div class="no-books-message">
              No books found in this category.
            </div>
          `;
          console.log(`No books found for category ${categoryId}`);
        }
      })
      .catch(error => {
        // Show error message
        console.error('Error loading books:', error);
        booksContainer.innerHTML = `
          <div class="no-books-message">
            Error loading books. Please try again later.
            <br><small>${error.message}</small>
          </div>
        `;
      });
  }
  
  // Add click handler to category tags
  categoryTags.forEach(tag => {
    tag.addEventListener('click', function() {
      // Update active state
      categoryTags.forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      
      // Get category ID
      const categoryId = this.getAttribute('data-category-id');
      
      // Load books for this category with fade effect
      booksContainer.classList.add('category-fade-out');
      setTimeout(() => {
        loadCategoryBooks(categoryId);
        setTimeout(() => {
          booksContainer.classList.remove('category-fade-out');
        }, 300);
      }, 300);
    });
  });
  
  // Load initial books (All category)
  loadCategoryBooks('all');



  //NEW
  //------------------------------------------------------------------------
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

    // Get rating if available, otherwise use placeholder
    let bookRating = "N/A";
    const ratingElement = bookCard.querySelector('.book-rating span');
    if (ratingElement) {
      bookRating = ratingElement.textContent;
    }

    // Get prices
    const borrowPrice = bookCard.querySelector('.book-price')?.textContent || "$0.00";
    const buyPrice = bookCard.querySelector('.buy-price')?.textContent || "$0.00";
document.addEventListener('DOMContentLoaded', function() {
    const tagsContainer = document.querySelector('.tags-container');
    const categoryBooksContainer = document.getElementById('category-books-container');
    
    if (tagsContainer && categoryBooksContainer) {
        const tags = tagsContainer.querySelectorAll('.tag');
        
        // Get favorite book IDs from the data attribute
        const favoriteBookIds = [];
        if (document.body.hasAttribute('data-favorite-book-ids')) {
            try {
                const favoriteIdsStr = document.body.getAttribute('data-favorite-book-ids');
                if (favoriteIdsStr) {
                    favoriteIdsStr.split(',').forEach(id => {
                        if (id && !isNaN(parseInt(id))) {
                            favoriteBookIds.push(parseInt(id));
                        }
                    });
                }
            } catch (e) {
                console.error('Error parsing favorite book IDs:', e);
            }
        }
        
        // Set active tag and load books
        tags.forEach(tag => {
            tag.addEventListener('click', function() {
                // Remove active class from all tags
                tags.forEach(t => t.classList.remove('active'));
                
                // Add active class to clicked tag
                this.classList.add('active');
                
                // Get category ID from data attribute
                const categoryId = this.getAttribute('data-category-id');
                
                // Show loading spinner
                categoryBooksContainer.innerHTML = `
                    <div class="loading-spinner">
                        <div class="spinner"></div>
                        <p>Loading books...</p>
                    </div>
                `;
                
                // Fetch books for selected category
                fetchBooksByCategory(categoryId);
            });
        });
        
        // Load initial books (all categories)
        fetchBooksByCategory('all');
        
        // Function to fetch books by category
        function fetchBooksByCategory(categoryId) {
            fetch(`/home/api/books-by-category/${categoryId}/`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        displayBooks(data.books);
                    } else {
                        categoryBooksContainer.innerHTML = `
                            <div class="error-message">
                                <p>Error loading books: ${data.error || 'Unknown error'}</p>
                            </div>
                        `;
                    }
                })
                .catch(error => {
                    console.error('Error fetching books:', error);
                    categoryBooksContainer.innerHTML = `
                        <div class="error-message">
                            <p>Error loading books. Please try again later.</p>
                        </div>
                    `;
                });
        }
        
        // Function to display books
        function displayBooks(books) {
            if (!books || books.length === 0) {
                categoryBooksContainer.innerHTML = `
                    <div class="no-books-message">
                        <p>No books found in this category.</p>
                    </div>
                `;
                return;
            }
            
            let html = '';
            
            books.forEach(book => {
                const isFavorite = favoriteBookIds.includes(book.id);
                const heartClass = isFavorite ? 'ph-heart-fill favorite-active' : 'ph-heart-straight';
                
                html += `
                    <div class="book-card" 
                         data-category="${book.category || 'Uncategorized'}"
                         data-pages="${book.pageCount || 0}"
                         data-rating-count="${book.ratingCount || 0}">
                        <div class="book-card-img">
                            <img src="${book.image}" alt="${book.title}">
                            <div class="action-buttons">
                                <a href="/home/borrow/${book.id}/" onclick="event.preventDefault(); document.getElementById('borrow-form-cat-${book.id}').submit();">
                                    <button class="borrow-btn">Borrow</button>
                                </a>
                                <a href="/home/buy/${book.id}/" onclick="event.preventDefault(); document.getElementById('buy-form-cat-${book.id}').submit();">
                                    <button class="buy-btn">Buy</button>
                                </a>
                            </div>
                            <form id="borrow-form-cat-${book.id}" action="/home/borrow/${book.id}/" method="post" style="display: none;">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${getCsrfToken()}">
                            </form>
                            <form id="buy-form-cat-${book.id}" action="/home/buy/${book.id}/" method="post" style="display: none;">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${getCsrfToken()}">
                            </form>
                        </div>
                        <div class="book-card-content">
                            <div style="justify-content: space-between !important; display: flex; align-items: center; margin-bottom: 10px;">
                                <span class="book-title">${book.title}</span>
                                <i class="ph ${heartClass}"
                                   onclick="event.preventDefault(); document.getElementById('favorite-form-cat-${book.id}').submit();"></i>
                            </div>
                            <form id="favorite-form-cat-${book.id}" action="/home/add-favorite/${book.id}/" method="post" style="display: none;">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${getCsrfToken()}">
                            </form>
                            <div class="book-info">
                                <span class="book-author">${book.author}</span>
                                <div class="book-rating">
                                    <i class="ph ph-star-fill"></i>
                                    <span>${book.rating || 'N/A'}</span>
                                </div>
                            </div>
                            <div class="book-prices">
                                <div class="book-price">$${book.borrowPrice.toFixed(2)}</div>
                                <div class="buy-price">$${book.buyPrice.toFixed(2)}</div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            categoryBooksContainer.innerHTML = html;
            
            // Apply fade-in animation
            setTimeout(() => {
                categoryBooksContainer.classList.add('category-fade-in');
            }, 100);
        }
        
        // Function to get CSRF token
        function getCsrfToken() {
            const cookieValue = document.cookie
                .split('; ')
                .find(row => row.startsWith('csrftoken='))
                ?.split('=')[1];
            
            if (cookieValue) {
                return cookieValue;
            }
            
            // Fallback - try to get from meta tag
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
            if (csrfToken) {
                return csrfToken;
            }
            
            // If no token found, log error and return empty string
            console.error('CSRF token not found!');
            return '';
        }
    }
});
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
        
        <div class="meta-row">
          <span class="meta">${pages} Pages</span>
          <span class="meta-separator"></span>
          <span class="meta">${reviewCount} Ratings</span>
        </div>
        
        <div class="meta">Borrow: ${borrowPrice}</div>
        <div class="meta">Purchase: ${buyPrice}</div>
        
        <p>Click on the buttons below to borrow or buy this book!</p>
        <div style="display: flex; gap: 10px; width: 100%; margin-top: 10px;">
          <button class="profile-borrow-btn" style="flex: 1; background-color: #4361ee;">Borrow</button>
          <button class="profile-buy-btn" style="flex: 1; background-color: #10b981;">Buy</button>
        </div>
      `;

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
  // Function to get CSRF token
  function getCsrfToken() {
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];
    
    if (cookieValue) {
      return cookieValue;
    }
    
    // Fallback - try to get from meta tag
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    if (csrfToken) {
      return csrfToken;
    }
    
    // If no token found, try to get from any existing form
    const existingToken = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (existingToken) {
      return existingToken.value;
    }
    
    console.error('CSRF token not found!');
    return '';
  }
  
  function createBookCard(book) {
    // Create a new book card element
    const bookCard = document.createElement('div');
    bookCard.className = 'book-card';
    bookCard.setAttribute('data-category', book.category);
    bookCard.setAttribute('data-pages', book.pageCount);
    bookCard.setAttribute('data-rating-count', book.ratingCount);

    // Generate star rating display
    let stars = '';
    if (book.rating) {
      const ratingNum = book.rating;
      for (let i = 1; i <= 5; i++) {
        if (i <= Math.floor(ratingNum)) {
          stars += '★'; // Full star
        } else if (i === Math.ceil(ratingNum) && ratingNum % 1 !== 0) {
          stars += '★'; // Half star (approximating with full star for simplicity)
        } else {
          stars += '☆'; // Empty star
        }
      }
      stars += ` ${ratingNum.toFixed(1)}`;
    } else {
      stars = '★☆☆☆☆ Not rated';
    }

    // Format prices with $ if they don't already have it
    const borrowPrice = book.borrowPrice.toString().includes('$') ?
      book.borrowPrice :
      `$${book.borrowPrice.toFixed(2)}`;

    const buyPrice = book.buyPrice.toString().includes('$') ?
      book.buyPrice :
      `$${book.buyPrice.toFixed(2)}`;

    // Set up the inner HTML of the book card
    bookCard.innerHTML = `
      <div class="book-card-img">
        <img src="${book.image}" alt="${book.title}">
        <div class="action-buttons">
          <button class="borrow-btn">Borrow</button>
          <button class="buy-btn">Buy</button>
        </div>
      </div>
      <div class="book-card-content">
        <div style="justify-content: space-between !important; display: flex; align-items: center; margin-bottom: 10px;">
          <span class="book-title">${book.title}</span>
          <i class="ph ph-heart-straight"
             onclick="event.preventDefault(); document.getElementById('favorite-form-discover-${book.id}').submit();"></i>
        </div>
        <form id="favorite-form-discover-${book.id}" action="/home/add-favorite/${book.id}/" 
              method="post" style="display: none;">
          <input type="hidden" name="csrfmiddlewaretoken" value="${getCsrfToken()}">
        </form>
        <div class="book-info">
          <span class="book-author">${book.author}</span>
          <div class="book-rating">
            <i class="ph ph-star-fill"></i>
            <span>${book.rating.toFixed(1)}</span>
          </div>
        </div>
        <div class="book-prices">
          <div class="book-price">${borrowPrice}</div>
          <div class="buy-price">${buyPrice}</div>
        </div>
      </div>
    `;

    // Add click event listener to book card
    bookCard.addEventListener('click', function(e) {
      // Only trigger if click wasn't on a button
      if (!e.target.classList.contains('borrow-btn') &&
          !e.target.classList.contains('buy-btn')) {
        updateProfileBox(this);
      }
    });

    // Add click event listeners to buttons
    const borrowBtn = bookCard.querySelector('.borrow-btn');
    const buyBtn = bookCard.querySelector('.buy-btn');

    borrowBtn.addEventListener('click', function() {
      // Check if user is logged in
      const isLoggedIn = document.body.getAttribute('data-logged-in') === 'true';
      if (isLoggedIn) {
        // Create a form and submit it to borrow the book
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/home/borrow/${book.id}/`;

        // Add CSRF token
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfToken) {
          const csrfInput = document.createElement('input');
          csrfInput.type = 'hidden';
          csrfInput.name = 'csrfmiddlewaretoken';
          csrfInput.value = csrfToken.value;
          form.appendChild(csrfInput);
        }

        document.body.appendChild(form);
        form.submit();
      } else {
        // Redirect to login page
        window.location.href = '/home/login/';
      }
    });

    buyBtn.addEventListener('click', function() {
      // Check if user is logged in
      const isLoggedIn = document.body.getAttribute('data-logged-in') === 'true';
      if (isLoggedIn) {
        // Create a form and submit it to buy the book
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/home/buy/${book.id}/`;

        // Add CSRF token
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfToken) {
          const csrfInput = document.createElement('input');
          csrfInput.type = 'hidden';
          csrfInput.name = 'csrfmiddlewaretoken';
          csrfInput.value = csrfToken.value;
          form.appendChild(csrfInput);
        }

        document.body.appendChild(form);
        form.submit();
      } else {
        // Redirect to login page
        window.location.href = '/home/login/';
      }
    });

    return bookCard;
  }



});
