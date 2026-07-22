const API_URL = 'http://localhost:5000/chat';

const chatContainer = document.getElementById('chatContainer');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const sendBtnText = document.getElementById('sendBtnText');
const sendBtnLoader = document.getElementById('sendBtnLoader');
const quickBtns = document.querySelectorAll('.quick-btn');

// Add message to chat
function addMessage(message, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Format message with line breaks and bold text
    const formattedMessage = message
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
    
    contentDiv.innerHTML = formattedMessage;
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Send message to backend
async function sendMessage(message) {
    if (!message.trim()) return;
    
    // Add user message
    addMessage(message, true);
    userInput.value = '';
    
    // Disable send button
    sendBtn.disabled = true;
    sendBtnText.style.display = 'none';
    sendBtnLoader.style.display = 'inline-block';
    
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        // Add bot response
        addMessage(data.reply || 'Sorry, I could not understand that.');
        
    } catch (error) {
        console.error('Error:', error);
        addMessage('Sorry, I am having trouble connecting to the server. Please make sure the backend is running on http://localhost:5000');
    } finally {
        // Re-enable send button
        sendBtn.disabled = false;
        sendBtnText.style.display = 'inline';
        sendBtnLoader.style.display = 'none';
    }
}

// Event listeners
sendBtn.addEventListener('click', () => {
    sendMessage(userInput.value);
});

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage(userInput.value);
    }
});

quickBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const question = btn.getAttribute('data-question');
        userInput.value = question;
        sendMessage(question);
    });
});

// Focus input on load
userInput.focus();