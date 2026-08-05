import { useMutation, useQueryClient } from '@tanstack/react-query';

import { logoutCurrentUser } from '@/api/auth';
import { currentUserQueryKey } from '@/features/auth/use-current-user';

export function useLogout() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: logoutCurrentUser,
        onMutate: async () => {
            await queryClient.cancelQueries({
                queryKey: currentUserQueryKey,
            });
        },
        onSuccess: () => {
            queryClient.setQueryData(currentUserQueryKey, null);
        },
    });
}
