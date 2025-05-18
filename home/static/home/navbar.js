  const toggleBtn = document.getElementById('toggle-sidebar');
  const sidebar = document.querySelector('.sidebar');
document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.querySelector('.search-input input');
  
  if (searchInput) {
    searchInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        const query = this.value.trim();
        if (query) {
          window.location.href = `/home/search/?q=${encodeURIComponent(query)}`;
        }
      }
    });
    let debounceTimer;
    searchInput.addEventListener('input', function() {
      clearTimeout(debounceTimer);
      if (this.value.trim().length < 2) {
        const existingSuggestions = document.querySelector('.search-suggestions');
        if (existingSuggestions) {
          existingSuggestions.remove();
        }
        return;
      }
      debounceTimer = setTimeout(function() {
        showSearchSuggestions(searchInput.value.trim());
      }, 300);
    });
    document.addEventListener('click', function(e) {
      if (!e.target.closest('.search-input')) {
        const suggestions = document.querySelector('.search-suggestions');
        if (suggestions) {
          suggestions.remove();
        }
      }
    });
  }
  function showSearchSuggestions(query) {
    const existingSuggestions = document.querySelector('.search-suggestions');
    if (existingSuggestions) {
      existingSuggestions.remove();
    }
    const suggestionsContainer = document.createElement('div');
    suggestionsContainer.className = 'search-suggestions';
    const searchPrompt = document.createElement('div');
    searchPrompt.className = 'search-prompt';
    searchPrompt.innerHTML = `<span>Press Enter to search for "${query}"</span>`;
    suggestionsContainer.appendChild(searchPrompt);
    const searchInput = document.querySelector('.search-input');
    searchInput.appendChild(suggestionsContainer);
    const inputRect = searchInput.getBoundingClientRect();
    suggestionsContainer.style.width = `${inputRect.width}px`;
    suggestionsContainer.style.top = `${inputRect.height}px`;
  }
});
  toggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
  });
