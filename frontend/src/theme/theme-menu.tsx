import { useEffect, useRef, useState } from 'react';
import { Check, Monitor, Moon, Sun, type LucideIcon } from 'lucide-react';

import type { Theme } from '@/theme/theme-context';
import { useTheme } from '@/theme/use-theme';

interface ThemeOption {
    icon: LucideIcon;
    label: string;
    value: Theme;
}

const themeOptions: readonly ThemeOption[] = [
    {
        value: 'light',
        label: 'Claro',
        icon: Sun,
    },
    {
        value: 'dark',
        label: 'Oscuro',
        icon: Moon,
    },
    {
        value: 'system',
        label: 'Sistema',
        icon: Monitor,
    },
];

export function ThemeMenu() {
    const [open, setOpen] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    const { theme, setTheme } = useTheme();

    const selectedOption =
        themeOptions.find((option) => option.value === theme) ?? themeOptions[2];

    const SelectedIcon = selectedOption.icon;

    useEffect(() => {
        if (!open) {
            return;
        }

        const handlePointerDown = (event: PointerEvent) => {
            if (
                containerRef.current &&
                !containerRef.current.contains(event.target as Node)
            ) {
                setOpen(false);
            }
        };

        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                setOpen(false);
            }
        };

        document.addEventListener('pointerdown', handlePointerDown);
        document.addEventListener('keydown', handleKeyDown);

        return () => {
            document.removeEventListener('pointerdown', handlePointerDown);
            document.removeEventListener('keydown', handleKeyDown);
        };
    }, [open]);

    return (
        <div ref={containerRef} className='relative'>
            <button
                type='button'
                className='inline-flex size-11 items-center justify-center rounded-full text-muted-foreground transition hover:bg-surface-muted hover:text-primary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary'
                aria-label={`Tema actual: ${selectedOption.label}`}
                aria-haspopup='menu'
                aria-expanded={open}
                aria-controls='public-theme-menu'
                title='Cambiar tema'
                onClick={() => setOpen((current) => !current)}
            >
                <SelectedIcon className='size-5' aria-hidden='true' />
            </button>

            {open ? (
                <div
                    id='public-theme-menu'
                    className='absolute right-0 top-[calc(100%+0.5rem)] z-50 w-44 overflow-hidden rounded-2xl border border-border bg-surface p-2 shadow-card'
                    role='menu'
                    aria-label='Seleccionar tema'
                >
                    {themeOptions.map((option) => {
                        const Icon = option.icon;
                        const selected = theme === option.value;

                        return (
                            <button
                                key={option.value}
                                type='button'
                                className={
                                    'flex min-h-11 w-full items-center gap-3 rounded-xl px-3 text-sm font-semibold transition ' +
                                    (selected
                                        ? 'bg-primary/10 text-primary'
                                        : 'text-muted-foreground hover:bg-surface-muted hover:text-foreground')
                                }
                                role='menuitemradio'
                                aria-checked={selected}
                                onClick={() => {
                                    setTheme(option.value);
                                    setOpen(false);
                                }}
                            >
                                <Icon className='size-4 shrink-0' aria-hidden='true' />

                                <span className='flex-1 text-left'>{option.label}</span>

                                {selected ? (
                                    <Check className='size-4' aria-hidden='true' />
                                ) : null}
                            </button>
                        );
                    })}
                </div>
            ) : null}
        </div>
    );
}
