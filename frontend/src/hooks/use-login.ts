import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { type CredentialResponse } from '@react-oauth/google';
import { jwtDecode } from 'jwt-decode';
import { toast } from 'sonner';
import axios from 'axios';

import { api } from '@/lib/api';
import { privatePaths } from '@/app/paths';
import { ES_UI } from '@/locales/es';
import { useAuthStore } from '@/store/auth-store';
import { type CurrentUser } from '@/types/auth';

interface GoogleJwtPayload {
    email: string;
    name: string;
    picture: string;
}

export function useLogin() {
    const navigate = useNavigate();
    const { setTokens, setUser } = useAuthStore();
    const [isLoading, setIsLoading] = useState(false);

    const dict = ES_UI.auth.login;

    const handleGoogleSuccess = async (response: CredentialResponse) => {
        if (!response.credential) return;

        try {
            setIsLoading(true);
            const decoded = jwtDecode<GoogleJwtPayload>(response.credential);

            if (!decoded.email.endsWith('@unsa.edu.pe')) {
                toast.error(dict.errors.invalidDomain);
                return;
            }

            const apiRes = await api.post('/accounts/auth/google/', {
                id_token: response.credential,
            });

            const { access, refresh, user } = apiRes.data as {
                access: string;
                refresh: string;
                user: CurrentUser;
            };

            setTokens({ access, refresh });
            setUser(user);
            toast.success(`¡Bienvenido, ${user.full_name}!`);

            if (!user.cui) {
                navigate(privatePaths.onboardingCui);
            } else if (!user.school_memberships || user.school_memberships.length === 0) {
                navigate(privatePaths.onboardingSchool);
            } else {
                navigate(privatePaths.dashboard);
            }
        } catch (err: unknown) {
            console.error('Login Error:', err);
            if (axios.isAxiosError(err)) {
                toast.error(err.message || dict.errors.default);
            } else if (err instanceof Error) {
                toast.error(err.message);
            } else {
                toast.error(dict.errors.default);
            }
        } finally {
            setIsLoading(false);
        }
    };

    return {
        handleGoogleSuccess,
        isLoading,
        dict,
    };
}
