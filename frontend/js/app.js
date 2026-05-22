function showAlert(message, type = 'success') {
    const alertContainer = document.getElementById('alertContainer') || document.body;
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alert.style.zIndex = '9999';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alert);
    setTimeout(() => alert.remove(), 4000);
}

function showLoading(show = true) {
    const loader = document.getElementById('loadingSpinner');
    if (loader) loader.style.display = show ? 'flex' : 'none';
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function formatDateTime(dateStr) {
    if (!dateStr) return '-';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
}

function statusBadge(status, type = 'status') {
    const map = {
        'Pending': 'badge-status-pending',
        'Approved': 'badge-status-approved',
        'Rejected': 'badge-status-rejected',
        'Active': 'badge-status-active',
        'Inactive': 'badge-status-inactive',
        'Planned': 'badge-status-planned',
        'Completed': 'badge-status-completed',
        'On Hold': 'badge-status-onhold',
        'In Progress': 'badge-status-inprogress',
        'Blocked': 'badge-status-blocked',
    };
    const cls = map[status] || 'bg-secondary';
    return `<span class="badge ${cls}">${status}</span>`;
}

function priorityBadge(priority) {
    const map = {
        'Low': 'badge bg-info text-white',
        'Medium': 'badge bg-warning text-white',
        'High': 'badge bg-danger text-white',
    };
    const cls = map[priority] || 'bg-secondary';
    return `<span class="${cls}">${priority}</span>`;
}

function populateSelect(selectId, data, valueKey = 'value', labelKey = 'label', placeholder = 'Select...') {
    const select = document.getElementById(selectId);
    if (!select) return;
    select.innerHTML = `<option value="">${placeholder}</option>`;
    data.forEach(item => {
        const option = document.createElement('option');
        option.value = item[valueKey];
        option.textContent = item[labelKey];
        select.appendChild(option);
    });
}

function getQueryParam(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

function logout() {
    api.logout();
}

function initSidebar() {
    const currentPage = window.location.pathname.split('/').pop();
    document.querySelectorAll('.nav-link').forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPage) {
            link.classList.add('active');
        }
    });

    const toggleBtn = document.getElementById('sidebarToggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            document.querySelector('.sidebar').classList.toggle('show');
        });
    }
}

function initUserProfile() {
    const user = api.getUser();
    const avatarEl = document.getElementById('userAvatar');
    const nameEl = document.getElementById('userName');
    const roleEl = document.getElementById('userRole');

    if (avatarEl && user.full_name) {
        avatarEl.textContent = user.full_name.charAt(0).toUpperCase();
    }
    if (nameEl) nameEl.textContent = user.full_name || '';
    if (roleEl) roleEl.textContent = user.role || '';
}

async function loadNotifications() {
    const notifContainer = document.getElementById('notificationList');
    const notifBadge = document.getElementById('notificationBadge');
    if (!notifContainer) return;

    try {
        const countData = await api.get('/notifications/unread-count');
        if (notifBadge) {
            notifBadge.textContent = countData.count;
            notifBadge.style.display = countData.count > 0 ? 'inline' : 'none';
        }

        const result = await api.get('/notifications');
        const notifications = result.data || [];

        notifContainer.innerHTML = notifications.length === 0
            ? '<div class="text-center p-3 text-muted small">No notifications</div>'
            : notifications.slice(0, 10).map(n => `
                <div class="notification-item ${n.is_read ? '' : 'unread'}" 
                     onclick="markNotifRead(${n.notification_id})">
                    <div class="notif-title">${n.title}</div>
                    <p class="notif-message">${n.message}</p>
                    <small class="notif-time">${formatDateTime(n.created_at)}</small>
                </div>
            `).join('') +
            (notifications.length > 10
                ? '<div class="text-center p-2"><a href="notifications.html" class="small">View all</a></div>'
                : '');

    } catch (error) {
        console.error('Failed to load notifications:', error);
    }
}

async function markNotifRead(id) {
    try {
        await api.put(`/notifications/${id}/read`);
        loadNotifications();
    } catch (error) {
        console.error('Failed to mark notification as read:', error);
    }
}

async function markAllNotifRead() {
    try {
        await api.put('/notifications/read-all');
        loadNotifications();
    } catch (error) {
        console.error('Failed to mark all as read:', error);
    }
}

function redirectBasedOnRole() {
    const user = api.getUser();
    const role = user.role || '';

    if (role === 'Admin') window.location.href = 'pages/dashboard.html';
    else if (role === 'Manager') window.location.href = 'pages/dashboard.html';
    else if (role === 'Employee') window.location.href = 'pages/dashboard.html';
}

function openModal(modalId) {
    const modal = new bootstrap.Modal(document.getElementById(modalId));
    modal.show();
}

function closeModal(modalId) {
    const modalEl = document.getElementById(modalId);
    const modal = bootstrap.Modal.getInstance(modalEl);
    if (modal) modal.hide();
}

document.addEventListener('DOMContentLoaded', function () {
    initSidebar();
    initUserProfile();
    loadNotifications();

    if (api.isAuthenticated()) {
        setInterval(loadNotifications, 30000);
    }
});
