import { Toaster } from 'sonner';

import { useTheme } from '@/theme/use-theme';

export function AppToaster() {
    const { resolvedTheme } = useTheme();

    return (
        <Toaster
            theme={resolvedTheme}
            position='bottom-right'
            richColors
            closeButton
            expand={false}
            duration={4_500}
            visibleToasts={3}
            offset={{
                bottom: 24,
                right: 24,
            }}
            mobileOffset={{
                bottom: 'calc(16px + env(safe-area-inset-bottom))',
                right: 16,
                left: 16,
            }}
            swipeDirections={['right']}
            containerAriaLabel='Notificaciones'
            toastOptions={{
                classNames: {
                    toast: ['!rounded-2xl', '!border', '!shadow-card'].join(' '),
                    title: '!font-extrabold',
                    description: '!opacity-85',
                    closeButton: [
                        '!border-current/15',
                        '!bg-inherit',
                        '!text-inherit',
                    ].join(' '),
                    actionButton: ['!bg-primary', '!text-primary-foreground'].join(' '),
                    cancelButton: [
                        '!bg-black/10',
                        '!text-current',
                        'dark:!bg-white/10',
                    ].join(' '),
                },
            }}
        />
    );
}
