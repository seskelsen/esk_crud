const API_URL = 'http://localhost:5000';
let modal;
let currentSupplier = null;
let suppliers = {};
let currentSearchTerm = '';
let currentSortField = 'name';

document.addEventListener('DOMContentLoaded', () => {
    // Check if user is logged in
    if (!isLoggedIn()) {
        window.location.href = 'login.html';
        return;
    }

    setupUI();
    modal = new bootstrap.Modal(document.getElementById('supplierModal'));
    
    // Inicializar componentes
    initializeComponents();
    
    // Carregar dados
    loadSuppliers();
});

function setupUI() {
    // Setup user info in navbar
    const user = JSON.parse(localStorage.getItem('user'));
    const navbarNav = document.getElementById('navbarNav');
    
    // Add user menu to navbar
    const userMenu = document.createElement('ul');
    userMenu.className = 'navbar-nav ms-auto';
    userMenu.innerHTML = `
        <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                <i class="bi bi-person-circle me-1"></i>${user.username}
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

function isLoggedIn() {
    const token = localStorage.getItem('token');
    return !!token;
}

function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.remove('hide');
        overlay.classList.add('show');
        document.body.style.overflow = 'hidden'; // Previne rolagem
    }
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.remove('show');
        overlay.classList.add('hide');
        document.body.style.overflow = ''; // Restaura rolagem
    }
}

function initializeComponents() {
    // Inicializar validação de formulários
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Adiciona formatação automática do CNPJ
    const cnpjInput = document.getElementById('cnpj');
    cnpjInput.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length <= 14) {
            e.target.value = formatCNPJ(value);
        } else {
            e.target.value = formatCNPJ(value.substr(0, 14));
        }
    });

    // Adiciona formatação automática do telefone
    const phoneInput = document.getElementById('phone');
    phoneInput.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length <= 11) {
            e.target.value = formatPhone(value);
        } else {
            e.target.value = formatPhone(value.substr(0, 11));
        }
    });
    
    // Adicionar funcionalidade de busca
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', debounce((e) => {
        currentSearchTerm = e.target.value.toLowerCase();
        filterAndSortSuppliers();
    }, 300));
    
    // Adicionar funcionalidade de ordenação
    const sortSelect = document.getElementById('sortSelect');
    sortSelect.addEventListener('change', () => {
        currentSortField = sortSelect.value;
        filterAndSortSuppliers();
        
        // Adicionando log para debug
        console.log('Ordenando por:', currentSortField);
    });
}

// Função central para filtrar e ordenar fornecedores
function filterAndSortSuppliers() {
    if (!suppliers) {
        console.error("Fornecedores não definidos");
        renderSuppliers([]);
        return;
    }
    
    // Converter o objeto suppliers em array, independentemente de sua estrutura
    let filteredSuppliers = [];
    try {
        if (Array.isArray(suppliers)) {
            filteredSuppliers = [...suppliers];
        } else if (typeof suppliers === 'object') {
            filteredSuppliers = Object.values(suppliers);
        }
    } catch (error) {
        console.error("Erro ao processar fornecedores:", error);
        renderSuppliers([]);
        return;
    }
    
    // Aplicar filtro se houver um termo de busca
    if (currentSearchTerm) {
        filteredSuppliers = filteredSuppliers.filter(supplier => {
            if (!supplier) return false;
            
            const nameMatch = supplier.name && supplier.name.toLowerCase().includes(currentSearchTerm);
            const cnpjMatch = supplier.cnpj && supplier.cnpj.includes(currentSearchTerm);
            const emailMatch = supplier.email && supplier.email.toLowerCase().includes(currentSearchTerm);
            const phoneMatch = supplier.phone && supplier.phone.includes(currentSearchTerm);
            
            return nameMatch || cnpjMatch || emailMatch || phoneMatch;
        });
    }
    
    // Ordenar a lista
    try {
        filteredSuppliers.sort((a, b) => {
            if (!a || !b) return 0;
            
            let valueA = a[currentSortField];
            let valueB = b[currentSortField];
            
            if (valueA === undefined || valueA === null) return 1;
            if (valueB === undefined || valueB === null) return -1;
            
            if (typeof valueA === 'string' && typeof valueB === 'string') {
                return valueA.toLowerCase().localeCompare(valueB.toLowerCase(), 'pt-BR');
            }
            
            return valueA < valueB ? -1 : valueA > valueB ? 1 : 0;
        });
    } catch (error) {
        console.error("Erro ao ordenar fornecedores:", error);
    }
    
    renderSuppliers(filteredSuppliers);
}

function filterSuppliers(searchTerm) {
    currentSearchTerm = searchTerm;
    filterAndSortSuppliers();
}

function sortSuppliers(sortBy) {
    currentSortField = sortBy;
    filterAndSortSuppliers();
}

// Função auxiliar para debounce (evita múltiplas execuções)
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatCNPJ(cnpj) {
    // Remove caracteres não numéricos
    cnpj = cnpj.replace(/\D/g, '');
    
    // Aplica a máscara
    return cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5');
}

function formatPhone(phone) {
    // Remove caracteres não numéricos
    phone = phone.replace(/\D/g, '');
    
    // Aplica a máscara dependendo se é celular (11 dígitos) ou fixo (10 dígitos)
    if (phone.length === 11) {
        return phone.replace(/^(\d{2})(\d{5})(\d{4})$/, '($1) $2-$3');
    } else if (phone.length === 10) {
        return phone.replace(/^(\d{2})(\d{4})(\d{4})$/, '($1) $2-$3');
    }
    return phone;
}

function openModal(supplier = null) {
    currentSupplier = supplier;
    const form = document.getElementById('supplierForm');
    form.reset();
    form.classList.remove('was-validated');
    
    if (supplier) {
        document.getElementById('modalTitle').textContent = 'Editar Fornecedor';
        document.getElementById('supplierId').value = supplier.id;
        document.getElementById('name').value = supplier.name;
        document.getElementById('cnpj').value = formatCNPJ(supplier.cnpj);
        document.getElementById('email').value = supplier.email;
        document.getElementById('phone').value = formatPhone(supplier.phone);
    } else {
        document.getElementById('modalTitle').textContent = 'Novo Fornecedor';
        document.getElementById('supplierId').value = '';
    }
    
    modal.show();
}

async function loadSuppliers() {
    try {
        showLoading();
        const response = await fetch(`${API_URL}/suppliers`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (response.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = 'login.html';
            return;
        }

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        
        if (result.success) {
            suppliers = result.data || {};
            console.log('Dados recebidos da API:', suppliers);
            
            // Converter para array se necessário
            const suppliersList = Object.values(suppliers);
            console.log('Total de fornecedores:', suppliersList.length);
            
            // Atualizar contagem e renderizar
            updateTotalCount(suppliersList.length);
            renderSuppliers(suppliersList);
        } else {
            throw new Error(result.message || 'Erro ao carregar dados');
        }
    } catch (error) {
        console.error('Erro ao carregar:', error);
        showErrorMessage('Erro ao carregar fornecedores');
        updateTotalCount(0);
        renderSuppliers([]);
    } finally {
        hideLoading();
    }
}

function renderSuppliers(suppliersList = []) {
    const tbody = document.getElementById('suppliersList');
    tbody.innerHTML = '';
    
    // Garantir que suppliersList seja um array válido
    const safeList = Array.isArray(suppliersList) ? suppliersList : [];
    
    // Atualizar contagem total primeiro
    updateTotalCount(safeList.length);
    
    if (safeList.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center py-4">
                    <div class="text-muted">
                        <i class="bi bi-inbox fs-4 d-block mb-2"></i>
                        Nenhum fornecedor encontrado
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    suppliersList.forEach(supplier => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="ps-3">
                <div class="fw-medium">${supplier.name}</div>
            </td>
            <td>${formatCNPJ(supplier.cnpj)}</td>
            <td>
                <a href="mailto:${supplier.email}" class="text-decoration-none">
                    ${supplier.email}
                </a>
            </td>
            <td class="text-decoration-none">
                ${formatPhone(supplier.phone)}
            </td>
            <td class="text-end pe-3">
                <button class="btn btn-sm btn-outline-primary me-1" onclick="openModal(${JSON.stringify(supplier).replace(/"/g, '&quot;')})">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteSupplier('${supplier.id}')">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function updateTotalCount(count = 0) {
    const totalElement = document.getElementById('totalSuppliers');
    if (!totalElement) return;

    // Garantir que count seja um número não-negativo
    const totalCount = Math.max(0, parseInt(count) || 0);
    
    const mensagem = totalCount === 0 ? 'Nenhum fornecedor' :
                    totalCount === 1 ? '1 fornecedor' :
                    `${totalCount} fornecedores`;
    
    totalElement.textContent = mensagem;
}

async function saveSupplier() {
    const form = document.getElementById('supplierForm');
    
    // Validar formulário
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return;
    }
    
    const id = document.getElementById('supplierId').value;
    const nameValue = document.getElementById('name').value.trim();
    const cnpjValue = document.getElementById('cnpj').value;
    const emailValue = document.getElementById('email').value.trim();
    const phoneValue = document.getElementById('phone').value;
    
    try {
        showLoading();
        
        // Validações adicionais
        if (cnpjValue.replace(/\D/g, '').length !== 14) {
            throw new Error('CNPJ deve ter 14 dígitos');
        }
        
        if (!emailValue.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
            throw new Error('Email inválido');
        }
        
        const phoneDigits = phoneValue.replace(/\D/g, '');
        if (phoneDigits.length < 10 || phoneDigits.length > 11) {
            throw new Error('Telefone deve ter 10 ou 11 dígitos');
        }
        
        const data = {
            name: nameValue,
            cnpj: cnpjValue.replace(/\D/g, ''),
            email: emailValue,
            phone: phoneDigits
        };

        const url = id ? `${API_URL}/suppliers/${id}` : `${API_URL}/suppliers`;
        const method = id ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify(data)
        });

        if (response.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = 'login.html';
            return;
        }
        
        const responseData = await response.json();
        
        if (!response.ok) {
            throw new Error(responseData.message || `Erro ${response.status} ao salvar fornecedor`);
        }
        
        if (!responseData.success) {
            throw new Error(responseData.message || 'Erro ao salvar fornecedor');
        }
        
        showSuccessMessage(id ? 'Fornecedor atualizado com sucesso!' : 'Fornecedor criado com sucesso!');
        modal.hide();
        await loadSuppliers();
        
    } catch (error) {
        console.error('Erro ao salvar:', error);
        showErrorMessage(error.message || 'Ocorreu um erro ao salvar');
    } finally {
        hideLoading();
    }
}

async function deleteSupplier(id) {
    try {
        const result = await Swal.fire({
            title: 'Confirmar exclusão',
            text: 'Deseja realmente excluir este fornecedor?',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Sim, excluir',
            cancelButtonText: 'Cancelar',
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            focusCancel: true
        });

        if (result.isConfirmed) {
            showLoading();
            try {
                const response = await fetch(`${API_URL}/suppliers/${id}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });

                if (response.status === 401) {
                    // Token expired or invalid
                    localStorage.removeItem('token');
                    localStorage.removeItem('user');
                    window.location.href = 'login.html';
                    return;
                }

                // Para status 204 não tem corpo JSON
                if (response.status === 204) {
                    showSuccessMessage('Fornecedor excluído com sucesso!');
                    await loadSuppliers();
                    return;
                }

                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.message || `HTTP error! status: ${response.status}`);
                }

                if (data.success) {
                    showSuccessMessage('Fornecedor excluído com sucesso!');
                    await loadSuppliers();
                } else {
                    throw new Error(data.message || 'Erro ao excluir fornecedor');
                }
            } finally {
                hideLoading();
            }
        }
    } catch (error) {
        console.error('Erro ao excluir:', error);
        showErrorMessage(error.message || 'Ocorreu um erro ao excluir');
        hideLoading();
    }
}

function showSuccessMessage(message) {
    Swal.fire({
        icon: 'success',
        title: 'Sucesso',
        text: message,
        timer: 2000,
        showConfirmButton: false
    });
}

function showErrorMessage(message) {
    Swal.fire({
        icon: 'error',
        title: 'Erro',
        text: message,
        confirmButtonColor: '#0d6efd'
    });
}

window.addEventListener('unhandledrejection', function(event) {
    // Garantir que o loading seja removido mesmo em caso de erros não tratados
    hideLoading();
});

window.addEventListener('error', function(event) {
    // Garantir que o loading seja removido mesmo em caso de erros não tratados
    hideLoading();
});