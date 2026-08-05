import { Monitor, Moon, Sun, type LucideIcon } from 'lucide-react';

import type { Theme } from '@/theme/theme-context';
import { useTheme } from '@/theme/use-theme';

interface ThemeOption {
    value: Theme;
    label: string;
    icon: LucideIcon;
}

const themeOptions: ThemeOption[] = [
    {
        value: 'light',
        label: 'Tema claro',
        icon: Sun,
    },
    {
        value: 'dark',
        label: 'Tema oscuro',
        icon: Moon,
    },
    {
        value: 'system',
        label: 'Usar tema del sistema',
        icon: Monitor,
    },
];

export function ThemeSelector() {
    const { theme, setTheme } = useTheme();

    return (
        <div
            className='inline-flex items-center rounded-xl border border-border bg-surface-muted p-1'
            role='group'
            aria-label='Seleccionar tema'
        >
            {themeOptions.map((option) => {
                const Icon = option.icon;
                const isSelected = theme === option.value;

                return (
                    <button
                        key={option.value}
                        type='button'
                        className={
                            'inline-flex size-9 items-center justify-center rounded-lg transition ' +
                            (isSelected
                                ? 'bg-primary text-primary-foreground shadow-sm'
                                : 'text-muted-foreground hover:bg-surface hover:text-foreground')
                        }
                        aria-label={option.label}
                        aria-pressed={isSelected}
                        title={option.label}
                        onClick={() => setTheme(option.value)}
                    >
                        <Icon className='size-4' aria-hidden='true' />
                    </button>
                );
            })}
        </div>
    );
}
