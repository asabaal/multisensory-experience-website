// Main JavaScript file

document.addEventListener('DOMContentLoaded', () => {
  // Initialize components
  initNavigation();
  initScrollEffects();
  initCarousel();
  initForms();
  
  // Page-specific initializations
  const currentPage = document.body.dataset.page;
  
  if (currentPage === 'home') {
    initHeroAnimation();
  } else if (currentPage === 'imagination') {
    initImaginationInteractive();
  } else if (currentPage === 'events') {
    initEventFilters();
  }
});

// Navigation functionality
function initNavigation() {
  const navToggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.nav');
  
  if (navToggle && nav) {
    navToggle.addEventListener('click', () => {
      navToggle.classList.toggle('nav-toggle--active');
      nav.classList.toggle('nav--open');
      document.body.classList.toggle('nav-open'); // Prevents scrolling when nav is open
    });
  }
  
  // Close mobile navigation when clicking outside
  document.addEventListener('click', (e) => {
    if (nav && navToggle && nav.classList.contains('nav--open')) {
      if (!nav.contains(e.target) && !navToggle.contains(e.target)) {
        navToggle.classList.remove('nav-toggle--active');
        nav.classList.remove('nav--open');
        document.body.classList.remove('nav-open');
      }
    }
  });
  
  // Set active nav item based on current page
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll('.nav__link');
  
  navLinks.forEach(link => {
    const linkPath = link.getAttribute('href');
    if (currentPath === linkPath || (linkPath !== '/' && currentPath.includes(linkPath))) {
      link.classList.add('nav__link--active');
    }
  });
}

// Scroll effects (header behavior, animations)
function initScrollEffects() {
  // Variables
  const header = document.querySelector('.header');
  let lastScrollY = window.scrollY;
  let ticking = false;
  
  // Handle scroll events with throttling for performance
  function onScroll() {
    if (!ticking) {
      window.requestAnimationFrame(() => {
        handleHeaderVisibility();
        animateOnScroll();
        ticking = false;
      });
      ticking = true;
    }
  }
  
  // Show/hide header based on scroll direction
  function handleHeaderVisibility() {
    if (!header) return;
    
    const currentScrollY = window.scrollY;
    
    // Header becomes sticky and gets shadow
    if (currentScrollY > 100) {
      header.classList.add('header--scrolled');
    } else {
      header.classList.remove('header--scrolled');
    }
    
    // Auto-hide header when scrolling down (below hero section)
    if (currentScrollY > 400) {
      if (currentScrollY > lastScrollY) {
        header.classList.add('header--hidden');
      } else {
        header.classList.remove('header--hidden');
      }
    }
    
    lastScrollY = currentScrollY;
  }
  
  // Animate elements when they come into view
  function animateOnScroll() {
    const elements = document.querySelectorAll('.animate-on-scroll:not(.animated)');
    
    elements.forEach(element => {
      if (isElementInViewport(element)) {
        element.classList.add('animated');
        
        // If element has a specific animation type, add that class
        const animationType = element.dataset.animation;
        if (animationType) {
          element.classList.add(`animate-${animationType}`);
        }
      }
    });
  }
  
  // Check if element is in viewport
  function isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
      rect.top <= (window.innerHeight || document.documentElement.clientHeight) * 0.85 &&
      rect.bottom >= 0
    );
  }
  
  // Add window event listeners
  window.addEventListener('scroll', onScroll);
  window.addEventListener('resize', onScroll);
  
  // Initial call to set correct states
  onScroll();
}

// Featured content carousel
function initCarousel() {
  const carousels = document.querySelectorAll('.carousel');
  
  carousels.forEach(carousel => {
    const container = carousel.querySelector('.carousel__container');
    const items = carousel.querySelectorAll('.carousel__item');
    const prevBtn = carousel.querySelector('.carousel__prev');
    const nextBtn = carousel.querySelector('.carousel__next');
    const dots = carousel.querySelectorAll('.carousel__dot');
    
    if (!container || !items.length) return;
    
    let currentIndex = 0;
    const itemCount = items.length;
    
    // Set initial state
    updateCarousel();
    
    // Next slide button
    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        currentIndex = (currentIndex + 1) % itemCount;
        updateCarousel();
      });
    }
    
    // Previous slide button
    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        currentIndex = (currentIndex - 1 + itemCount) % itemCount;
        updateCarousel();
      });
    }
    
    // Dot navigation
    if (dots.length) {
      dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
          currentIndex = index;
          updateCarousel();
        });
      });
    }
    
    // Auto-advance slides if data-auto-slide is present
    if (carousel.dataset.autoSlide) {
      const interval = parseInt(carousel.dataset.autoSlide) || 5000;
      
      setInterval(() => {
        currentIndex = (currentIndex + 1) % itemCount;
        updateCarousel();
      }, interval);
    }
    
    // Touch/swipe support
    let touchStartX = 0;
    let touchEndX = 0;
    
    carousel.addEventListener('touchstart', e => {
      touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });
    
    carousel.addEventListener('touchend', e => {
      touchEndX = e.changedTouches[0].screenX;
      handleSwipe();
    }, { passive: true });
    
    function handleSwipe() {
      const swipeThreshold = 50;
      if (touchEndX < touchStartX - swipeThreshold) {
        // Swipe left (next)
        currentIndex = (currentIndex + 1) % itemCount;
        updateCarousel();
      } else if (touchEndX > touchStartX + swipeThreshold) {
        // Swipe right (prev)
        currentIndex = (currentIndex - 1 + itemCount) % itemCount;
        updateCarousel();
      }
    }
    
    // Update carousel display
    function updateCarousel() {
      // Update slides position
      const slideWidth = items[0].offsetWidth;
      container.style.transform = `translateX(-${currentIndex * slideWidth}px)`;
      
      // Update active dot
      if (dots.length) {
        dots.forEach((dot, index) => {
          if (index === currentIndex) {
            dot.classList.add('carousel__dot--active');
          } else {
            dot.classList.remove('carousel__dot--active');
          }
        });
      }
    }
    
    // Update on window resize
    window.addEventListener('resize', updateCarousel);
  });
}

