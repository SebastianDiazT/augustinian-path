import { Toaster as Sonner } from 'sonner';

type ToasterProps = React.ComponentProps<typeof Sonner>;

export function Toaster({ ...props }: ToasterProps) {
    return (
        <Sonner
            className='toaster group'
            toastOptions={{
                classNames: {
                    toast: 'group toast group-[.toaster]:bg-surface group-[.toaster]:text-foreground group-[.toaster]:border-border shadow-lg rounded-xl',
                    description: 'group-[.toast]:text-muted-foreground',
                    actionButton:
                        'group-[.toast]:bg-primary group-[.toast]:text-primary-foreground',
                    cancelButton: 'group-[.toast]:bg-muted group-[.toast]:text-muted-foreground',
                    error: 'group-[.toaster]:bg-destructive group-[.toaster]:text-destructive-foreground',
                    success:
                        'group-[.toaster]:bg-emerald-500 group-[.toaster]:text-white dark:group-[.toaster]:bg-emerald-600',
                },
            }}
            {...props}
        />
    );
}
