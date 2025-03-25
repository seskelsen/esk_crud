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
});

async function handleLogin(event) {
    event.preventDefault();
    
    const form = event.target;
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return;
    }

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        showLoading();
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
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
        showErrorMessage(error.message || 'Erro ao fazer login');
    } finally {
        hideLoading();
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

function showErrorMessage(message) {
    Swal.fire({
        icon: 'error',
        title: 'Erro',
        text: message,
        confirmButtonColor: '#0d6efd'
    });
}