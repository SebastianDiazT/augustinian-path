import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthTokens {
    access: string;
    refresh: string;
}

interface AuthState {
    tokens: AuthTokens | null;
    isAuthenticated: boolean;
    setTokens: (tokens: AuthTokens) => void;
    clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            tokens: null,
            isAuthenticated: false,

            setTokens: (tokens) => set({ tokens, isAuthenticated: true }),

            clearAuth: () => set({ tokens: null, isAuthenticated: false }),
        }),
        {
            name: 'ruta-agustina-auth',
        },
    ),
);
