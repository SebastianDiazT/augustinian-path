import { ensureCsrfCookie } from '@/api/auth';
import { API_BASE_URL } from '@/api/client';
import { getCsrfToken } from '@/api/csrf';
import { apiEndpoints } from '@/api/endpoints';
import { authPaths } from '@/app/paths';

function appendHiddenField(form: HTMLFormElement, name: string, value: string): void {
    const input = document.createElement('input');

    input.type = 'hidden';
    input.name = name;
    input.value = value;

    form.append(input);
}

export async function startGoogleLogin(): Promise<void> {
    await ensureCsrfCookie();

    const csrfToken = getCsrfToken();
    const callbackUrl = new URL(authPaths.callback, window.location.origin).toString();

    const form = document.createElement('form');

    form.method = 'post';
    form.action = API_BASE_URL + apiEndpoints.headlessAuth.providerRedirect;
    form.acceptCharset = 'UTF-8';
    form.hidden = true;

    appendHiddenField(form, 'csrfmiddlewaretoken', csrfToken);
    appendHiddenField(form, 'provider', 'google');
    appendHiddenField(form, 'process', 'login');
    appendHiddenField(form, 'callback_url', callbackUrl);

    document.body.append(form);
    form.submit();
}
