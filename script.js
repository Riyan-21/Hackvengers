// Chat functionality
const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const aiExpertBtn = document.querySelector('.ai-expert-btn');
const liveChatBtn = document.querySelector('.live-chat-btn');
const voiceCallBtn = document.getElementById('voice-call-btn');
const chatVoiceBtn = document.getElementById('chat-voice-btn');
const voiceCallModal = document.getElementById('voice-call-modal');
const startVoiceCallBtn = document.getElementById('start-voice-call');
const endVoiceCallBtn = document.getElementById('end-voice-call');
const closeModalBtn = document.querySelector('.close-modal');
const voiceStatus = document.getElementById('voice-status');
const voiceWave = document.getElementById('voice-wave');

let currentChatMode = 'ai'; // Default to AI expert mode
let isVoiceCallActive = false;

// Sample wellness-related responses from AI
const aiResponses = {
    'hello': 'Hello! I\'m your ZenZone wellness assistant. How can I help you find your peace today?',
    'stress': 'Let\'s practice some mindfulness. Try taking three deep breaths, focusing on the present moment.',
    'anxiety': 'Remember, it\'s okay to feel anxious. Let\'s try some grounding techniques: name 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, and 1 thing you can taste.',
    'sleep': 'For better sleep, try establishing a calming bedtime routine. Dim the lights, avoid screens, and practice gentle stretching or meditation.',
    'meditation': 'Would you like to try a guided meditation? I can help you find your center and focus on your breath.',
    'default': 'I\'m here to support your wellness journey. Feel free to share what\'s on your mind, and we can explore ways to find your zen together.'
};

// Health Issues Solutions
const healthSolutions = {
    'stress': {
        title: 'Managing Stress',
        text: 'Try these stress-relief techniques:\n\n1. Practice deep breathing exercises\n2. Engage in regular physical activity\n3. Try mindfulness meditation\n4. Maintain a healthy sleep schedule\n5. Connect with supportive friends and family\n\nWould you like to try a guided breathing exercise?'
    },
    'anxiety': {
        title: 'Coping with Anxiety',
        text: 'Here are some anxiety management strategies:\n\n1. Practice the 5-4-3-2-1 grounding technique\n2. Try progressive muscle relaxation\n3. Keep a worry journal\n4. Limit caffeine and sugar intake\n5. Practice regular mindfulness exercises\n\nWould you like to try a guided anxiety relief exercise?'
    },
    'sleep': {
        title: 'Improving Sleep',
        text: 'Follow these sleep hygiene tips:\n\n1. Maintain a consistent sleep schedule\n2. Create a relaxing bedtime routine\n3. Keep your bedroom cool and dark\n4. Avoid screens before bedtime\n5. Limit caffeine and heavy meals in the evening\n\nWould you like to try a guided sleep meditation?'
    },
    'depression': {
        title: 'Managing Depression',
        text: 'Consider these self-care strategies:\n\n1. Engage in regular physical activity\n2. Practice gratitude journaling\n3. Connect with supportive people\n4. Set small, achievable goals\n5. Seek professional help when needed\n\nWould you like to try a mood-boosting exercise?'
    },
    'focus': {
        title: 'Enhancing Focus',
        text: 'Try these focus-improving techniques:\n\n1. Practice the Pomodoro technique\n2. Minimize distractions in your environment\n3. Take regular breaks\n4. Stay hydrated and eat brain-healthy foods\n5. Try mindfulness exercises\n\nWould you like to try a focus-enhancing exercise?'
    }
};

