document.addEventListener('DOMContentLoaded', function () {
  const homeBtn = document.getElementById('home-btn');
  const borrowedBtn = document.getElementById('borrowed-btn');
  const logoutBtn = document.getElementById('logout-btn');
  const allBooksBtn=document.getElementById('allBooks-btn')
  const cateogires = document.getElementById('categories-btn');
  const favouritesBtn = document.getElementById('favourites-btn');
  const settingsBtn = document.getElementById('settings-btn');
  const supportBtn = document.getElementById('support-btn');
  const loginBtn = document.getElementById('login-btn');
  const addBookBtn = document.getElementById('addBook-btn');
  const admindashboradBtn = document.getElementById('adminDashboard-btn');
  if(admindashboradBtn){
    admindashboradBtn.addEventListener('click',function(){
        window.location.href="/home/adminDashboard/"
    })
  }
  if(addBookBtn){
      addBookBtn.addEventListener('click',function(){
          window.location.href="/home/addBooks/"
      })
  }
  if(loginBtn){
      loginBtn.addEventListener('click',function(){
          window.location.href="/home/login/"
      })
  }
  if (homeBtn) {
      homeBtn.addEventListener('click', function () {
          window.location.href = "/home/homePage/";
      });
  }
  if(cateogires){
      cateogires.addEventListener('click',function(){
          window.location.href="/home/categories/"
      })
  }
  if(favouritesBtn){
      favouritesBtn.addEventListener('click',function(){
          window.location.href="/home/favorites/"
      })
  }
  // if(supportBtn){
  //     supportBtn.addEventListener('click',function(){
  //         window.location.href="/home/support/"
  //     })
  // }
  // if(settingsBtn){
  //     settingsBtn.addEventListener('click',function(){
  //         window.location.href="/home/settings/"
  //     })
  // }

  if(allBooksBtn){
      allBooksBtn.addEventListener('click',function(){
          window.location.href="/home/categories/"
      })
  }
  if (borrowedBtn) {
      borrowedBtn.addEventListener('click', function () {
          window.location.href = "/home/borrowedBooks/";
      });
  }

  if (logoutBtn) {
      logoutBtn.addEventListener('click', function () {
          window.location.href = "/home/logout/";
      });
  }
 });
