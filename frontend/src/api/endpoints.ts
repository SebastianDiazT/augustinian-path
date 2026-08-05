const defaultApiVersion = 'v1';

const apiVersion = import.meta.env.VITE_API_VERSION?.trim() || defaultApiVersion;

const apiPrefix = `/api/${apiVersion}`;

export const apiEndpoints = {
    auth: {
        currentUser: `${apiPrefix}/auth/me/`,
    },
} as const;
