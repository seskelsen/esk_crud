const API_URL = 'http://localhost:5000';

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('registerForm');
    form.addEventListener('submit', handleRegister);
});

async function handleRegister(event) {
    event.preventDefault();

    const form = event.target;
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return;
    }

    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        showLoading();
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
        Swal.fire({
            icon: 'error',
            title: 'Erro',
            text: err.message || 'Erro no registro',
            confirmButtonColor: '#0d6efd'
        });
    } finally {
        hideLoading();
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
