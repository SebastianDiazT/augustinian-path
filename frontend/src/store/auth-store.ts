import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { type AuthTokens, type CurrentUser } from '@/types/auth';

interface AuthState {
    tokens: AuthTokens | null;
    user: CurrentUser | null;
    isAuthenticated: boolean;

    setTokens: (tokens: AuthTokens) => void;
    setUser: (user: CurrentUser) => void;
    clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            tokens: null,
            user: null,
            isAuthenticated: false,

            setTokens: (tokens) => set({ tokens, isAuthenticated: true }),

            setUser: (user) => set({ user }),

            clearAuth: () => set({ tokens: null, user: null, isAuthenticated: false }),
        }),
        {
            name: 'ruta-agustina-auth',
            partialize: (state) => ({ tokens: state.tokens, user: state.user }),
        },
    ),
);
