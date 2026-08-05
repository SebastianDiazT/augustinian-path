const csrfCookieName = 'csrftoken';

function readCookie(name: string): string | null {
    const prefix = `${name}=`;

    const cookie = document.cookie
        .split(';')
        .map((part) => part.trim())
        .find((part) => part.startsWith(prefix));

    if (!cookie) {
        return null;
    }

    return decodeURIComponent(cookie.slice(prefix.length));
}

export function getCsrfToken(): string {
    const csrfToken = readCookie(csrfCookieName);

    if (!csrfToken) {
        throw new Error('No se pudo obtener el token CSRF.');
    }

    return csrfToken;
}
