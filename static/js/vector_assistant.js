document.addEventListener('DOMContentLoaded', function() {
    // Initialize the chat when the DOM is fully loaded
    initializeChat();
    
    // Start the chat automatically when the page loads
    fetch('/start_chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        console.log("Chat session initialized");
    })
    .catch(error => {
        console.error('Error starting chat:', error);
    });
    
    // Setup event listeners
    document.getElementById('chatForm').addEventListener('submit', function(e) {
        e.preventDefault();
        sendMessage();
    });
    
    // Auto-scroll when user types input
    document.getElementById('userMessage').addEventListener('input', function() {
        scrollChatToBottom();
    });
    
    document.getElementById('resetChatBtn').addEventListener('click', function() {
        resetChat();
    });
    
    // Helper function to properly scroll chat to bottom
    function scrollChatToBottom(delay = 0) {
        setTimeout(() => {
            const chatMessages = document.getElementById('chatMessages');
            if (chatMessages) {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }, delay);
    }
    
    // Make scrolling function available globally in this scope
    window.scrollChatToBottom = scrollChatToBottom;
    
    // Show welcome message from the API when the modal is opened
    document.getElementById('vectorAssistantModal').addEventListener('shown.bs.modal', function() {
        if (document.getElementById('chatMessages').children.length === 0) {
            // Show typing indicator
            showTypingIndicator(true);
            
            // Send an empty message to get initial response from the API
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: "Hello"
                })
            })
            .then(response => response.json())
            .then(data => {
                // Hide typing indicator
                showTypingIndicator(false);
                
                // Add assistant response to chat
                addMessage(data.response, 'assistant');
                
                // Update the listing count indicator if available
                updateListingCount(data.listing_count);
                
                // If there are listings to display
                if (data.listings && data.listings.length > 0) {
                    addListings(data.listings, data.alternative_listings || []);
                }
                
                // Scroll to bottom of chat with a slight delay to ensure content is fully rendered
                scrollChatToBottom(100);
            })
            .catch(error => {
                console.error('Error getting initial message:', error);
                showTypingIndicator(false);
                addMessage("I'm sorry, I encountered an error connecting to the assistant. Please try again later.", 'assistant');
            });
        }
        
        // Auto-focus the input field
        document.getElementById('userMessage').focus();
    });
    
    // Function to initialize chat
    function initializeChat() {
        // Clear any existing messages
        document.getElementById('chatMessages').innerHTML = '';
        
        // Reset listing count indicator
        updateListingCount(null);
    }
    
    // Function to reset chat
    function resetChat() {
        fetch('/reset_chat', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                initializeChat();
                
                // Show typing indicator
                showTypingIndicator(true);
                
                // Get initial message from API after reset
                fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: "Hello"
                    })
                })
                .then(response => response.json())
                .then(data => {
                    // Hide typing indicator
                    showTypingIndicator(false);
                    
                    // Add assistant response to chat
                    addMessage(data.response, 'assistant');
                    
                    // Update the listing count indicator if available
                    updateListingCount(data.listing_count);
                    
                    // If there are listings to display
                    if (data.listings && data.listings.length > 0) {
                        addListings(data.listings, data.alternative_listings || []);
                    }
                    
                    // Scroll to bottom of chat with a slight delay to ensure content is fully rendered
                    scrollChatToBottom(100);
                })
                .catch(error => {
                    console.error('Error getting initial message after reset:', error);
                    showTypingIndicator(false);
                    addMessage("I'm sorry, I encountered an error connecting to the assistant. Please try again.", 'assistant');
                });
            }
        })
        .catch(error => {
            console.error('Error resetting chat:', error);
        });
    }
    
    // Function to send message
    function sendMessage() {
        const userMessageInput = document.getElementById('userMessage');
        const userMessageText = userMessageInput.value.trim();
        
        if (userMessageText === '') return;
        
        // Add user message to chat
        addMessage(userMessageText, 'user');
        
        // Clear input field
        userMessageInput.value = '';
        
        // Show typing indicator
        showTypingIndicator(true);
        
        // Send message to server
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: userMessageText
            })
        })
        .then(response => response.json())
        .then(data => {
            // Hide typing indicator
            showTypingIndicator(false);
            
            // Add assistant response to chat
            addMessage(data.response, 'assistant');
            
            // Update the listing count indicator if available
            updateListingCount(data.listing_count);
            
            // If there are listings to display
            if (data.listings && data.listings.length > 0) {
                addListings(data.listings, data.alternative_listings || []);
            }
            
            // Scroll to bottom of chat with a slight delay to ensure content is fully rendered
            scrollChatToBottom(100);
        })
        .catch(error => {
            console.error('Error sending message:', error);
            showTypingIndicator(false);
            addMessage("I'm sorry, I encountered an error. Please try again later.", 'assistant');
        });
    }
    
    // Function to update listing count indicator
    function updateListingCount(count) {
        const modalHeader = document.querySelector('#vectorAssistantModal .modal-header');
        
        // Remove existing count badge if present
        const existingBadge = modalHeader.querySelector('.listing-count-badge');
        if (existingBadge) {
            existingBadge.remove();
        }
        
        // Add new count badge if count is available
        if (count !== null && count !== undefined) {
            const countBadge = document.createElement('div');
            countBadge.classList.add('listing-count-badge', 'ms-auto', 'badge', 'bg-info');
            countBadge.textContent = `${count} matching listings`;
            
            // Insert before the close button
            const closeButton = modalHeader.querySelector('.btn-close');
            modalHeader.insertBefore(countBadge, closeButton);
        }
    }
    
    // Function to add message to chat
    function addMessage(message, sender) {
        const chatMessages = document.getElementById('chatMessages');
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);
        
        // Convert newlines to <br> tags
        const formattedMessage = message.replace(/\n/g, '<br>');
        messageElement.innerHTML = formattedMessage;
        
        chatMessages.appendChild(messageElement);
        
        // Scroll to bottom of chat with a slight delay for smooth scrolling
        scrollChatToBottom(50);
    }
    
    // Function to add listings to chat
    function addListings(listings, alternativeListings) {
        const chatMessages = document.getElementById('chatMessages');
        
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', 'assistant');
        messageElement.innerHTML = `Here ${listings.length === 1 ? 'is a listing' : 'are some listings'} that might interest you:`;
        
        chatMessages.appendChild(messageElement);
        
        // Add listings container
        const listingsContainer = document.createElement('div');
        listingsContainer.classList.add('listing-container');
        
        // Add each listing
        listings.forEach(listing => {
            const listingCard = createListingCard(listing);
            listingsContainer.appendChild(listingCard);
        });
        
        chatMessages.appendChild(listingsContainer);
        
        // Add alternative suggestions if available
        if (alternativeListings && alternativeListings.length > 0) {
            const alternativeMessage = document.createElement('div');
            alternativeMessage.classList.add('message', 'assistant');
            alternativeMessage.innerHTML = "If those don't quite match what you're looking for, here are some alternatives:";
            
            chatMessages.appendChild(alternativeMessage);
            
            const alternativeContainer = document.createElement('div');
            alternativeContainer.classList.add('listing-container');
            
            // Add each alternative listing
            alternativeListings.forEach(listing => {
                const listingCard = createListingCard(listing);
                alternativeContainer.appendChild(listingCard);
            });
            
            chatMessages.appendChild(alternativeContainer);
        }
        
        // Scroll to bottom of chat with a slight delay for smooth scrolling
        scrollChatToBottom(100);
    }
    
    // Function to create a listing card
    function createListingCard(listing) {
        const card = document.createElement('div');
        card.classList.add('listing-card');
        
        // Create image container
        const imgContainer = document.createElement('div');
        imgContainer.classList.add('listing-img');
        
        // Check if we have an image URL from the API
        if (listing.image_url && listing.image_url.trim() !== '') {
            // Create and add an actual image
            const img = document.createElement('img');
            img.src = listing.image_url;
            img.alt = listing.title || 'Property Image';
            img.classList.add('property-thumbnail');
            imgContainer.appendChild(img);
        } else {
            // Fallback to building icon if no image URL
            const icon = document.createElement('i');
            icon.classList.add('fas', 'fa-building');
            imgContainer.appendChild(icon);
        }
        
        // Create details container
        const details = document.createElement('div');
        details.classList.add('listing-details');
        
        // Create title
        const title = document.createElement('div');
        title.classList.add('listing-title');
        title.textContent = listing.title;
        
        // Create info
        const info = document.createElement('div');
        info.classList.add('listing-info');
        
        // Add bedrooms
        const bedrooms = document.createElement('span');
        bedrooms.innerHTML = `<i class="fas fa-bed"></i> ${listing.beds}`;
        
        // Add bathrooms
        const bathrooms = document.createElement('span');
        bathrooms.innerHTML = `<i class="fas fa-bath"></i> ${listing.baths}`;
        
        // Add price
        const price = document.createElement('span');
        price.classList.add('listing-price');
        price.innerHTML = `<i class="fas fa-tag"></i> $${Number(listing.price).toLocaleString()}`;
        
        // Add all info to info container
        info.appendChild(bedrooms);
        info.appendChild(bathrooms);
        info.appendChild(price);
        
        // Create action
        const action = document.createElement('div');
        action.classList.add('listing-action');
        
        // Add view button
        const viewButton = document.createElement('a');
        viewButton.href = `/listings/${listing.id}`;
        viewButton.classList.add('btn', 'btn-sm', 'btn-outline-primary');
        viewButton.textContent = 'View Details';
        action.appendChild(viewButton);
        
        // Assemble details
        details.appendChild(title);
        details.appendChild(info);
        details.appendChild(action);
        
        // Assemble card
        card.appendChild(imgContainer);
        card.appendChild(details);
        
        return card;
    }
    
    // Function to show/hide typing indicator
    function showTypingIndicator(show) {
        const typingIndicator = document.getElementById('typingIndicator');
        
        if (show) {
            typingIndicator.style.display = 'inline-flex';
        } else {
            typingIndicator.style.display = 'none';
        }
    }
});