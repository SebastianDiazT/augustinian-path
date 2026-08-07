import { useQuery } from '@tanstack/react-query';

import { resolveCurrentUser, type CurrentUser } from '@/api/auth';

export const currentUserQueryKey = ['auth', 'current-user'] as const;

async function queryCurrentUser(signal: AbortSignal): Promise<CurrentUser | null> {
    return resolveCurrentUser(signal);
}

export function useCurrentUser() {
    return useQuery({
        queryKey: currentUserQueryKey,
        queryFn: ({ signal }) => queryCurrentUser(signal),
        retry: false,
    });
}
