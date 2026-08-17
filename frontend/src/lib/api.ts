import axios from 'axios';
import { useAuthStore } from '@/store/auth-store';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

api.interceptors.request.use(
    (config) => {
        const tokens = useAuthStore.getState().tokens;
        if (tokens?.access) {
            config.headers.Authorization = `Bearer ${tokens.access}`;
        }
        return config;
    },
    (error) => Promise.reject(error),
);

api.interceptors.response.use(
    (response) => {
        if (response.data && response.data.data !== undefined) {
            response.data = response.data.data;
        }
        return response;
    },
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            const tokens = useAuthStore.getState().tokens;

            if (tokens?.refresh) {
                try {
                    const response = await axios.post(`${API_URL}/accounts/auth/refresh/`, {
                        refresh: tokens.refresh,
                    });

                    const newTokens = response.data.data || response.data;
                    useAuthStore.getState().setTokens(newTokens);

                    originalRequest.headers.Authorization = `Bearer ${newTokens.access}`;
                    return api(originalRequest);
                } catch (refreshError) {
                    useAuthStore.getState().clearAuth();
                    window.location.replace('/login');
                    return Promise.reject(refreshError);
                }
            } else {
                useAuthStore.getState().clearAuth();
                window.location.replace('/login');
            }
        }

        if (error.response?.data?.error?.message) {
            error.message = error.response.data.error.message;
        }

        return Promise.reject(error);
    },
);
