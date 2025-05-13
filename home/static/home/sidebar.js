document.addEventListener('DOMContentLoaded', function () {
  const homeBtn = document.getElementById('home-btn');
  const borrowedBtn = document.getElementById('borrowed-btn');
  const logoutBtn = document.getElementById('logout-btn');
  const allBooksBtn=document.getElementById('allBooks-btn')
  const darkModeToggle = document.querySelector('.sidebar-buttons.darkMode');
  const cateogires = document.getElementById('categories-btn');
  const favouritesBtn = document.getElementById('favourites-btn');
  const settingsBtn = document.getElementById('settings-btn');
  const supportBtn = document.getElementById('support-btn');
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
  if(supportBtn){
      supportBtn.addEventListener('click',function(){
          window.location.href="/home/support/"
      })
  }
  if(settingsBtn){
      settingsBtn.addEventListener('click',function(){
          window.location.href="/home/settings/"
      })
  }

  if(allBooksBtn){
      allBooksBtn.addEventListener('click',function(){
          window.location.href="/home/categories/"
      })
  }
  if (borrowedBtn) {
      borrowedBtn.addEventListener('click', function () {
          window.location.href = "/home/borrowedBooksUser/";
      });
  }

  if (logoutBtn) {
      logoutBtn.addEventListener('click', function () {
          window.location.href = "/home/logout/";
      });
  }

  if (darkModeToggle) {
      darkModeToggle.addEventListener('click', () => {
          document.body.classList.toggle('dark-mode');
      });
  }
 });