// Function to add a message to the chat
function addMessage(message, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Function to get AI response
async function getAIResponse(userMessage) {
    try {
        const response = await fetch('http://localhost:5500/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: userMessage })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        return data.response;
    } catch (error) {
        console.error('Error:', error);
        return 'Sorry, I encountered an error. Please try again.';
    }
}

// Voice Call Functions
async function startVoiceCall() {
    if (!isVoiceCallActive) {
        isVoiceCallActive = true;
        startVoiceCallBtn.disabled = true;
        endVoiceCallBtn.disabled = false;
        voiceStatus.textContent = 'Listening...';
        voiceWave.style.display = 'flex';
        
        try {
            const response = await fetch('http://localhost:5500/start_voice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to start voice call');
            }
            
            const data = await response.json();
            voiceStatus.textContent = data.status;
            
            // Start polling for voice responses
            pollVoiceResponses();
        } catch (error) {
            console.error('Error:', error);
            voiceStatus.textContent = 'Error starting voice call';
            endVoiceCall();
        }
    }
}

async function pollVoiceResponses() {
    if (!isVoiceCallActive) return;
    
    try {
        const response = await fetch('http://localhost:5500/get_voice_response');
        if (!response.ok) {
            throw new Error('Failed to get voice response');
        }
        
        const data = await response.json();
        if (data.message) {
            addMessage(data.message, false);
            voiceStatus.textContent = 'Listening...';
        }
        
        // Continue polling
        setTimeout(pollVoiceResponses, 1000);
    } catch (error) {
        console.error('Error:', error);
        setTimeout(pollVoiceResponses, 1000);
    }
}

async function endVoiceCall() {
    if (isVoiceCallActive) {
        isVoiceCallActive = false;
        startVoiceCallBtn.disabled = false;
        endVoiceCallBtn.disabled = true;
        voiceStatus.textContent = 'Call ended';
        voiceWave.style.display = 'none';
        
        try {
            await fetch('http://localhost:5500/end_voice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
        } catch (error) {
            console.error('Error:', error);
        }
        
        addMessage('Voice call ended. Would you like to continue chatting?', false);
    }
}

// Modal Functions
function openVoiceCallModal() {
    voiceCallModal.style.display = 'block';
}

function closeVoiceCallModal() {
    voiceCallModal.style.display = 'none';
    if (isVoiceCallActive) {
        endVoiceCall();
    }
}

// Event Listeners
sendButton.addEventListener('click', async () => {
    const message = messageInput.value.trim();
    if (message) {
        // Add user message to chat
        addMessage(message, true);
        messageInput.value = '';
        
        if (currentChatMode === 'ai') {
            // Show loading indicator
            const loadingMessage = addMessage('Thinking...', false);
            
            try {
                // Get response from chat.py via server
                const response = await getAIResponse(message);
                
                // Remove loading message
                chatMessages.removeChild(loadingMessage);
                
                // Add AI response to chat
                addMessage(response);
            } catch (error) {
                // Remove loading message
                chatMessages.removeChild(loadingMessage);
                addMessage('Sorry, I encountered an error. Please try again.');
            }
        } else {
            // For live chat, you would typically send the message to a server
            addMessage('Connecting to a wellness professional...');
        }
    }
});

// Handle Enter key in message input
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendButton.click();
    }
});

// Voice call button event listeners
voiceCallBtn.addEventListener('click', openVoiceCallModal);
chatVoiceBtn.addEventListener('click', openVoiceCallModal);
startVoiceCallBtn.addEventListener('click', startVoiceCall);
endVoiceCallBtn.addEventListener('click', endVoiceCall);
closeModalBtn.addEventListener('click', closeVoiceCallModal);

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    if (e.target === voiceCallModal) {
        closeVoiceCallModal();
    }
});

// Chat mode switching
aiExpertBtn.addEventListener('click', () => {
    currentChatMode = 'ai';
    aiExpertBtn.style.backgroundColor = 'var(--primary-color)';
    aiExpertBtn.style.color = 'white';
    liveChatBtn.style.backgroundColor = 'white';
    liveChatBtn.style.color = 'var(--primary-color)';
    addMessage('Switched to AI Wellness Expert mode. How can I help you find your zen?');
});

liveChatBtn.addEventListener('click', () => {
    currentChatMode = 'live';
    liveChatBtn.style.backgroundColor = 'var(--primary-color)';
    liveChatBtn.style.color = 'white';
    aiExpertBtn.style.backgroundColor = 'white';
    aiExpertBtn.style.color = 'var(--primary-color)';
    addMessage('Connecting you to a live wellness professional...');
});

// Health Issues Event Listeners
document.querySelectorAll('.health-issue-btn').forEach(button => {
    button.addEventListener('click', () => {
        const issue = button.getAttribute('data-issue');
        const solution = healthSolutions[issue];
        
        if (solution) {
            document.getElementById('solution-title').textContent = solution.title;
            document.getElementById('solution-text').textContent = solution.text;
            
            // Add the solution to the chat
            addMessage(`Selected: ${solution.title}`, true);
            setTimeout(() => {
                addMessage(solution.text);
            }, 1000);
        }
    });
});

// Login/Signup functionality
const loginBtn = document.querySelector('.login-btn');
const signupBtn = document.querySelector('.signup-btn');

if (loginBtn && signupBtn) {
    loginBtn.addEventListener('click', (e) => {
        e.preventDefault();
        window.location.href = 'login.html?mode=login';
    });

    signupBtn.addEventListener('click', (e) => {
        e.preventDefault();
        window.location.href = 'login.html?mode=signup';
    });
}

// Initialize chat with welcome message
window.addEventListener('load', () => {
    addMessage('Welcome to ZenZone! I\'m your AI wellness assistant. How can I help you find your peace today?');
});

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Scroll to chat section
const startChatBtn = document.getElementById('start-chat-btn');
const chatSection = document.getElementById('chat-section');

startChatBtn.addEventListener('click', () => {
    chatSection.scrollIntoView({ behavior: 'smooth' });
    // Focus on the message input after scrolling
    setTimeout(() => {
        messageInput.focus();
    }, 1000);
}); 