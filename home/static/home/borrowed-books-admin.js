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
    const id = book.id

    // Set up the inner HTML of the book card
    bookCard.innerHTML = `
          <div class="book-card-img">
            <img src="${book.image}" alt="${book.title}">
              <div class="action-buttons">
                ${
                    document.body.getAttribute('data-user-type') === 'Admin' ? `
                    
                      <button class="edit-btn">Edit</button>
                      
                      <button class="buy-btn">Delete</button>`
                        : `<button class="borrow-btn">Borrow</button>
                          <button class="buy-btn">Buy</button>`}
              </div>
          </div>
          <div class="book-card-content">
                <div style="justify-content: space-between !important; display: flex; align-items: center; margin-bottom: 10px;">
                  <span class="book-title">${book.title}</span>
                  <i class="${isFavorite(book.id,book) ? 'ph-fill ph-heart-straight' : 'ph ph-heart-straight'}"
                     style="${isFavorite(book.id,book) ? 'color: red;' : ''}"
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
                  <div class="book-id" style="display: none">${id}</div>
                </div>
                <div class="book-des" style="display: none;">${book.description || 'No description available.'}</div>

              </div>
      
    `;
      if (book.stock === 0) {
          bookCard.classList.add('out-of-stock');
      }

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
    const editBtn = bookCard.querySelector('.edit-btn');
    editBtn.addEventListener('click', function() {
      const isLoggedIn = document.body.getAttribute('data-logged-in') === 'true';
      if(isLoggedIn){
          window.location.href = `/home/edit/${book.id}`;
      }

    })

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

    buyBtn.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();

      // Check if user is logged in
      const isLoggedIn = document.body.getAttribute('data-logged-in') === 'true';
      if (isLoggedIn) {
        // Check if a form already exists for this book
        const existingForm = document.getElementById(`buy-form-discover-${book.id}`);
        if (existingForm) {
          existingForm.submit();
          return;
        }

        // Create a form and submit it to buy the book
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/home/buy/${book.id}/`;
        form.id = `dynamic-buy-form-${book.id}`;
        form.style.display = 'none';

        // Add CSRF token
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = getCsrfToken();
        form.appendChild(csrfInput);

        document.body.appendChild(form);
        form.submit();
      } else {
        // Redirect to login page
        window.location.href = '/home/login/';
      }
    });

    return bookCard;
  }
