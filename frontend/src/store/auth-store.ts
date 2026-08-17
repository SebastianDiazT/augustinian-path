import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import axios from 'axios';
import { toast } from 'sonner';
import { api } from '@/lib/api';
import { type AuthTokens, type CurrentUser } from '@/types/auth';

interface AuthState {
    tokens: AuthTokens | null;
    user: CurrentUser | null;
    isAuthenticated: boolean;

    setTokens: (tokens: AuthTokens) => void;
    setUser: (user: CurrentUser) => void;
    clearAuth: () => void;
    syncProfile: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set, get) => ({
            tokens: null,
            user: null,
            isAuthenticated: false,

            setTokens: (tokens) => set({ tokens, isAuthenticated: true }),

            setUser: (user) => set({ user }),

            clearAuth: () => set({ tokens: null, user: null, isAuthenticated: false }),

            syncProfile: async () => {
                try {
                    const res = await api.get('/accounts/users/me/');
                    set({ user: res.data });
                } catch (error: unknown) {
                    console.error('Error al sincronizar el perfil:', error);
                    if (axios.isAxiosError(error) && error.response?.status === 401) {
                        toast.error('Tu sesión ha expirado. Por favor, vuelve a iniciar sesión.');
                        get().clearAuth();
                    }
                }
            },
        }),
        {
            name: 'ruta-agustina-auth',
            partialize: (state) => ({ tokens: state.tokens, user: state.user }),
        },
    ),
);
