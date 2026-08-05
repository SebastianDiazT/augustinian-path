import { ensureCsrfCookie } from '@/api/auth';
import { API_BASE_URL } from '@/api/client';
import { apiEndpoints } from '@/api/endpoints';

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

function appendHiddenField(form: HTMLFormElement, name: string, value: string): void {
    const input = document.createElement('input');

    input.type = 'hidden';
    input.name = name;
    input.value = value;

    form.append(input);
}

export async function startGoogleLogin(): Promise<void> {
    await ensureCsrfCookie();

    const csrfToken = readCookie(csrfCookieName);

    if (!csrfToken) {
        throw new Error('No se pudo obtener el token CSRF.');
    }

    const form = document.createElement('form');

    form.method = 'post';
    form.action = API_BASE_URL + apiEndpoints.headlessAuth.providerRedirect;
    form.acceptCharset = 'UTF-8';
    form.hidden = true;

    appendHiddenField(form, 'csrfmiddlewaretoken', csrfToken);
    appendHiddenField(form, 'provider', 'google');
    appendHiddenField(form, 'process', 'login');
    appendHiddenField(form, 'callback_url', window.location.origin);

    document.body.append(form);
    form.submit();
}
