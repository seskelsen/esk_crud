const API_URL = 'http://localhost:5000';
let userModal;
let currentUser = null;

// Page initialization
document.addEventListener('DOMContentLoaded', () => {
    // Check authentication
    if (!isLoggedIn()) {
        window.location.href = 'login.html';
        return;
    }
    const user = JSON.parse(localStorage.getItem('user'));
    // Only admins can access this page
    if (user.role !== 'admin') {
        window.location.href = 'index.html';
        return;
    }
    setupUI();
    userModal = new bootstrap.Modal(document.getElementById('userModal'));
    initializeFormValidation();
    loadUsers();
});

function isLoggedIn() {
    return !!localStorage.getItem('token');
}

function setupUI() {
    const stored = JSON.parse(localStorage.getItem('user'));
    const navbarNav = document.getElementById('navbarNav');
    const userMenu = document.createElement('ul');
    userMenu.className = 'navbar-nav ms-auto';
    userMenu.innerHTML = `
        <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                <i class="bi bi-person-circle me-1"></i>${stored.username}
            </a>
            <ul class="dropdown-menu dropdown-menu-end">
                <li><a class="dropdown-item" href="#" onclick="logout()">
                    <i class="bi bi-box-arrow-right me-2"></i>Sair
                </a></li>
            </ul>
        </li>
    `;
    navbarNav.appendChild(userMenu);
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = 'login.html';
}

function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    overlay && overlay.classList.remove('hide');
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    overlay && overlay.classList.add('hide');
}

function initializeFormValidation() {
    const form = document.getElementById('userForm');
    form.addEventListener('submit', event => {
        if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
        }
        form.classList.add('was-validated');
    }, false);
}

async function loadUsers() {
    try {
        showLoading();
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_URL}/users`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error(`Status ${response.status}`);
        const result = await response.json();
        if (result.success) {
            renderUsers(Object.values(result.data));
        } else {
            throw new Error(result.message);
        }
    } catch (err) {
        console.error('Erro ao carregar usuários:', err);
        Swal.fire({ icon: 'error', title: 'Erro', text: err.message });
    } finally {
        hideLoading();
    }
}

function renderUsers(list) {
    const tbody = document.getElementById('usersList');
    tbody.innerHTML = '';
    if (!list.length) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center py-4 text-muted">Nenhum usuário encontrado</td></tr>`;
        return;
    }
    list.forEach(u => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="ps-3">${u.username}</td>
            <td>${u.email}</td>
            <td>${u.role}</td>
            <td class="text-center">${u.active ? 'Sim' : 'Não'}</td>
            <td class="text-end pe-3">
                <button class="btn btn-sm btn-outline-primary me-1" onclick='openModal(${JSON.stringify(u).replace(/"/g, '&quot;')})'>
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteUser('${u.id}')">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function openModal(user = null) {
    currentUser = user;
    const form = document.getElementById('userForm');
    form.reset();
    form.classList.remove('was-validated');
    document.getElementById('userId').value = user ? user.id : '';
    document.getElementById('username').value = user ? user.username : '';
    document.getElementById('email').value = user ? user.email : '';
    document.getElementById('role').value = user ? user.role : 'user';
    document.getElementById('active').checked = user ? user.active : true;
    // Show password only for new user
    const pwdGroup = document.getElementById('passwordGroup');
    pwdGroup.style.display = user ? 'none' : 'block';
    document.getElementById('modalUserTitle').textContent = user ? 'Editar Usuário' : 'Novo Usuário';
    userModal.show();
}

async function saveUser() {
    const form = document.getElementById('userForm');
    if (!form.checkValidity()) { form.classList.add('was-validated'); return; }
    const id = document.getElementById('userId').value;
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const role = document.getElementById('role').value;
    const active = document.getElementById('active').checked;
    const password = document.getElementById('password')?.value;
    try {
        showLoading();
        const token = localStorage.getItem('token');
        let response;
        if (id) {
            // Update existing user
            const data = { username, email, role, active };
            if (password) data.password = password;
            response = await fetch(`${API_URL}/users/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify(data)
            });
        } else {
            // Create new user via register endpoint
            const data = { username, email, password };
            response = await fetch(`${API_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (response.ok) {
                const result = await response.json();
                // After creating, update role and active
                const newId = result.user.id;
                await fetch(`${API_URL}/users/${newId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                    body: JSON.stringify({ role, active })
                });
            }
        }
        const result = await response.json();
        if (!response.ok) throw new Error(result.message || 'Erro');
        Swal.fire({ icon: 'success', title: 'Sucesso', text: 'Operação realizada com sucesso', timer: 1500, showConfirmButton: false });
        userModal.hide();
        loadUsers();
    } catch (err) {
        console.error('Erro ao salvar usuário:', err);
        Swal.fire({ icon: 'error', title: 'Erro', text: err.message });
    } finally {
        hideLoading();
    }
}

async function deleteUser(id) {
    const confirmed = await Swal.fire({ title: 'Excluir usuário?', text: 'Essa ação não pode ser desfeita.', icon: 'warning', showCancelButton: true, confirmButtonText: 'Sim, excluir' });
    if (!confirmed.isConfirmed) return;
    try {
        showLoading();
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_URL}/users/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.message);
        Swal.fire({ icon: 'success', title: 'Sucesso', text: 'Usuário excluído', timer: 1500, showConfirmButton: false });
        loadUsers();
    } catch (err) {
        console.error('Erro ao excluir usuário:', err);
        Swal.fire({ icon: 'error', title: 'Erro', text: err.message });
    } finally {
        hideLoading();
    }
}

// Global error handlers
window.addEventListener('unhandledrejection', () => hideLoading());
window.addEventListener('error', () => hideLoading());
