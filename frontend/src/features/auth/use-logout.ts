import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

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

            toast.success('Sesión cerrada correctamente', {
                id: 'auth-logout-success',
            });
        },
        onError: () => {
            toast.error('No se pudo cerrar la sesión', {
                id: 'auth-logout-error',
                description: 'Comprueba tu conexión e inténtalo nuevamente.',
            });
        },
    });
}
