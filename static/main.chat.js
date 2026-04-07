/**
 * Agentic AI Console - Frontend Logic
 * This script handles user interactions, message rendering, 
 * file path detection, and communication with the FastAPI backend.
 */

// ── DOM ELEMENTS ─────────────────────────────────────────────────────────────
const respond = document.getElementById('respond');
const prompt  = document.getElementById('prompt');
const submit  = document.getElementById('submit');
const filePreview = document.getElementById('file-preview');
const filePreviewPath = document.getElementById('file-preview-path');

// ── CONSTANTS ────────────────────────────────────────────────────────────────
// Regex to detect Windows (C:\...) and Unix (/...) file paths
const FILE_PATH_REGEX = /([A-Za-z]:\\(?:[^\\\/:*?"<>|\r\n]+\\)*[^\\\/:*?"<>|\r\n]*|\/(?:[^\/\0\s]+\/)*[^\/\0\s]+\.\w+)/g;

// ── UTILITIES ────────────────────────────────────────────────────────────────

/**
 * Extracts all file paths from a string of text.
 * @param {string} text - The text to scan.
 * @returns {string[]} - Array of detected paths.
 */
function detectFilePaths(text) {
    return [...text.matchAll(FILE_PATH_REGEX)].map(m => m[0]);
}

/**
 * Wraps detected file paths in a styled <span> with an appropriate icon.
 * @param {string} text - The source message text.
 * @returns {string} - HTML string with path "chips".
 */
function renderFilePaths(text) {
    return text.replace(FILE_PATH_REGEX, (match) => {
        // Simple extension-based icon mapping
        const icon = match.endsWith('.py') ? 'fa-python' :
                     match.endsWith('.js') ? 'fa-js' :
                     match.endsWith('.json') ? 'fa-brackets-curly' :
                     match.endsWith('.txt') || match.endsWith('.md') ? 'fa-file-lines' :
                     'fa-file-code';
        return `<span class="file-chip"><i class="fas ${icon}"></i>${match}</span>`;
    });
}

// ── UI ACTIONS ───────────────────────────────────────────────────────────────

/**
 * Appends a message bubble to the chat container.
 * @param {string} text - The message content.
 * @param {string} role - 'user' or 'agent'.
 */
function addMessage(text, role) {
    const row = document.createElement('div');
    row.className = `message-row ${role}`;

    const bubble = document.createElement('div');
    bubble.className = `bubble ${role}`;

    if (role === 'agent') {
        // Agent bubbles include a microchip icon and path rendering
        const icon = document.createElement('i');
        icon.className = 'fas fa-microchip agent-icon';
        bubble.appendChild(icon);

        const span = document.createElement('span');
        span.innerHTML = renderFilePaths(text);
        bubble.appendChild(span);
    } else {
        // User bubbles just render paths
        bubble.innerHTML = renderFilePaths(text);
    }

    row.appendChild(bubble);
    respond.appendChild(row);
    
    // Auto-scroll to bottom of the console
    respond.scrollTop = respond.scrollHeight;
    return row;
}

/**
 * Displays a "Processing" state indicator.
 */
function showThinking() {
    const el = document.createElement('div');
    el.className = 'thinking';
    el.id = 'thinking';
    el.innerHTML = `<i class="fas fa-microchip" style="color:var(--accent);font-size:0.8rem"></i> Processing <div class="dots"><span></span><span></span><span></span></div>`;
    respond.appendChild(el);
    respond.scrollTop = respond.scrollHeight;
}

/**
 * Removes the "Processing" indicator.
 */
function hideThinking() {
    document.getElementById('thinking')?.remove();
}

/**
 * Sends the user message to the backend and handles the response.
 */
async function sendMessage() {
    const text = prompt.value.trim();
    if (!text) return;

    // 1. Show user message and reset input
    addMessage(text, 'user');
    prompt.value = '';
    prompt.style.height = 'auto';
    filePreview.classList.remove('visible');
    
    // 2. Disable UI during processing
    submit.disabled = true;
    showThinking();

    try {
        // 3. POST request to /agent endpoint
        const res = await fetch('/agent', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: text })
        });

        const data = await res.json();


        hideThinking();
        
        // 4. Render agent response
        addMessage(data.response || 'No response generated.', 'agent');
    } catch (err) {
        hideThinking();
        addMessage('Connection error. Is the server running?', 'agent');
        console.error("Fetch Error:", err);
    } finally {
        // 5. Re-enable UI
        submit.disabled = false;
        prompt.focus();
    }
}

// ── EVENT LISTENERS ─────────────────────────────────────────────────────────

// Handle textarea auto-resize and path preview
prompt.addEventListener('input', () => {
    prompt.style.height = 'auto';
    prompt.style.height = Math.min(prompt.scrollHeight, 140) + 'px';

    // Show path preview if one or more paths are detected
    const paths = detectFilePaths(prompt.value);
    if (paths.length > 0) {
        filePreviewPath.textContent = paths.join('  ·  ');
        filePreview.classList.add('visible');
    } else {
        filePreview.classList.remove('visible');
    }
});

// Enter to send, Shift+Enter for newline
prompt.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

submit.addEventListener('click', sendMessage);
