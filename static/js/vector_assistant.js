document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const chatForm = document.getElementById('chatForm');
    const userMessageInput = document.getElementById('userMessage');
    const typingIndicator = document.getElementById('typingIndicator');
    const resetChatBtn = document.getElementById('resetChatBtn');
    
    // Railway.app API URL
    const RAILWAY_API_URL = 'https://dash-production-b25c.up.railway.app';
    
    // Hide typing indicator initially
    typingIndicator.style.display = 'none';
    
    // Function to add a message to the chat
    function addMessage(sender, message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}-message`;
        
        // Create avatar element
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'chat-avatar';
        
        if (sender === 'user') {
            avatarDiv.innerHTML = '<i class="fas fa-user"></i>';
        } else {
            avatarDiv.innerHTML = '<img src="/static/images/Vector Icon.png" alt="Vector Assistant" width="24">';
        }
        
        // Create message content
        const contentDiv = document.createElement('div');
        contentDiv.className = 'chat-content';
        contentDiv.textContent = message;
        
        // Append elements
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Function to show typing indicator
    function showTypingIndicator() {
        typingIndicator.style.display = 'flex';
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Function to hide typing indicator
    function hideTypingIndicator() {
        typingIndicator.style.display = 'none';
    }
    
    // Function to send message to Railway.app API
    async function sendMessage(message) {
        try {
            showTypingIndicator();
            
            // Get stored preferences from localStorage if they exist
            const storedPreferences = localStorage.getItem('chatPreferences');
            const preferences = storedPreferences ? JSON.parse(storedPreferences) : {};
            
            // Prepare the payload
            const payload = {
                message: message
            };
            
            // Add preferences if they exist
            if (Object.keys(preferences).length > 0) {
                payload.preferences = preferences;
            }
            
            console.log("Sending to Railway API:", payload);
            
            // Call Railway.app API directly
            const response = await fetch(`${RAILWAY_API_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(payload),
                credentials: 'include' // This sends cookies if needed
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log("Received from Railway API:", data);
            
            // Store updated preferences
            if (data.preferences) {
                localStorage.setItem('chatPreferences', JSON.stringify(data.preferences));
            }
            
            hideTypingIndicator();
            return data.message || "I'm sorry, I couldn't process your request.";
            
        } catch (error) {
            console.error('Error sending message:', error);
            hideTypingIndicator();
            return "I'm sorry, I'm having trouble connecting to our servers right now. Please try again later.";
        }
    }
    
    // Function to reset chat
    async function resetChat() {
        try {
            // Clear chat messages UI
            chatMessages.innerHTML = '';
            
            // Clear stored preferences
            localStorage.removeItem('chatPreferences');
            
            // Call Railway.app reset endpoint
            await fetch(`${RAILWAY_API_URL}/reset-chat`, {
                method: 'POST',
                credentials: 'include'
            });
            
            // Add welcome message
            addMessage('assistant', 'Hi there! I'm Vector Assistant. How can I help you find your perfect NYC apartment today?');
            
        } catch (error) {
            console.error('Error resetting chat:', error);
            addMessage('assistant', 'Chat has been reset. How can I help you today?');
        }
    }
    
    // Initialize chat when modal is opened
    const vectorAssistantModal = document.getElementById('vectorAssistantModal');
    vectorAssistantModal.addEventListener('shown.bs.modal', function() {
        // Only initialize if chat is empty
        if (chatMessages.children.length === 0) {
            addMessage('assistant', "Hi there! I'm Vector Assistant. How can I help you find your perfect NYC apartment today?");
        }
        
        // Focus on input field
        userMessageInput.focus();
    });
    
    // Handle form submission
    chatForm.addEventListener('submit', async function(e) {
        e.preventDefault(); // Prevent the form from submitting normally
        
        const message = userMessageInput.value.trim();
        if (!message) return;
        
        // Clear input
        userMessageInput.value = '';
        
        // Add user message to chat
        addMessage('user', message);
        
        // Get response from API
        const response = await sendMessage(message);
        
        // Add assistant response to chat
        addMessage('assistant', response);
    });
    
    // Handle reset button
    resetChatBtn.addEventListener('click', resetChat);
});