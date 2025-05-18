document.getElementById('image').addEventListener('change', function(e) {
      const preview = document.getElementById('imagePreview');
      preview.innerHTML = '';

      if (this.files && this.files[0]) {
        const reader = new FileReader();

        reader.onload = function(e) {
          const img = document.createElement('img');
          img.src = e.target.result;
          img.style.maxWidth = '200px';
          img.style.maxHeight = '300px';
          img.style.marginTop = '10px';
          img.style.borderRadius = '4px';
          preview.appendChild(img);
        }

        reader.readAsDataURL(this.files[0]);
      }
    });
 document.addEventListener('DOMContentLoaded', function() {
      const currentPath = window.location.pathname;
      const sidebarItems = document.querySelectorAll('.sidebar li');

      sidebarItems.forEach(item => {
        item.classList.remove('active');
      });

      document.getElementById('addBook-btn').classList.add('active');
    });
