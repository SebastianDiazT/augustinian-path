const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();

export const API_BASE_URL = (configuredBaseUrl || 'http://localhost:8000').replace(
    /\/+$/,
    '',
);

export interface ApiMeta {
    request_id: string;
    api_version: string;
    timestamp: string;
}

export interface ApiSuccessResponse<T> {
    data: T;
    meta: ApiMeta;
}

export class ApiError extends Error {
    readonly status: number;
    readonly payload: unknown;

    constructor(status: number, payload: unknown) {
        super(`La API respondió con el estado ${status}.`);

        this.name = 'ApiError';
        this.status = status;
        this.payload = payload;
    }
}

export async function apiRequest<T>(
    path: string,
    options: RequestInit = {},
): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...options,
        credentials: 'include',
        headers: {
            Accept: 'application/json',
            ...options.headers,
        },
    });

    const contentType = response.headers.get('content-type');
    const payload: unknown = contentType?.includes('application/json')
        ? await response.json()
        : null;

    if (!response.ok) {
        throw new ApiError(response.status, payload);
    }

    return payload as T;
}
