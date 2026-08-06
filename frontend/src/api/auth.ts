import { apiRequest, type ApiSuccessResponse, ApiError } from '@/api/client';
import { getCsrfToken } from '@/api/csrf';
import { apiEndpoints } from '@/api/endpoints';

export type UserRole = 'platform_admin' | 'student';

export interface CurrentUser {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    avatar_url: string | null;
    roles: UserRole[];
}

interface CsrfData {
    csrf_cookie_set: boolean;
}

interface LogoutData {
    authenticated: false;
}

export async function ensureCsrfCookie(signal?: AbortSignal): Promise<void> {
    await apiRequest<ApiSuccessResponse<CsrfData>>(apiEndpoints.auth.csrf, {
        method: 'GET',
        signal,
    });
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

export async function logoutCurrentUser(): Promise<void> {
    await ensureCsrfCookie();

    try {
        await apiRequest<ApiSuccessResponse<LogoutData>>(apiEndpoints.auth.logout, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
            },
        });
    } catch (error: unknown) {
        if (
            error instanceof ApiError &&
            (error.status === 401 || error.status === 403)
        ) {
            return;
        }

        throw error;
    }
}
