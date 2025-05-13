// document.getElementById('uploadImageFileButton').addEventListener('click', () => {
//   document.getElementById('imageFileInput').click();
// });
//
// document.getElementById('imageFileInput').addEventListener('change', (event) => {
//   const file = event.target.files[0];
//   const previewContainer = document.getElementById('imagePreviewContainer');
//
//   if (file && file.type.startsWith('image/')) {
//     const reader = new FileReader();
//     reader.onload = function (e) {
//       previewContainer.innerHTML = `<img src="${e.target.result}" alt="Book Cover" style="max-width: 200px; max-height: 300px;">`;
//     };
//     reader.readAsDataURL(file);
//   } else {
//     previewContainer.innerHTML = `<p>Please select a valid image file.</p>`;
//   }
// });
//
// document.getElementById("addbutton").addEventListener("click", function () {
//   const title = document.getElementById("bookTitle").value.trim();
//   const author = document.getElementById("bookAuthor").value.trim();
//   const description = document.getElementById("bookDescription").value.trim();
//   const language = document.getElementById("bookLanguage").value.trim();
//   const pages = parseInt(document.getElementById("bookPageCount").value.trim()) || 300;
//
//   const categorySelect = document.getElementById("bookCategory").value;
//   const customCategory = document.getElementById("customCategory").value.trim();
//   const category = customCategory || categorySelect;
//
//   const priceInput = document.getElementById("bookPrice").value.trim();
//   const price = parseFloat(priceInput) || 0;
//
//   const imageFile = document.getElementById("imageFileInput").files[0];
//   if (!title || !imageFile) {
//     alert("Please enter the book title and upload an image.");
//     return;
//   }
//
//   const reader = new FileReader();
//   reader.onload = function (e) {
//     const imageData = e.target.result;
//
//     const newBook = {
//       title: title,
//       author: author,
//       description: description,
//       language: language,
//       pages: pages,
//       category: category,
//       price: price,
//       imagePath: imageData,
//       isBorrowed: false,
//       isReturned: false,
//       isCompleted: false
//     };
//
//     let customBooks = JSON.parse(localStorage.getItem("customBooks")) || [];
//     customBooks.push(newBook);
//     localStorage.setItem("customBooks", JSON.stringify(customBooks));
//
//     alert("Book added successfully!");
//   };
//
//   reader.readAsDataURL(imageFile);
// });
// // localStorage.removeItem("customBooks");
// // localStorage.removeItem("borrowedBooks");


document.addEventListener('DOMContentLoaded', function () {
  const homeBtn = document.getElementById('home-btn');
  const borrowedBtn = document.getElementById('borrowed-btn');
  const logoutBtn = document.getElementById('logout-btn');
  const allBooksBtn=document.getElementById('allBooks-btn')
  const darkModeToggle = document.querySelector('.sidebar-buttons.darkMode');

  if (homeBtn) {
      homeBtn.addEventListener('click', function () {
          window.location.href = "/home/homePage";
      });
  }

  if (borrowedBtn) {
      borrowedBtn.addEventListener('click', function () {
          window.location.href = "/home/borrowedBooksAdmin/";
      });
  }
  if(allBooksBtn){
    allBooksBtn.addEventListener('click',function(){
      window.location.href="/home/availableBooks/"
    })
  }

  if (logoutBtn) {
      logoutBtn.addEventListener('click', function () {
          localStorage.setItem("isLoggedIn", "false");
          window.location.href = "/home/homePage/";
      });
  }

  if (darkModeToggle) {
      darkModeToggle.addEventListener('click', () => {
          document.body.classList.toggle('dark-mode');
      });
  }
});
