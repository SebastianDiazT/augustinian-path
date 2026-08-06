import { useEffect, useRef, useState } from 'react';

import {
    ChevronDown,
    CircleHelp,
    ExternalLink,
    LoaderCircle,
    LogOut,
} from 'lucide-react';
import { Link } from 'react-router';

import type { CurrentUser } from '@/api/auth';
import { publicPaths } from '@/app/paths';
import { useLogout } from '@/features/auth/use-logout';

interface UserMenuProps {
    user: CurrentUser;
}

function getDisplayName(user: CurrentUser): string {
    return [user.first_name, user.last_name].filter(Boolean).join(' ') || user.email;
}

function getInitials(user: CurrentUser): string {
    const firstInitial = user.first_name.trim().charAt(0);
    const lastInitial = user.last_name.trim().charAt(0);

    const initials = `${firstInitial}${lastInitial}`;

    if (initials) {
        return initials.toUpperCase();
    }

    return user.email.slice(0, 2).toUpperCase();
}

export function UserMenu({ user }: UserMenuProps) {
    const [isOpen, setIsOpen] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);
    const logout = useLogout();

    const displayName = getDisplayName(user);
    const initials = getInitials(user);

    useEffect(() => {
        if (!isOpen) {
            return;
        }

        const handlePointerDown = (event: PointerEvent) => {
            if (
                event.target instanceof Node &&
                !containerRef.current?.contains(event.target)
            ) {
                setIsOpen(false);
            }
        };

        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                setIsOpen(false);
            }
        };

        document.addEventListener('pointerdown', handlePointerDown);
        document.addEventListener('keydown', handleKeyDown);

        return () => {
            document.removeEventListener('pointerdown', handlePointerDown);
            document.removeEventListener('keydown', handleKeyDown);
        };
    }, [isOpen]);

    const handleLogout = () => {
        logout.mutate(undefined, {
            onSuccess: () => {
                setIsOpen(false);
            },
        });
    };

    return (
        <div ref={containerRef} className='relative'>
            <button
                type='button'
                className='group flex min-h-11 items-center gap-2 rounded-xl px-2 text-left transition hover:bg-surface-muted focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary sm:gap-3'
                aria-expanded={isOpen}
                aria-haspopup='menu'
                onClick={() => setIsOpen((current) => !current)}
            >
                <span className='inline-flex size-10 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-extrabold text-primary-foreground shadow-sm'>
                    {initials}
                </span>

                <span className='hidden min-w-0 sm:block'>
                    <span className='block max-w-40 truncate text-sm font-extrabold text-foreground'>
                        {displayName}
                    </span>

                    <span className='block text-xs text-muted-foreground'>
                        Estudiante
                    </span>
                </span>

                <ChevronDown
                    className={
                        'hidden size-4 text-muted-foreground transition-transform sm:block ' +
                        (isOpen ? 'rotate-180' : '')
                    }
                    aria-hidden='true'
                />
            </button>

            {isOpen ? (
                <div
                    className='absolute right-0 top-[calc(100%+0.65rem)] z-50 w-72 overflow-hidden rounded-2xl border border-border bg-surface shadow-card'
                    role='menu'
                >
                    <div className='border-b border-border px-4 py-4'>
                        <p className='truncate text-sm font-extrabold'>{displayName}</p>

                        <p className='mt-1 truncate text-xs text-muted-foreground'>
                            {user.email}
                        </p>

                        <span className='mt-3 inline-flex rounded-full bg-primary/10 px-2.5 py-1 text-xs font-bold text-primary'>
                            Panel estudiantil
                        </span>
                    </div>

                    <div className='p-2'>
                        <Link
                            to={publicPaths.support}
                            role='menuitem'
                            className='flex min-h-10 items-center gap-3 rounded-xl px-3 text-sm font-semibold text-muted-foreground transition hover:bg-surface-muted hover:text-foreground'
                            onClick={() => setIsOpen(false)}
                        >
                            <CircleHelp className='size-4' aria-hidden='true' />
                            Ayuda y soporte
                        </Link>

                        <Link
                            to={publicPaths.home}
                            role='menuitem'
                            className='flex min-h-10 items-center gap-3 rounded-xl px-3 text-sm font-semibold text-muted-foreground transition hover:bg-surface-muted hover:text-foreground'
                            onClick={() => setIsOpen(false)}
                        >
                            <ExternalLink className='size-4' aria-hidden='true' />
                            Ir al sitio público
                        </Link>
                    </div>

                    <div className='border-t border-border p-2'>
                        <button
                            type='button'
                            role='menuitem'
                            className='flex min-h-10 w-full items-center gap-3 rounded-xl px-3 text-left text-sm font-bold text-primary transition hover:bg-primary/10 disabled:cursor-wait disabled:opacity-60'
                            disabled={logout.isPending}
                            aria-busy={logout.isPending}
                            onClick={handleLogout}
                        >
                            {logout.isPending ? (
                                <LoaderCircle
                                    className='size-4 motion-safe:animate-spin'
                                    aria-hidden='true'
                                />
                            ) : (
                                <LogOut className='size-4' aria-hidden='true' />
                            )}

                            {logout.isPending ? 'Cerrando sesión…' : 'Cerrar sesión'}
                        </button>

                        {logout.isError ? (
                            <p
                                className='px-3 pb-2 pt-1 text-xs font-semibold text-primary'
                                role='alert'
                            >
                                No se pudo cerrar la sesión.
                            </p>
                        ) : null}
                    </div>
                </div>
            ) : null}
        </div>
    );
}
