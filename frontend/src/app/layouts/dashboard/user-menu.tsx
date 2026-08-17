import { useEffect, useRef, useState } from 'react';
import { ChevronDown, CircleHelp, LogOut } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { publicPaths } from '@/app/paths';
import { useAuthStore } from '@/store/auth-store';
import type { DashboardPanel } from './dashboard.types';

interface UserMenuProps {
    activePanel: DashboardPanel;
}

const panelLabels: Record<DashboardPanel, string> = {
    student: 'Estudiante',
    delegate: 'Delegado',
    admin: 'Administrador',
};

export function UserMenu({ activePanel }: UserMenuProps) {
    const { user, clearAuth } = useAuthStore();
    const navigate = useNavigate();
    const [isOpen, setIsOpen] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    const displayName = user?.full_name || user?.email || 'Usuario';

    const panelLabel = panelLabels[activePanel];

    useEffect(() => {
        if (!isOpen) return;
        const handlePointerDown = (event: PointerEvent) => {
            if (event.target instanceof Node && !containerRef.current?.contains(event.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('pointerdown', handlePointerDown);
        return () => document.removeEventListener('pointerdown', handlePointerDown);
    }, [isOpen]);

    const handleLogout = () => {
        clearAuth();
        navigate(publicPaths.home);
    };

    return (
        <div ref={containerRef} className='relative'>
            <button
                type='button'
                className='group flex min-h-11 items-center gap-2 rounded-xl px-2 text-left transition hover:bg-surface focus-visible:outline-2 focus-visible:outline-primary sm:gap-3'
                onClick={() => setIsOpen(!isOpen)}
            >
                <img
                    src={user?.picture_url}
                    alt='Avatar'
                    className='size-9 rounded-full border border-border shadow-sm object-cover'
                    referrerPolicy='no-referrer'
                />
                <span className='hidden min-w-0 sm:block'>
                    <span className='block max-w-40 truncate text-sm font-extrabold text-foreground'>
                        {displayName.split(' ')[0]}
                    </span>
                    <span className='block text-xs font-medium text-muted-foreground'>
                        {panelLabel}
                    </span>
                </span>
                <ChevronDown
                    className={`hidden size-4 text-muted-foreground transition-transform sm:block ${isOpen ? 'rotate-180' : ''}`}
                />
            </button>

            {isOpen && (
                <div className='absolute right-0 top-[calc(100%+8px)] z-50 w-72 overflow-hidden rounded-2xl border border-border bg-background shadow-2xl animate-in slide-in-from-top-2'>
                    <div className='border-b border-border p-4 bg-surface/50'>
                        <div className='flex items-center gap-3'>
                            <img
                                src={user?.picture_url}
                                alt='Avatar'
                                className='size-12 rounded-full border border-border'
                            />
                            <div className='min-w-0'>
                                <p className='truncate text-sm font-extrabold text-foreground'>
                                    {displayName}
                                </p>
                                <p className='mt-0.5 truncate text-xs text-muted-foreground'>
                                    {user?.email}
                                </p>
                            </div>
                        </div>
                        <span className='mt-3 inline-flex rounded-md bg-primary/10 px-2.5 py-1 text-xs font-bold text-primary'>
                            Panel {panelLabel}
                        </span>
                    </div>

                    <div className='p-2 space-y-1'>
                        <Link
                            to={publicPaths.support}
                            className='flex min-h-10 items-center gap-3 rounded-xl px-3 text-sm font-medium text-foreground transition hover:bg-muted'
                            onClick={() => setIsOpen(false)}
                        >
                            <CircleHelp className='size-4 text-muted-foreground' />
                            Ayuda y soporte
                        </Link>
                    </div>

                    <div className='border-t border-border p-2'>
                        <button
                            type='button'
                            className='flex min-h-10 w-full items-center gap-3 rounded-xl px-3 text-left text-sm font-bold text-destructive transition hover:bg-destructive/10'
                            onClick={handleLogout}
                        >
                            <LogOut className='size-4' />
                            Cerrar sesión
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
