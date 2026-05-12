const API_URL = 'http://localhost:5000';

document.addEventListener('DOMContentLoaded', () => {
    // Check if user is already logged in
    if (isLoggedIn()) {
        window.location.href = 'index.html';
        return;
    }

    // Initialize form validation
    const form = document.getElementById('loginForm');
    form.addEventListener('submit', handleLogin);
    initializePasswordToggles();
});

async function handleLogin(event) {
    event.preventDefault();

    const form = event.target;
    clearInlineError('login-inline-error');

    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        setInlineError('login-inline-error', 'Preencha usuário e senha para continuar.');
        return;
    }

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
        showLoading();
        setFormSubmitting('login-submit-btn', true, 'Entrando...');
        
        const requestData = { username, password };
        
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Erro ao fazer login');
        }

        if (data.success) {
            // Store token and user data
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));

            // Redirect to main page
            window.location.href = 'index.html';
        } else {
            throw new Error(data.message || 'Credenciais inválidas');
        }
    } catch (error) {
        setInlineError('login-inline-error', error.message || 'Erro ao fazer login.');
    } finally {
        hideLoading();
        setFormSubmitting('login-submit-btn', false);
    }
}

function isLoggedIn() {
    const token = localStorage.getItem('token');
    return !!token;
}

function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.remove('hide');
        overlay.classList.add('show');
    }
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.remove('show');
        overlay.classList.add('hide');
    }
}

function setInlineError(elementId, message) {
    const errorElement = document.getElementById(elementId);
    if (errorElement) {
        errorElement.textContent = message;
    }
}

function clearInlineError(elementId) {
    const errorElement = document.getElementById(elementId);
    if (errorElement) {
        errorElement.textContent = '';
    }
}

function setFormSubmitting(buttonId, isSubmitting, loadingText = '') {
    const submitButton = document.getElementById(buttonId);
    if (!submitButton) {
        return;
    }

    submitButton.disabled = isSubmitting;
    submitButton.classList.toggle('is-submitting', isSubmitting);
}

function initializePasswordToggles() {
    const toggleButtons = document.querySelectorAll('.password-toggle-btn');
    toggleButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const targetId = button.getAttribute('data-target');
            const targetInput = document.getElementById(targetId);
            const icon = button.querySelector('i');

            if (!targetInput || !icon) {
                return;
            }

            const isPassword = targetInput.type === 'password';
            targetInput.type = isPassword ? 'text' : 'password';
            icon.className = isPassword ? 'bi bi-eye-slash' : 'bi bi-eye';
            button.setAttribute('aria-label', isPassword ? 'Ocultar senha' : 'Mostrar senha');
        });
    });
}