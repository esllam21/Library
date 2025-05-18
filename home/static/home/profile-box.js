document.addEventListener("DOMContentLoaded", function () {
  const bookCards = document.querySelectorAll('.book-card');
  const profileBox = document.querySelector('.profile-box');
  let activeBookCard = null;
  function updateProfileBox(bookCard) {
    if (activeBookCard === bookCard) return;
    if (activeBookCard) {
      activeBookCard.classList.remove('book-card-active');
    }
    activeBookCard = bookCard;
    bookCard.classList.add('book-card-active');
    const bookImage = bookCard.querySelector('img').src;
    const bookTitle = bookCard.querySelector('.book-title').textContent;
    const bookAuthor = bookCard.querySelector('.book-author').textContent;
    const bookDes=bookCard.querySelector('.book-des').textContent;
    const borrowPrice = bookCard.querySelector('.book-price')?.textContent || "$0.00";
    const buyPrice = bookCard.querySelector('.buy-price')?.textContent || "$0.00";
    const id = bookCard.querySelector('.book-id')?.textContent || "0";
    const stock = bookCard.querySelector('.stock')?.textContent || "0";
    const count = bookCard.querySelector('.count')?.textContent || "0";
    const pages=bookCard.getAttribute('data-pages');
    const reviewCount=bookCard.getAttribute('data-rating-count');
    const bookRating = bookCard.querySelector('.book-rating span')?.textContent || "N/A";
    const currentPath=window.location.pathname;
    let bookCategory
    let stars = "";
    if (bookRating !== "N/A") {
      const ratingNum = parseFloat(bookRating);
      for (let i = 1; i <= 5; i++) {
        if (i <= Math.floor(ratingNum)) {
          stars += "★";
        } else if (i === Math.ceil(ratingNum) && ratingNum % 1 !== 0) {
          stars += "★";
        } else {
          stars += "☆";
        }
      }
      stars += ` ${bookRating}`;
    } else {
      stars = "★☆☆☆☆ Not rated";
    }
    profileBox.classList.add('profile-box-fade');
    if(currentPath.includes('categories')){
      bookCategory = bookCard.querySelector('.book-category').textContent;
    }
    else{
      bookCategory = bookCard.getAttribute('data-category');
    }
    setTimeout(() => {
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
        <div class="meta-row">
          <div class="meta">${borrowPrice}</div>
          <span class="meta-separator"></span>
          <div class="meta">${buyPrice}</div>
        </div>
        ${ document.body.getAttribute('data-user-type') === 'Admin' ? `<div class="meta-row">
            <div class="meta">Stock: ${stock}</div>
            <span class="meta-separator"></span>
            <div class="meta">Count: ${count}</div>
          </div>` : ``}
        <div style="display: flex; gap: 10px; width: 100%; margin-top: 10px;">
          ${currentPath.includes('borrowedBooks') ? 
            `
            <button class="profile-return-btn" style="flex: 1; background-color: #ff5151">Return</button>
            <button class="profile-buy-btn" style="flex: 1; background-color: #10b981">Buy</button>
            `
            : 
            `
            <button class="profile-borrow-btn" style="flex: 1; background-color: #4361ee">Borrow</button>
            <button class="profile-buy-btn" style="flex: 1; background-color: #10b981">Buy</button>
            `
          }       
         </div>
        ${document.body.getAttribute('data-user-type') === 'Admin' ? `
          <div style="display: flex; gap: 10px; width: 100%; margin-top: 10px;">
            <button class="profile-edit-btn" style="flex: 1; background-color:#4361ee ">Edit</button>
            <button class="profile-delete-btn" style="flex: 1; background-color: #ff5151">Delete</button>
          </div>` : ``}
      `;

      setTimeout(() => {
        profileBox.classList.remove('profile-box-fade');
      }, 50);
      const borrowBtn = profileBox.querySelector('.profile-borrow-btn');
      const buyBtn = profileBox.querySelector('.profile-buy-btn');
      const editBtn = profileBox.querySelector('.profile-edit-btn');
      const deleteBtn = profileBox.querySelector('.profile-delete-btn');
      const returnBtn = profileBox.querySelector('.profile-return-btn');
      const originalBorrowBtn = bookCard.querySelector('.borrow-btn');
      const originalBuyBtn = bookCard.querySelector('.buy-btn');
      const originalEditBtn = bookCard.querySelector('.edit-btn');
      const originalDeleteBtn = bookCard.querySelector('.delete-btn');
      const originalReturnBtn = bookCard.querySelector('.return-btn');

      if(returnBtn && originalReturnBtn){
        returnBtn.addEventListener('click', () => {
          originalReturnBtn.click();
        });
      }
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
  const initializeFirstBook = () => {
    if (bookCards.length > 0) {
      updateProfileBox(bookCards[0]);
    }
  };
  bookCards.forEach(bookCard => {
    bookCard.addEventListener('click', function(e) {
      if (!e.target.classList.contains('borrow-btn') &&
          !e.target.classList.contains('buy-btn')&&
          !e.target.classList.contains('edit-btn')) {
        updateProfileBox(this);
      }
    });
  });
  setTimeout(initializeFirstBook, 500);
});
