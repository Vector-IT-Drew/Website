// main.js - JavaScript functionality for Vector New York Website

// Execute code when DOM content is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Vector New York Website loaded');
    
    // Initialize components
    initializeComponents();
    
    // Set up event listeners
    setupEventListeners();
    
    // Initialize effect for hero section if it exists
    if (document.querySelector('.hero-section')) {
        initSkylineEffect();
    }
    
    // Initialize smooth scrolling for section navigation
    initSmoothScrolling();
});

// Initialize Bootstrap and custom components
function initializeComponents() {
    // Initialize all Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Format price inputs with commas as thousands separators
    formatPriceInputs();
    
    // Initialize hero section effect
    if (document.querySelector('.hero-section')) {
        initSkylineEffect();
    }
    
    // Initialize contact card sticky behavior with proper offset
    initContactCardSticky();
}

// Set up event listeners for various interactions
function setupEventListeners() {
    // Add event listeners for contact form submission
    const contactForms = document.querySelectorAll('.agent-contact form');
    if (contactForms) {
        contactForms.forEach(form => {
            form.addEventListener('submit', function(event) {
                event.preventDefault();
                // Show a message that this is a demo
                alert('This is a demo form. In a real application, this would send a message to the agent.');
            });
        });
    }
    
    // Add event listener for fade effect on scroll
    window.addEventListener('scroll', function() {
        if (document.querySelector('.hero-section')) {
            animateSkyline();
        }
    });
    
    // Handle navbar transparency on scroll
    var navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        });
    }
    
    // Set up share buttons functionality
    setupShareButtons();
}

// Format price inputs with commas as users type
function formatPriceInputs() {
    const priceInputs = document.querySelectorAll('input[name="price"]');
    if (priceInputs) {
        priceInputs.forEach(input => {
            input.addEventListener('input', function(e) {
                // Remove any non-digits
                let value = this.value.replace(/[^\d]/g, '');
                
                // Format with commas if there's a value
                if (value.length) {
                    this.value = Number(value).toLocaleString();
                }
            });
            
            // When focusing, remove the formatting
            input.addEventListener('focus', function(e) {
                this.value = this.value.replace(/,/g, '');
            });
            
            // When blurring, re-apply the formatting
            input.addEventListener('blur', function(e) {
                let value = this.value.replace(/[^\d]/g, '');
                if (value.length) {
                    this.value = Number(value).toLocaleString();
                }
            });
        });
    }
}

// Set up share button functionality
function setupShareButtons() {
    const shareButtons = document.querySelectorAll('.share-buttons a');
    if (shareButtons) {
        shareButtons.forEach(button => {
            button.addEventListener('click', function(event) {
                event.preventDefault();
                
                // Get page URL and title
                const url = encodeURIComponent(window.location.href);
                const title = encodeURIComponent(document.title);
                
                // Determine which social network was clicked
                if (this.classList.contains('btn-outline-primary')) {
                    // Facebook
                    window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}`, 'facebook-share', 'width=580,height=296');
                } else if (this.classList.contains('btn-outline-info')) {
                    // Twitter
                    window.open(`https://twitter.com/intent/tweet?text=${title}&url=${url}`, 'twitter-share', 'width=550,height=235');
                } else if (this.classList.contains('btn-outline-danger')) {
                    // Email
                    window.location.href = `mailto:?subject=${title}&body=Check out this property: ${url}`;
                } else if (this.classList.contains('btn-outline-success')) {
                    // WhatsApp
                    window.open(`https://api.whatsapp.com/send?text=${title} ${url}`);
                } else if (this.classList.contains('btn-outline-secondary')) {
                    // Copy link
                    navigator.clipboard.writeText(window.location.href).then(() => {
                        alert('Link copied to clipboard!');
                    }).catch(err => {
                        console.error('Could not copy text: ', err);
                    });
                }
            });
        });
    }
}

