const API_BASE = 'http://localhost:5000/api';

const api = {
    getToken: () => localStorage.getItem('token'),
    getUser: () => JSON.parse(localStorage.getItem('user') || '{}'),

    setAuth: (token, user) => {
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));
    },

    clearAuth: () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    },

    isAuthenticated: () => !!localStorage.getItem('token'),

    getHeaders: () => {
        const headers = { 'Content-Type': 'application/json' };
        const token = api.getToken();
        if (token) headers['Authorization'] = `Bearer ${token}`;
        return headers;
    },

    getFormHeaders: () => {
        const headers = {};
        const token = api.getToken();
        if (token) headers['Authorization'] = `Bearer ${token}`;
        return headers;
    },

    request: async (endpoint, options = {}) => {
        const url = `${API_BASE}${endpoint}`;
        const config = {
            ...options,
            headers: { ...api.getHeaders(), ...options.headers },
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                if (response.status === 401) {
                    api.clearAuth();
                    window.location.href = '../index.html';
                }
                throw { status: response.status, ...data };
            }

            return data;
        } catch (error) {
            if (error.status) throw error;
            throw { message: 'Network error. Please check your connection.' };
        }
    },

    get: (endpoint) => api.request(endpoint),
    post: (endpoint, data) => api.request(endpoint, { method: 'POST', body: JSON.stringify(data) }),
    put: (endpoint, data) => api.request(endpoint, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (endpoint) => api.request(endpoint, { method: 'DELETE' }),

    upload: async (endpoint, formData) => {
        const url = `${API_BASE}${endpoint}`;
        const headers = {};
        const token = api.getToken();
        if (token) headers['Authorization'] = `Bearer ${token}`;

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers,
                body: formData,
            });
            const data = await response.json();
            if (!response.ok) throw { status: response.status, ...data };
            return data;
        } catch (error) {
            if (error.status) throw error;
            throw { message: 'Upload failed. Please try again.' };
        }
    },

    login: async (email, password) => {
        const data = await api.post('/login', { email, password });
        if (data.success) {
            api.setAuth(data.token, data.user);
        }
        return data;
    },

    logout: () => {
        api.clearAuth();
        window.location.href = '../index.html';
    },
};
