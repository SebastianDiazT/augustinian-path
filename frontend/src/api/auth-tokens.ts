const refreshTokenStorageKey = 'ruta-agustina.auth.refresh-token';

let accessToken: string | null = null;

export interface AuthTokenPair {
    access: string;
    refresh: string;
}

function getSessionStorage(): Storage | null {
    if (typeof window === 'undefined') {
        return null;
    }

    try {
        return window.sessionStorage;
    } catch {
        return null;
    }
}

export function getAccessToken(): string | null {
    return accessToken;
}

export function getRefreshToken(): string | null {
    return getSessionStorage()?.getItem(refreshTokenStorageKey) ?? null;
}

export function setAccessToken(token: string): void {
    accessToken = token;
}

export function setAuthTokens(tokens: AuthTokenPair): void {
    accessToken = tokens.access;

    getSessionStorage()?.setItem(refreshTokenStorageKey, tokens.refresh);
}

export function clearAuthTokens(): void {
    accessToken = null;

    getSessionStorage()?.removeItem(refreshTokenStorageKey);
}
