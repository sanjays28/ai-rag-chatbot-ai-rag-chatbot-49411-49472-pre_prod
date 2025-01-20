// Main JavaScript file for the chatbot interface
document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const uploadBox = document.getElementById('upload-box');
    const fileInput = document.getElementById('file-input');
    const uploadStatus = document.getElementById('upload-status');
    const uploadProgress = document.getElementById('upload-progress');
    const uploadProgressBar = document.getElementById('upload-progress-bar');
    const fileInfo = document.getElementById('file-info');
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-btn');
    const errorContainer = document.getElementById('error-container');
    const loadingIndicator = document.getElementById('loading-indicator');

    // Helper function to format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // State
    let isFileUploaded = false;

    // Drag and drop handlers
    uploadBox.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadBox.classList.add('drag-over');
    });

    uploadBox.addEventListener('dragleave', () => {
        uploadBox.classList.remove('drag-over');
    });

    uploadBox.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadBox.classList.remove('drag-over');
        const file = e.dataTransfer.files[0];
        if (file && file.type === 'application/pdf') {
            handleFileUpload(file);
        } else {
            showError('Please upload a PDF file');
        }
    });

    // File input handler
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleFileUpload(file);
        }
    });

    // Handle file upload
    async function handleFileUpload(file) {
        try {
            // Display file info
            fileInfo.innerHTML = `
                <span class="file-name">${file.name}</span>
                <span class="file-size">(${formatFileSize(file.size)})</span>
            `;

            // Show progress bar
            uploadProgress.style.display = 'block';
            uploadProgressBar.style.width = '0%';
            uploadStatus.textContent = '';
            uploadStatus.className = 'upload-status';

            const formData = new FormData();
            formData.append('file', file);

            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/upload', true);

            // Track upload progress
            xhr.upload.onprogress = (e) => {
                if (e.lengthComputable) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    uploadProgressBar.style.width = percentComplete + '%';
                }
            };

            // Handle response
            xhr.onload = () => {
                if (xhr.status === 200) {
                    const data = JSON.parse(xhr.responseText);
                    isFileUploaded = true;
                    sendButton.disabled = false;
                    uploadStatus.textContent = 'PDF uploaded successfully!';
                    uploadStatus.classList.add('success');
                    showMessage('system', 'PDF uploaded successfully. You can now ask questions about its contents.');
                } else {
                    throw new Error('Upload failed');
                }
            };

            xhr.onerror = () => {
                throw new Error('Network error');
            };

            xhr.send(formData);
        } catch (error) {
            uploadStatus.textContent = 'Failed to upload PDF: ' + error.message;
            uploadStatus.classList.add('error');
            fileInfo.innerHTML = '';
        } finally {
            // Hide progress bar after a short delay
            setTimeout(() => {
                uploadProgress.style.display = 'none';
                uploadProgressBar.style.width = '0%';
            }, 1000);
        }
    }

    // Chat input handlers
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    sendButton.addEventListener('click', sendMessage);

    // Auto-resize textarea
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = userInput.scrollHeight + 'px';
    });

    // Send message function
    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message || !isFileUploaded) return;

        // Add user message to chat
        showMessage('user', message);
        userInput.value = '';
        userInput.style.height = 'auto';
        sendButton.disabled = true;

        try {
            showLoading('Thinking...');
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: message })
            });

            if (!response.ok) {
                throw new Error('Failed to get response');
            }

            const data = await response.json();
            showMessage('assistant', data.response);
        } catch (error) {
            showError('Failed to get response: ' + error.message);
        } finally {
            hideLoading();
            sendButton.disabled = false;
        }
    }

    // UI Helper functions
    function showMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        messageDiv.innerHTML = `
            <div class="message-content">
                ${role === 'user' ? 'You' : role === 'assistant' ? 'Assistant' : 'System'}: ${content}
            </div>
        `;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showError(message) {
        errorContainer.textContent = message;
        errorContainer.style.display = 'block';
        setTimeout(() => {
            errorContainer.style.display = 'none';
        }, 5000);
    }

    function showLoading(message) {
        const loadingText = loadingIndicator.querySelector('p');
        loadingText.textContent = message;
        loadingIndicator.style.display = 'flex';
    }

    function hideLoading() {
        loadingIndicator.style.display = 'none';
    }

    // Initialize
    console.log('PDF Chatbot initialized');
});