// Initialize any effects for the hero section
function initSkylineEffect() {
    // We're using a simple background image now, no animations needed
    console.log("Hero section initialized with simple background");
}

// Smooth scrolling for section navigation
function initSmoothScrolling() {
    // Add IDs to each section if they don't have one
    const sections = document.querySelectorAll('section');
    sections.forEach((section, index) => {
        if (!section.id) {
            // Get section class name or assign a default
            const className = section.classList[0] || `section-${index + 1}`;
            section.id = className;
        }
    });

    // Handle clicks on navigation links
    const navLinks = document.querySelectorAll('.nav-link[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                // Smooth scroll to the target
                window.scrollTo({
                    top: targetElement.offsetTop - 80, // Account for fixed navbar
                    behavior: 'smooth'
                });
                
                // Update active state in navbar
                document.querySelectorAll('.nav-link').forEach(navLink => {
                    navLink.classList.remove('active');
                });
                this.classList.add('active');
            }
        });
    });
    
    // Special handling for scroll-down link on hero section
    const scrollDownLink = document.querySelector('.scroll-down-link');
    if (scrollDownLink) {
        scrollDownLink.addEventListener('click', function(e) {
            e.preventDefault();
            const contentSection = document.getElementById('content-section');
            if (contentSection) {
                const offsetPosition = contentSection.offsetTop - 70; // Account for navbar
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            } else {
                // If content section is not found, just scroll to the window height
                window.scrollTo({
                    top: window.innerHeight - 70,
                    behavior: 'smooth'
                });
            }
        });
    }
    
    // Handle all other anchor links
    document.querySelectorAll('a[href^="#"]:not(.nav-link):not(.scroll-down-link)').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                const offsetPosition = targetElement.offsetTop - 70; // Account for navbar
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Auto-highlight the current section in navbar based on scroll position
    window.addEventListener('scroll', function() {
        let currentSection = '';
        const scrollPosition = window.scrollY;
        
        // Determine which section is in view
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 100;
            const sectionHeight = section.offsetHeight;
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                currentSection = '#' + section.id;
            }
        });
        
        // Update active state in navbar
        if (currentSection) {
            document.querySelectorAll('.nav-link').forEach(navLink => {
                navLink.classList.remove('active');
                if (navLink.getAttribute('href') === currentSection) {
                    navLink.classList.add('active');
                }
            });
        }
    });
}

// Simple fade effect for hero section when scrolling
function animateSkyline() {
    // No animation needed now that we're using a simple background
    // This function remains for backward compatibility
    const scrollPosition = window.scrollY;
    const heroSection = document.querySelector('.hero-section');
    
    if (heroSection && scrollPosition > 0) {
        // Just a simple fade effect on scroll
        const opacity = Math.max(0.7, 1 - (scrollPosition * 0.001));
        heroSection.style.opacity = opacity;
    }
}

// Function to handle sticky positioning of contact card
function initContactCardSticky() {
    const contactCard = document.querySelector('.contact-card');
    const navbar = document.querySelector('.navbar');
    
    if (contactCard && navbar) {
        // Update the top position of the contact card when the page loads
        const navbarHeight = navbar.offsetHeight;
        contactCard.style.top = (navbarHeight + 20) + 'px'; // 20px extra padding
        
        // Update the top position when the window is resized
        window.addEventListener('resize', function() {
            const navbarHeight = navbar.offsetHeight;
            contactCard.style.top = (navbarHeight + 20) + 'px';
        });
        
        // Also adjust when scrolling in case the navbar changes height
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                // When scrolled, navbar might be smaller
                const navbarHeight = navbar.offsetHeight;
                contactCard.style.top = (navbarHeight + 20) + 'px';
            } else {
                // At top, navbar might be taller
                const navbarHeight = navbar.offsetHeight;
                contactCard.style.top = (navbarHeight + 20) + 'px';
            }
        });
    }
}
