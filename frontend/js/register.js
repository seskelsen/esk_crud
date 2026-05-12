const API_URL = 'http://localhost:5000';

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('registerForm');
    form.addEventListener('submit', handleRegister);
    initializePasswordToggles();
});

async function handleRegister(event) {
    event.preventDefault();

    const form = event.target;
    clearInlineError('register-inline-error');

    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        setInlineError('register-inline-error', 'Preencha os campos obrigatórios.');
        return;
    }

    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    if (password !== confirmPassword) {
        setInlineError('register-inline-error', 'As senhas não coincidem.');
        return;
    }

    try {
        showLoading();
        setFormSubmitting('register-submit-btn', true, 'Registrando...');
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ username, email, password })
        });
        const data = await response.json();
        if (!response.ok || !data.success) {
            throw new Error(data.message || 'Erro no registro');
        }
        Swal.fire({
            icon: 'success',
            title: 'Registrado com sucesso',
            text: 'Agora você pode fazer login.',
            confirmButtonColor: '#0d6efd'
        }).then(() => window.location.href = 'login.html');
    } catch (err) {
        setInlineError('register-inline-error', err.message || 'Erro no registro.');
    } finally {
        hideLoading();
        setFormSubmitting('register-submit-btn', false);
    }
}

function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.remove('hide');
    overlay.classList.add('show');
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.remove('show');
    overlay.classList.add('hide');
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