// Form handling (validation, submission)
function initForms() {
  const forms = document.querySelectorAll('form');
  
  forms.forEach(form => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      
      // Skip validation if the form has the no-validate class
      if (form.classList.contains('no-validate')) {
        displayFormSuccess(form);
        return;
      }
      
      // Otherwise, validate the form
      if (validateForm(form)) {
        displayFormSuccess(form);
      }
    });
  });
  
  // Form validation
  function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input:not([type="submit"]), textarea, select');
    
    // Remove any existing error messages
    const existingErrors = form.querySelectorAll('.form__message--error');
    existingErrors.forEach(error => error.remove());
    
    // Validate each input
    inputs.forEach(input => {
      input.classList.remove('input--error');
      
      // Required fields
      if (input.hasAttribute('required') && !input.value.trim()) {
        displayErrorForInput(input, 'This field is required');
        isValid = false;
      }
      
      // Email validation
      if (input.type === 'email' && input.value.trim()) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(input.value.trim())) {
          displayErrorForInput(input, 'Please enter a valid email address');
          isValid = false;
        }
      }
      
      // Password validation (if needed)
      if (input.type === 'password' && input.hasAttribute('data-min-length')) {
        const minLength = parseInt(input.getAttribute('data-min-length'));
        if (input.value.length < minLength) {
          displayErrorForInput(input, `Password must be at least ${minLength} characters`);
          isValid = false;
        }
      }
      
      // Custom validation based on data attributes can go here
    });
    
    return isValid;
  }
  
  // Display error message for an input
  function displayErrorForInput(input, message) {
    input.classList.add('input--error');
    
    const errorElement = document.createElement('div');
    errorElement.className = 'form__message form__message--error';
    errorElement.textContent = message;
    
    // Insert error after the input
    input.parentNode.insertBefore(errorElement, input.nextSibling);
  }
  
  // Display success message and optionally reset form
  function displayFormSuccess(form) {
    // If there's a success message container, show it
    const successContainer = form.querySelector('.form__success');
    
    if (successContainer) {
      successContainer.classList.add('form__success--visible');
      
      // Hide it after a delay if it's not persistent
      if (!successContainer.hasAttribute('data-persistent')) {
        setTimeout(() => {
          successContainer.classList.remove('form__success--visible');
        }, 5000); // 5 seconds
      }
    } else {
      // Otherwise, create a success message
      const formMessage = document.createElement('div');
      formMessage.className = 'form__message form__message--success';
      formMessage.textContent = 'Form submitted successfully!';
      
      form.appendChild(formMessage);
      
      // Remove after a delay
      setTimeout(() => {
        formMessage.remove();
      }, 5000); // 5 seconds
    }
    
    // Reset the form (unless it has the no-reset class)
    if (!form.classList.contains('no-reset')) {
      form.reset();
    }
  }
}

// Hero section animation (for home page)
function initHeroAnimation() {
  const hero = document.querySelector('.hero');
  if (!hero) return;
  
  // Add animation classes with slight delays for a cascade effect
  setTimeout(() => {
    const title = hero.querySelector('.hero__title');
    if (title) title.classList.add('animated', 'animate-fade-in');
  }, 300);
  
  setTimeout(() => {
    const subtitle = hero.querySelector('.hero__subtitle');
    if (subtitle) subtitle.classList.add('animated', 'animate-fade-in');
  }, 600);
  
  setTimeout(() => {
    const cta = hero.querySelector('.hero__cta');
    if (cta) cta.classList.add('animated', 'animate-fade-in-up');
  }, 900);
}

// Imagination page interactive elements
function initImaginationInteractive() {
  const interactiveElements = document.querySelectorAll('.interactive-element');
  
  interactiveElements.forEach(element => {
    element.addEventListener('click', () => {
      // Toggle active state for this element
      element.classList.toggle('interactive-element--active');
      
      // If there's associated content to show/hide
      const targetId = element.dataset.target;
      if (targetId) {
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
          targetElement.classList.toggle('visible');
        }
      }
    });
  });
}

// Events page filtering
function initEventFilters() {
  const filterBtns = document.querySelectorAll('.event-filter');
  const events = document.querySelectorAll('.event-card');
  
  // Early exit if elements don't exist
  if (!filterBtns.length || !events.length) return;
  
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      // Update active button
      filterBtns.forEach(b => b.classList.remove('event-filter--active'));
      btn.classList.add('event-filter--active');
      
      // Get filter category
      const filter = btn.dataset.filter;
      
      // Show/hide events based on filter
      events.forEach(event => {
        if (filter === 'all' || event.dataset.category === filter) {
          event.style.display = '';
        } else {
          event.style.display = 'none';
        }
      });
    });
  });
}