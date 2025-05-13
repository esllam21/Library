  const toggleBtn = document.getElementById('toggle-sidebar');
  const sidebar = document.querySelector('.sidebar');
// Search functionality
document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.querySelector('.search-input input');
  
  if (searchInput) {
    // Add event listener for the Enter key
    searchInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        
        // Get the search query
        const query = this.value.trim();
        
        if (query) {
          // Navigate to the search results page
          window.location.href = `/home/search/?q=${encodeURIComponent(query)}`;
        }
      }
    });
    
    // Add debounced input event for live search suggestions (optional)
    let debounceTimer;
    searchInput.addEventListener('input', function() {
      clearTimeout(debounceTimer);
      
      // Only proceed if there's actual input
      if (this.value.trim().length < 2) {
        // Remove any existing search suggestions
        const existingSuggestions = document.querySelector('.search-suggestions');
        if (existingSuggestions) {
          existingSuggestions.remove();
        }
        return;
      }
      
      // Set a debounce timer to avoid too many requests
      debounceTimer = setTimeout(function() {
        // This is where you would normally make an AJAX call to get search suggestions
        // For now, we'll just show a simple UI
        showSearchSuggestions(searchInput.value.trim());
      }, 300); // Wait 300ms after user stops typing
    });
    
    // Handle clicks outside the search area to close suggestions
    document.addEventListener('click', function(e) {
      if (!e.target.closest('.search-input')) {
        const suggestions = document.querySelector('.search-suggestions');
        if (suggestions) {
          suggestions.remove();
        }
      }
    });
  }
  
  // Function to show search suggestions
  function showSearchSuggestions(query) {
    // Remove any existing suggestions
    const existingSuggestions = document.querySelector('.search-suggestions');
    if (existingSuggestions) {
      existingSuggestions.remove();
    }
    
    // Create suggestions container
    const suggestionsContainer = document.createElement('div');
    suggestionsContainer.className = 'search-suggestions';
    
    // Add a message to press Enter to search
    const searchPrompt = document.createElement('div');
    searchPrompt.className = 'search-prompt';
    searchPrompt.innerHTML = `<span>Press Enter to search for "${query}"</span>`;
    suggestionsContainer.appendChild(searchPrompt);
    
    // Add the suggestions container to the DOM
    const searchInput = document.querySelector('.search-input');
    searchInput.appendChild(suggestionsContainer);
    
    // Position the suggestions container
    const inputRect = searchInput.getBoundingClientRect();
    suggestionsContainer.style.width = `${inputRect.width}px`;
    suggestionsContainer.style.top = `${inputRect.height}px`;
  }
});
  toggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
  });
