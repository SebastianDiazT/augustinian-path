const defaultApiVersion = 'v1';
const headlessApiVersion = 'v1';

const apiVersion = import.meta.env.VITE_API_VERSION?.trim() || defaultApiVersion;

const apiPrefix = `/api/${apiVersion}`;

export const apiEndpoints = {
    auth: {
        csrf: `${apiPrefix}/auth/csrf/`,
        google: `${apiPrefix}/auth/google/`,
        refresh: `${apiPrefix}/auth/refresh/`,
        currentUser: `${apiPrefix}/auth/me/`,
        logout: `${apiPrefix}/auth/logout/`,
    },
    headlessAuth: {
        providerRedirect:
            `/_allauth/browser/${headlessApiVersion}` + '/auth/provider/redirect',
    },
} as const;
