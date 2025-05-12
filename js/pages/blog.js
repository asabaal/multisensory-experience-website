// Blog Page Specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
  initPostFilters();
});

// Filter blog posts by category
function initPostFilters() {
  const filterButtons = document.querySelectorAll('.post-filter__button');
  const blogPosts = document.querySelectorAll('.blog-card');
  
  // Exit if elements don't exist
  if (!filterButtons.length || !blogPosts.length) return;
  
  filterButtons.forEach(button => {
    button.addEventListener('click', () => {
      // Update active button
      filterButtons.forEach(btn => btn.classList.remove('post-filter__button--active'));
      button.classList.add('post-filter__button--active');
      
      // Get filter category
      const filter = button.dataset.filter;
      
      // Show/hide posts based on filter
      blogPosts.forEach(post => {
        if (filter === 'all' || post.dataset.category === filter) {
          post.style.display = '';
          
          // Add animation when showing posts
          post.classList.add('animate-fade-in');
          setTimeout(() => {
            post.classList.remove('animate-fade-in');
          }, 1000);
        } else {
          post.style.display = 'none';
        }
      });
    });
  });
  
  // Initialize search functionality
  initSearch();
}

// Search blog posts
function initSearch() {
  const searchForm = document.querySelector('.search-form');
  const searchInput = document.querySelector('.search-form__input');
  const blogPosts = document.querySelectorAll('.blog-card');
  const featuredPost = document.querySelector('.featured-post');
  
  if (!searchForm || !searchInput || !blogPosts.length) return;
  
  searchForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const searchTerm = searchInput.value.trim().toLowerCase();
    
    // Don't search if no term provided
    if (!searchTerm) return;
    
    // Reset active filter button
    const filterButtons = document.querySelectorAll('.post-filter__button');
    filterButtons.forEach(btn => btn.classList.remove('post-filter__button--active'));
    document.querySelector('[data-filter="all"]').classList.add('post-filter__button--active');
    
    // Search the blog posts
    let hasResults = false;
    
    // Search featured post if it exists
    if (featuredPost) {
      const featuredPostTitle = featuredPost.querySelector('.featured-post__title').textContent.toLowerCase();
      const featuredPostExcerpt = featuredPost.querySelector('.featured-post__excerpt').textContent.toLowerCase();
      
      if (featuredPostTitle.includes(searchTerm) || featuredPostExcerpt.includes(searchTerm)) {
        featuredPost.style.display = '';
        hasResults = true;
      } else {
        featuredPost.style.display = 'none';
      }
    }
    
    // Search regular posts
    blogPosts.forEach(post => {
      const postTitle = post.querySelector('.blog-card__title').textContent.toLowerCase();
      const postExcerpt = post.querySelector('.blog-card__excerpt').textContent.toLowerCase();
      const postCategory = post.querySelector('.blog-card__category').textContent.toLowerCase();
      
      if (postTitle.includes(searchTerm) || postExcerpt.includes(searchTerm) || postCategory.includes(searchTerm)) {
        post.style.display = '';
        hasResults = true;
        
        // Add animation when showing posts
        post.classList.add('animate-fade-in');
        setTimeout(() => {
          post.classList.remove('animate-fade-in');
        }, 1000);
      } else {
        post.style.display = 'none';
      }
    });
    
    // Show message if no results
    const noResultsMessage = document.querySelector('.no-results-message');
    
    if (!hasResults) {
      if (!noResultsMessage) {
        const message = document.createElement('div');
        message.className = 'no-results-message';
        message.textContent = `No results found for "${searchTerm}". Please try a different search term.`;
        
        const blogGrid = document.querySelector('.blog-grid');
        blogGrid.parentNode.insertBefore(message, blogGrid);
      }
    } else if (noResultsMessage) {
      noResultsMessage.remove();
    }
  });
}

// Pagination functionality
document.querySelectorAll('.pagination__button').forEach(button => {
  button.addEventListener('click', () => {
    // In a real implementation, this would load new posts
    // For this demo, we'll just update the active button
    document.querySelectorAll('.pagination__button').forEach(btn => {
      btn.classList.remove('pagination__button--active');
    });
    
    if (!button.classList.contains('pagination__button--next')) {
      button.classList.add('pagination__button--active');
    }
    
    // Scroll to top of posts
    document.querySelector('.blog-section').scrollIntoView({ behavior: 'smooth' });
  });
});