import {
    clearAuthTokens,
    getAccessToken,
    getRefreshToken,
    setAuthTokens,
    type AuthTokenPair,
} from '@/api/auth-tokens';
import { apiRequest, type ApiSuccessResponse, ApiError } from '@/api/client';
import { apiEndpoints } from '@/api/endpoints';

export type UserRole = 'platform_admin' | 'academic_admin' | 'student';

export interface CurrentUser {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    avatar_url: string | null;
    roles: UserRole[];
}

export interface GoogleLoginResult {
    user: CurrentUser;
    is_new_user: boolean;
}

interface GoogleLoginData extends AuthTokenPair {
    user: CurrentUser;
    is_new_user: boolean;
}

interface CsrfData {
    csrf_cookie_set: boolean;
}

interface LogoutData {
    revoked: true;
}

let refreshPromise: Promise<AuthTokenPair | null> | null = null;

export async function loginWithGoogle(credential: string): Promise<GoogleLoginResult> {
    const response = await apiRequest<ApiSuccessResponse<GoogleLoginData>>(
        apiEndpoints.auth.google,
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                credential,
            }),
        },
    );

    setAuthTokens(response.data);

    return {
        user: response.data.user,
        is_new_user: response.data.is_new_user,
    };
}

async function performTokenRefresh(): Promise<AuthTokenPair | null> {
    const refresh = getRefreshToken();

    if (!refresh) {
        clearAuthTokens();

        return null;
    }

    try {
        const response = await apiRequest<ApiSuccessResponse<AuthTokenPair>>(
            apiEndpoints.auth.refresh,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    refresh,
                }),
            },
        );

        setAuthTokens(response.data);

        return response.data;
    } catch (error: unknown) {
        if (
            error instanceof ApiError &&
            (error.status === 400 || error.status === 401)
        ) {
            clearAuthTokens();

            return null;
        }

        throw error;
    }
}

export function refreshAuthTokens(): Promise<AuthTokenPair | null> {
    if (!refreshPromise) {
        refreshPromise = performTokenRefresh().finally(() => {
            refreshPromise = null;
        });
    }

    return refreshPromise;
}

export async function getCurrentUser(signal?: AbortSignal): Promise<CurrentUser> {
    const response = await apiRequest<ApiSuccessResponse<CurrentUser>>(
        apiEndpoints.auth.currentUser,
        {
            method: 'GET',
            signal,
        },
    );

    return response.data;
}

function isAuthenticationError(error: unknown): boolean {
    return error instanceof ApiError && error.status === 401;
}

export async function resolveCurrentUser(
    signal?: AbortSignal,
): Promise<CurrentUser | null> {
    let refreshAttempted = false;

    if (!getAccessToken()) {
        const tokens = await refreshAuthTokens();

        if (!tokens) {
            return null;
        }

        refreshAttempted = true;
    }

    try {
        return await getCurrentUser(signal);
    } catch (error: unknown) {
        if (!isAuthenticationError(error)) {
            throw error;
        }

        if (refreshAttempted) {
            clearAuthTokens();

            return null;
        }
    }

    const tokens = await refreshAuthTokens();

    if (!tokens) {
        return null;
    }

    try {
        return await getCurrentUser(signal);
    } catch (error: unknown) {
        if (isAuthenticationError(error)) {
            clearAuthTokens();

            return null;
        }

        throw error;
    }
}

export async function logoutCurrentUser(): Promise<void> {
    const refresh = getRefreshToken();

    if (!refresh) {
        clearAuthTokens();

        return;
    }

    try {
        await apiRequest<ApiSuccessResponse<LogoutData>>(apiEndpoints.auth.logout, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                refresh,
            }),
        });
    } catch (error: unknown) {
        if (!(error instanceof ApiError && error.status === 401)) {
            throw error;
        }
    } finally {
        clearAuthTokens();
    }
}

/**
 * Compatibilidad temporal con el flujo anterior de allauth.
 *
 * Se eliminará al migrar start-google-login.ts a
 * Google Identity Services.
 */
export async function ensureCsrfCookie(signal?: AbortSignal): Promise<void> {
    await apiRequest<ApiSuccessResponse<CsrfData>>(apiEndpoints.auth.csrf, {
        method: 'GET',
        signal,
    });
}
