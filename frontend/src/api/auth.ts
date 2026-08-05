import { apiRequest, type ApiSuccessResponse } from '@/api/client';
import { apiEndpoints } from '@/api/endpoints';

export type UserRole = 'platform_admin' | 'student';

export interface CurrentUser {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    roles: UserRole[];
}

interface CsrfData {
    csrf_cookie_set: boolean;
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
