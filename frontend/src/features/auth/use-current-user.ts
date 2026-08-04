import { useQuery } from '@tanstack/react-query';

import { getCurrentUser } from '../../api/auth';
import type { CurrentUser } from '../../api/auth';
import { ApiError } from '../../api/client';

export const currentUserQueryKey = ['auth', 'current-user'] as const;

async function getCurrentSession(signal: AbortSignal): Promise<CurrentUser | null> {
    try {
        return await getCurrentUser(signal);
    } catch (error: unknown) {
        if (
            error instanceof ApiError &&
            (error.status === 401 || error.status === 403)
        ) {
            return null;
        }

        throw error;
    }
}

export function useCurrentUser() {
    return useQuery({
        queryKey: currentUserQueryKey,
        queryFn: ({ signal }) => getCurrentSession(signal),
    });
}
