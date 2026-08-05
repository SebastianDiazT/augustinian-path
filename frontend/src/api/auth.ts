import { apiRequest, type ApiSuccessResponse } from '@/api/client';

export type UserRole = 'platform_admin' | 'student';

export interface CurrentUser {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    roles: UserRole[];
}

export async function getCurrentUser(signal?: AbortSignal): Promise<CurrentUser> {
    const response = await apiRequest<ApiSuccessResponse<CurrentUser>>(
        '/api/v1/auth/me/',
        {
            method: 'GET',
            signal,
        },
    );

    return response.data;
}
