document.addEventListener('DOMContentLoaded', function() {
    // Initialize the chat when the DOM is fully loaded
    initializeChat();
    
    // Start the chat automatically when the page loads
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        console.log("Chat session initialized");
        console.log("FULL RESPONSE DATA:", JSON.stringify(data));
        console.log("show_listings flag:", data.show_listings);
        console.log("listings array:", data.listings ? data.listings.length : 0);
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
                }),
                // Add timeout to prevent hanging requests
                timeout: 30000
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server responded with status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Hide typing indicator
                showTypingIndicator(false);
                
                // Add assistant response to chat
                addMessage(data.response || "I'm sorry, I couldn't process your request at this time.", 'assistant');
                
                // Update the listing count indicator if available
                updateListingCount(data.listing_count);
                
                // If there are listings to display
                if (data.listings && data.listings.length > 0) {
                    const listingsElement = document.createElement('div');
                    listingsElement.innerHTML = formatListings(data.listings);
                    addMessage(listingsElement, 'assistant');
                }
                
                // Scroll to bottom of chat with a slight delay to ensure content is fully rendered
                scrollChatToBottom(100);
            })
            .catch(error => {
                console.error('Error getting initial message:', error);
                showTypingIndicator(false);
                addMessage("I'm sorry, I encountered an error connecting to the assistant. Please try refreshing the page or try again later.", 'assistant');
                scrollChatToBottom(100);
            });
        }
        
        // Auto-focus the input field
        document.getElementById('userMessage').focus();
    });
    
    // Function to initialize chat
    function initializeChat() {
        // Show typing indicator
        showTypingIndicator(true);
        
        // Start a new chat session
        fetch('/start_chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'include' // Include cookies for session management
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Chat session initialized");
            
            // Hide typing indicator
            showTypingIndicator(false);
            
            // Display the initial welcome message
            if (data.initial_message) {
                addMessage(data.initial_message, 'assistant');
                scrollChatToBottom(100);
            }
        })
        .catch(error => {
            console.error('Error initializing chat:', error);
            showTypingIndicator(false);
            addMessage("I'm sorry, I encountered an error connecting to the assistant. Please try refreshing the page or try again later.", 'assistant');
            scrollChatToBottom(100);
        });
    }
    
    // Function to reset chat
    function resetChat() {
        // Clear the chat display
        document.getElementById('chatMessages').innerHTML = '';
        
        // Show typing indicator
        showTypingIndicator(true);
        
        // Call the reset endpoint
        fetch('/reset_chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Hide typing indicator
            showTypingIndicator(false);
            
            if (data.status === 'success') {
                // Display the welcome message
                addMessage(data.welcome_message, 'assistant');
                
                // Clear the input field
                document.getElementById('userMessage').value = '';
                
                // Scroll to bottom of chat
                scrollChatToBottom(100);
            } else {
                // Show error message
                addMessage("I'm sorry, I encountered an error resetting the chat. Please try refreshing the page.", 'assistant');
            }
        })
        .catch(error => {
            console.error('Error resetting chat:', error);
            showTypingIndicator(false);
            addMessage("I'm sorry, I encountered an error resetting the chat. Please try refreshing the page.", 'assistant');
            scrollChatToBottom(100);
        });
    }
    
    // Function to send message
    function sendMessage() {
        const userMessage = document.getElementById('userMessage').value.trim();
        if (!userMessage) return;
        
        // Add user message to chat
        addMessage(userMessage, 'user');
        
        // Clear input field
        document.getElementById('userMessage').value = '';
        
        // Show typing indicator
        showTypingIndicator(true);
        
        console.log("Sending message to server:", userMessage);
        
        // Send message to server with explicit timeout and error handling
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ message: userMessage }),
            credentials: 'include' // Include cookies for session management
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("FULL RESPONSE DATA:", JSON.stringify(data));
            console.log("show_listings flag:", data.show_listings);
            console.log("listings array:", data.listings ? data.listings.length : 0);
            console.log("Received response from server:", data);
            
            // Hide typing indicator
            showTypingIndicator(false);
            
            // Add assistant response to chat
            const responseText = data.response || data.message || "I'm sorry, I couldn't process your request at this time.";
            addMessage(responseText, 'assistant');
            
            // Update the listing count indicator if available
            if (data.listing_count) {
                console.log("Updating listing count:", data.listing_count);
                updateListingCount(data.listing_count);
            }
            
            // Find the last message element (the one we just added)
            const lastMessage = document.querySelector('#chatMessages .message:last-child .message-content');
            
            // Check if listings are included in the response AND lastMessage exists
            if (data.listings && data.listings.length > 0 && lastMessage) {
                console.log("Listings found:", data.listings.length);
                console.log("First listing:", data.listings[0]);
                
                // Create listings element
                const listingsElement = document.createElement('div');
                listingsElement.className = 'listings-section';
                listingsElement.innerHTML = formatListings(data.listings);
                
                // Append listings to the last message
                lastMessage.appendChild(listingsElement);
                console.log("Listings added to chat");
            } else {
                console.log("No listings in response or lastMessage not found:", 
                           "Listings:", data.listings ? data.listings.length : 0,
                           "lastMessage:", lastMessage ? "exists" : "null");
            }
            
            // Scroll to bottom of chat
            scrollChatToBottom(100);
        })
        .catch(error => {
            console.error('Error sending message:', error);
            showTypingIndicator(false);
            addMessage("I'm sorry, there was an error processing your request. Please try again later.", 'assistant');
            scrollChatToBottom(100);
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
        
        // Create a container for the message content
        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');
        
        // Check if message is a string or an HTML element
        if (typeof message === 'string') {
            // Convert newlines to <br> tags for string messages
            messageContent.innerHTML = message.replace(/\n/g, '<br>');
        } else {
            // If it's an HTML element, append it directly
            messageContent.appendChild(message);
        }
        
        // Append the message content to the message element
        messageElement.appendChild(messageContent);
        
        // Append the message element to the chat
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
    
    // Function to format listings for display in chat
    function formatListings(listings) {
        if (!listings || listings.length === 0) {
            return '<div class="no-listings">No listings available at this time.</div>';
        }
        
        let listingsHTML = '<div class="listings-container" style="display: flex; flex-direction: column; gap: 16px; margin-top: 16px;">';
        
        listings.forEach(listing => {
            // Default image URL
            let imageUrl = '';
            
            // Try to get the first image from unit_images
            try {
                if (listing.unit_images && listing.unit_images.length > 0) {
                    // Handle both string and array formats
                    if (typeof listing.unit_images === 'string') {
                        // Try to parse if it's a JSON string
                        try {
                            const images = JSON.parse(listing.unit_images);
                            if (images && images.length > 0) {
                                imageUrl = images[0];
                            }
                        } catch (e) {
                            console.log("Error parsing unit_images string:", e);
                        }
                    } else if (Array.isArray(listing.unit_images) && listing.unit_images.length > 0) {
                        imageUrl = listing.unit_images[0];
                    }
                }
            } catch (error) {
                console.error("Error processing unit images:", error);
            }
            
            // Format the rent with commas
            const formattedRent = listing.actual_rent ? listing.actual_rent.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") : "N/A";
            
            // Handle building amenities safely
            let buildingAmenities = [];
            try {
                if (listing.building_amenities) {
                    if (typeof listing.building_amenities === 'string') {
                        buildingAmenities = JSON.parse(listing.building_amenities);
                    } else if (Array.isArray(listing.building_amenities)) {
                        buildingAmenities = listing.building_amenities;
                    }
                }
            } catch (error) {
                console.error("Error processing building amenities:", error);
            }
            
            // Get the listing ID
            const listingId = listing.unit_id || '';
            
            // Create the listing card with a clickable link
            listingsHTML += `
                <a href="https://vectorny.com/listings/${listingId}" target="_blank" style="text-decoration: none; color: inherit; cursor: pointer;">
                    <div class="listing-card" style="display: flex; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.1); background: white; max-width: 100%; transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 6px 12px rgba(0,0,0,0.15)';" onmouseout="this.style.transform=''; this.style.boxShadow='0 4px 8px rgba(0,0,0,0.1)';">
                        <div class="listing-image" style="width: 120px; min-width: 120px; height: 120px; overflow: hidden; position: relative;">
                            <img src="${imageUrl}" alt="${listing.address} ${listing.unit}" 
                                 style="width: 100%; height: 100%; object-fit: cover;"
                                 onerror="this.onerror=null; this.src='https://dl.dropboxusercontent.com/scl/fi/erhz52z0z7lskr8ru5v1h/img-coming-soon-5.jpeg?rlkey=bf8j1tpvtqb2q02tcjy0mdp3v&st=grqntgpl&dl=0';">
                        </div>
                        <div class="listing-details" style="flex: 1; padding: 12px; display: flex; flex-direction: column; justify-content: space-between;">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                <div>
                                    <h3 class="listing-address" style="margin: 0 0 4px 0; font-size: 16px; font-weight: 600;">${listing.address} #${listing.unit}</h3>
                                    <div class="listing-neighborhood" style="font-size: 14px; color: #666; margin-bottom: 4px;">${listing.neighborhood || ''}, ${listing.borough || ''}</div>
                                    <div class="listing-specs" style="font-size: 14px; margin-bottom: 4px;">
                                        <span class="listing-beds">${listing.beds} Bed${listing.beds !== 1 ? 's' : ''}</span> • 
                                        <span class="listing-baths">${listing.baths} Bath${listing.baths !== 1 ? 's' : ''}</span>
                                        ${listing.sqft ? ` • <span class="listing-sqft">${listing.sqft} sq ft</span>` : ''}
                                    </div>
                                </div>
                                <div class="listing-rent" style="font-size: 18px; font-weight: 700; color: #1a73e8;">$${formattedRent}</div>
                            </div>
                            
                            <div class="listing-amenities" style="font-size: 13px; color: #666;">
                                ${buildingAmenities && buildingAmenities.length > 0 
                                    ? `<div style="margin-top: 4px;"><span style="font-weight: 500;">Amenities:</span> ${buildingAmenities.slice(0, 3).join(', ')}${buildingAmenities.length > 3 ? '...' : ''}</div>` 
                                    : ''}
                            </div>
                        </div>
                    </div>
                </a>
            `;
        });
        
        listingsHTML += '</div>';
        return listingsHTML;
    }
});