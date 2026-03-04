// API Base URL
const API_URL = 'http://127.0.0.1:8000/api';

// Проверка авторизации при загрузке
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('access_token');
    const currentPage = window.location.pathname;

    console.log('Page loaded:', currentPage);
    console.log('Token exists:', !!token);

    if (!token && !currentPage.includes('login') && !currentPage.includes('register')) {
        window.location.href = '/login/';
    }

    // Инициализация форм
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
        console.log('Login form initialized');
    }

    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
        console.log('Register form initialized');
    }

    // Загрузка данных если на главной странице
    if (token && currentPage.includes('dashboard')) {
        loadDepartments();
        loadEmployees();
    }
});

// Авторизация
async function handleLogin(e) {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    console.log('Login attempt:', username);

    try {
        const response = await fetch(`${API_URL}/token/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        console.log('Response status:', response.status);

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            console.log('Login successful, redirecting...');
            window.location.href = '/dashboard/';
        } else {
            const errorData = await response.json();
            alert('Ошибка: ' + JSON.stringify(errorData));
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('Ошибка подключения к серверу');
    }
}

// Регистрация
async function handleRegister(e) {
    e.preventDefault();

    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const password_confirm = document.getElementById('reg-password-confirm').value;

    console.log('Register attempt:', username, email);

    try {
        const response = await fetch(`${API_URL}/register/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password, password_confirm })
        });

        console.log('Response status:', response.status);

        if (response.ok) {
            alert('Регистрация успешна! Теперь войдите.');
            window.location.href = '/login/';
        } else {
            const data = await response.json();
            alert('Ошибка: ' + JSON.stringify(data));
        }
    } catch (error) {
        console.error('Register error:', error);
        alert('Ошибка подключения к серверу');
    }
}

// Выход
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login/';
}

// Показать секцию
function showSection(sectionName) {
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });
    document.getElementById(sectionName).style.display = 'block';
}

// Загрузка отделов
async function loadDepartments() {
    try {
        const response = await fetch(`${API_URL}/departments/`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });
        const data = await response.json();

        const container = document.getElementById('departments-list');
        if (data.results && data.results.length > 0) {
            container.innerHTML = data.results.map(dept => `
                <div class="card">
                    <h3>${dept.name}</h3>
                    <p><strong>Код:</strong> ${dept.code}</p>
                    <p><strong>Кабинет:</strong> ${dept.office_number}</p>
                    <p><strong>Сотрудников:</strong> ${dept.employees_count}</p>
                    <div class="card-actions">
                        <button class="btn-edit" onclick="editDepartment(${dept.id})">Изменить</button>
                        <button class="btn-delete" onclick="deleteDepartment(${dept.id})">Удалить</button>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p>Нет отделов. Добавьте первый отдел!</p>';
        }
    } catch (error) {
        console.error('Error loading departments:', error);
        document.getElementById('departments-list').innerHTML = '<p>Ошибка загрузки</p>';
    }
}

// Загрузка сотрудников
async function loadEmployees() {
    try {
        const response = await fetch(`${API_URL}/employees/`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });
        const data = await response.json();

        const container = document.getElementById('employees-list');
        if (data.results && data.results.length > 0) {
            container.innerHTML = data.results.map(emp => `
                <div class="card">
                    <h3>${emp.full_name}</h3>
                    <p><strong>Email:</strong> ${emp.email}</p>
                    <p><strong>Телефон:</strong> ${emp.phone}</p>
                    <p><strong>Должность:</strong> ${emp.position_display}</p>
                    <p><strong>Отдел:</strong> ${emp.department_name}</p>
                    <div class="card-actions">
                        <button class="btn-edit" onclick="editEmployee(${emp.id})">Изменить</button>
                        <button class="btn-delete" onclick="deleteEmployee(${emp.id})">Удалить</button>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p>Нет сотрудников. Добавьте первого сотрудника!</p>';
        }
    } catch (error) {
        console.error('Error loading employees:', error);
        document.getElementById('employees-list').innerHTML = '<p>Ошибка загрузки</p>';
    }
}

// Открыть модальное окно
function openModal(type) {
    const modal = document.getElementById('modal');
    const title = document.getElementById('modal-title');
    const form = document.getElementById('modal-form');

    modal.style.display = 'block';

    if (type === 'department') {
        title.textContent = 'Добавить отдел';
        form.innerHTML = `
            <div class="form-group">
                <label>Название</label>
                <input type="text" id="dept-name" required>
            </div>
            <div class="form-group">
                <label>Код</label>
                <input type="text" id="dept-code" required>
            </div>
            <div class="form-group">
                <label>Номер кабинета</label>
                <input type="text" id="dept-office" required>
            </div>
            <button type="button" class="btn-primary" onclick="createDepartment()">Создать</button>
        `;
    } else if (type === 'employee') {
        title.textContent = 'Добавить сотрудника';
        form.innerHTML = `
            <div class="form-group">
                <label>ФИО</label>
                <input type="text" id="emp-name" required>
            </div>
            <div class="form-group">
                <label>Email</label>
                <input type="email" id="emp-email" required>
            </div>
            <div class="form-group">
                <label>Телефон</label>
                <input type="text" id="emp-phone" required>
            </div>
            <div class="form-group">
                <label>Должность</label>
                <select id="emp-position" required>
                    <option value="junior">Junior</option>
                    <option value="middle">Middle</option>
                    <option value="senior">Senior</option>
                    <option value="lead">Team Lead</option>
                    <option value="manager">Manager</option>
                </select>
            </div>
            <div class="form-group">
                <label>Отдел (ID)</label>
                <input type="number" id="emp-department" required>
            </div>
            <div class="form-group">
                <label>Дата приема</label>
                <input type="date" id="emp-hire-date" required>
            </div>
            <button type="button" class="btn-primary" onclick="createEmployee()">Создать</button>
        `;
    }
}

// Закрыть модальное окно
function closeModal() {
    document.getElementById('modal').style.display = 'none';
}

// Создание отдела
async function createDepartment() {
    const data = {
        name: document.getElementById('dept-name').value,
        code: document.getElementById('dept-code').value,
        office_number: document.getElementById('dept-office').value
    };

    try {
        const response = await fetch(`${API_URL}/departments/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            closeModal();
            loadDepartments();
        } else {
            const errorData = await response.json();
            alert('Ошибка: ' + JSON.stringify(errorData));
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Создание сотрудника
async function createEmployee() {
    const data = {
        full_name: document.getElementById('emp-name').value,
        email: document.getElementById('emp-email').value,
        phone: document.getElementById('emp-phone').value,
        position: document.getElementById('emp-position').value,
        department: parseInt(document.getElementById('emp-department').value),
        hire_date: document.getElementById('emp-hire-date').value
    };

    try {
        const response = await fetch(`${API_URL}/employees/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            closeModal();
            loadEmployees();
        } else {
            const errorData = await response.json();
            alert('Ошибка: ' + JSON.stringify(errorData));
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Удаление отдела
async function deleteDepartment(id) {
    if (!confirm('Удалить отдел?')) return;

    try {
        const response = await fetch(`${API_URL}/departments/${id}/`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });

        if (response.ok) {
            loadDepartments();
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Удаление сотрудника
async function deleteEmployee(id) {
    if (!confirm('Удалить сотрудника?')) return;

    try {
        const response = await fetch(`${API_URL}/employees/${id}/`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });

        if (response.ok) {
            loadEmployees();
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Закрытие модального окна при клике вне его
window.onclick = function(event) {
    const modal = document.getElementById('modal');
    if (event.target == modal) {
        closeModal();
    }
}