import axios, { type InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '@/store/auth-store';
import { authPaths } from '@/app/paths';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

let isRefreshing = false;
let failedQueue: Array<{
    resolve: (token: string) => void;
    reject: (error: unknown) => void;
}> = [];

const processQueue = (error: unknown, token: string | null = null) => {
    failedQueue.forEach((prom) => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token as string);
        }
    });
    failedQueue = [];
};

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

interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
    _retry?: boolean;
}

api.interceptors.response.use(
    (response) => {
        if (response.data && response.data.data !== undefined) {
            response.data = response.data.data;
        }
        return response;
    },
    async (error) => {
        const originalRequest = error.config as CustomAxiosRequestConfig;

        if (error.response?.status === 401 && !originalRequest._retry) {
            if (isRefreshing) {
                return new Promise(function (resolve, reject) {
                    failedQueue.push({ resolve, reject });
                })
                    .then((token) => {
                        originalRequest.headers.Authorization = `Bearer ${token}`;
                        return api(originalRequest);
                    })
                    .catch((err) => {
                        return Promise.reject(err);
                    });
            }

            originalRequest._retry = true;
            isRefreshing = true;

            const tokens = useAuthStore.getState().tokens;

            if (tokens?.refresh) {
                try {
                    const response = await axios.post(`${API_URL}/accounts/auth/refresh/`, {
                        refresh: tokens.refresh,
                    });

                    const newTokens = response.data.data || response.data;

                    useAuthStore.getState().setTokens({
                        access: newTokens.access,
                        refresh: newTokens.refresh || tokens.refresh,
                    });

                    processQueue(null, newTokens.access);

                    originalRequest.headers.Authorization = `Bearer ${newTokens.access}`;
                    return api(originalRequest);
                } catch (refreshError) {
                    processQueue(refreshError, null);
                    useAuthStore.getState().clearAuth();
                    window.location.replace(authPaths.login);
                    return Promise.reject(refreshError);
                } finally {
                    isRefreshing = false;
                }
            } else {
                useAuthStore.getState().clearAuth();
                window.location.replace(authPaths.login);
            }
        }

        if (error.response?.data?.error?.message) {
            error.message = error.response.data.error.message;
        }

        return Promise.reject(error);
    },
);
