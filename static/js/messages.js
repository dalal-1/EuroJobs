/**
 * Messages.js - JavaScript for messaging functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Auto-scroll to bottom of conversation
    const conversationBody = document.querySelector('.conversation-body');
    
    if (conversationBody) {
        conversationBody.scrollTop = conversationBody.scrollHeight;
        
        // Observe for new messages and scroll down
        const observer = new MutationObserver(() => {
            conversationBody.scrollTop = conversationBody.scrollHeight;
        });
        
        observer.observe(conversationBody, { childList: true, subtree: true });
    }
    
    // Message form submit handling
    const messageForm = document.getElementById('message-form');
    
    if (messageForm) {
        messageForm.addEventListener('submit', function(e) {
            const messageInput = document.getElementById('body');
            
            if (!messageInput.value.trim()) {
                e.preventDefault();
                return false;
            }
            
            // On successful submission, clear the input field
            // This happens after the form is submitted and the page reloads
        });
    }
    
    // Message input auto-resize
    const messageInput = document.getElementById('body');
    
    if (messageInput) {
        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        
        // Initial height
        messageInput.style.height = 'auto';
        messageInput.style.height = (messageInput.scrollHeight) + 'px';
        
        // Focus the input when page loads
        messageInput.focus();
    }
    
    // Conversation item click handler (for mobile)
    const conversationItems = document.querySelectorAll('.conversation-item');
    
    conversationItems.forEach(item => {
        item.addEventListener('click', function() {
            // Add active class to clicked item
            conversationItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Highlight active conversation in the sidebar
    const activeConversationId = getCurrentConversationId();
    
    if (activeConversationId) {
        const activeItem = document.querySelector(`.conversation-item[data-conversation-id="${activeConversationId}"]`);
        
        if (activeItem) {
            activeItem.classList.add('active');
        }
    }
    
    // Search functionality for conversations
    const searchInput = document.getElementById('conversation-search');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase().trim();
            const conversations = document.querySelectorAll('.conversation-item');
            
            conversations.forEach(conversation => {
                const name = conversation.querySelector('.conversation-name').textContent.toLowerCase();
                const message = conversation.querySelector('.conversation-message').textContent.toLowerCase();
                
                if (name.includes(query) || message.includes(query)) {
                    conversation.style.display = '';
                } else {
                    conversation.style.display = 'none';
                }
            });
        });
    }
    
    // Emoji picker functionality (simplified version)
    const emojiButton = document.getElementById('emoji-button');
    
    if (emojiButton && messageInput) {
        const emojis = ['😀', '😁', '😂', '🤣', '😃', '😄', '😅', '😆', '😉', '😊', '😋', '😎', '😍', '😘', '🙂', '🤔', '👍', '👏', '👋', '❤️'];
        
        emojiButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Create and show emoji picker
            let emojiPicker = document.getElementById('emoji-picker');
            
            if (!emojiPicker) {
                emojiPicker = document.createElement('div');
                emojiPicker.id = 'emoji-picker';
                emojiPicker.className = 'emoji-picker';
                emojiPicker.style.position = 'absolute';
                emojiPicker.style.bottom = '70px';
                emojiPicker.style.right = '20px';
                emojiPicker.style.backgroundColor = 'white';
                emojiPicker.style.border = '1px solid #e9ecef';
                emojiPicker.style.borderRadius = '10px';
                emojiPicker.style.padding = '10px';
                emojiPicker.style.display = 'grid';
                emojiPicker.style.gridTemplateColumns = 'repeat(5, 1fr)';
                emojiPicker.style.gap = '5px';
                emojiPicker.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.1)';
                emojiPicker.style.zIndex = '1000';
                
                // Add emojis
                emojis.forEach(emoji => {
                    const emojiButton = document.createElement('button');
                    emojiButton.type = 'button';
                    emojiButton.className = 'emoji-item';
                    emojiButton.textContent = emoji;
                    emojiButton.style.border = 'none';
                    emojiButton.style.background = 'none';
                    emojiButton.style.fontSize = '1.5rem';
                    emojiButton.style.cursor = 'pointer';
                    emojiButton.style.width = '40px';
                    emojiButton.style.height = '40px';
                    emojiButton.style.borderRadius = '5px';
                    emojiButton.style.transition = 'all 0.2s ease';
                    
                    emojiButton.addEventListener('mouseenter', function() {
                        this.style.backgroundColor = '#f8f9fc';
                    });
                    
                    emojiButton.addEventListener('mouseleave', function() {
                        this.style.backgroundColor = 'transparent';
                    });
                    
                    emojiButton.addEventListener('click', function() {
                        // Insert emoji at cursor position
                        const cursorPos = messageInput.selectionStart;
                        const textBefore = messageInput.value.substring(0, cursorPos);
                        const textAfter = messageInput.value.substring(cursorPos);
                        
                        messageInput.value = textBefore + emoji + textAfter;
                        
                        // Update cursor position and trigger resize
                        messageInput.selectionStart = cursorPos + emoji.length;
                        messageInput.selectionEnd = cursorPos + emoji.length;
                        messageInput.focus();
                        
                        // Trigger input event to resize textarea
                        const inputEvent = new Event('input', { bubbles: true });
                        messageInput.dispatchEvent(inputEvent);
                        
                        // Hide emoji picker
                        emojiPicker.style.display = 'none';
                    });
                    
                    emojiPicker.appendChild(emojiButton);
                });
                
                document.querySelector('.conversation-footer').appendChild(emojiPicker);
            } else {
                // Toggle visibility
                emojiPicker.style.display = emojiPicker.style.display === 'none' ? 'grid' : 'none';
            }
            
            // Close when clicking outside
            document.addEventListener('click', function closeEmojiPicker(e) {
                if (e.target !== emojiButton && !emojiPicker.contains(e.target)) {
                    emojiPicker.style.display = 'none';
                    document.removeEventListener('click', closeEmojiPicker);
                }
            });
        });
    }
});

/**
 * Get the ID of the current active conversation from the URL
 * @returns {string|null} The conversation ID or null if not found
 */
function getCurrentConversationId() {
    const path = window.location.pathname;
    const match = path.match(/\/messages\/conversation\/(\d+)/);
    
    if (match && match[1]) {
        return match[1];
    }
    
    return null;
}
