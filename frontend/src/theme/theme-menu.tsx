import { Check, Monitor, Moon, Sun, type LucideIcon } from 'lucide-react';
import { useTheme } from './use-theme';
import type { Theme } from './use-theme';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';

interface ThemeOption {
    value: Theme;
    label: string;
    icon: LucideIcon;
}

const themeOptions: readonly ThemeOption[] = [
    { value: 'light', label: 'Claro', icon: Sun },
    { value: 'dark', label: 'Oscuro', icon: Moon },
    { value: 'system', label: 'Sistema', icon: Monitor },
];

export function ThemeMenu() {
    const { theme, setTheme } = useTheme();

    const selectedOption = themeOptions.find((option) => option.value === theme) ?? themeOptions[2];
    const SelectedIcon = selectedOption.icon;

    return (
        <DropdownMenu>
            <DropdownMenuTrigger
                className={cn(
                    'inline-flex size-10 items-center justify-center rounded-full text-muted-foreground transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary',
                    'hover:bg-surface-muted hover:text-primary',
                    'dark:hover:bg-white/10 dark:hover:text-foreground',
                )}
                aria-label={`Tema actual: ${selectedOption.label}`}
            >
                <SelectedIcon className='size-5' aria-hidden='true' />
            </DropdownMenuTrigger>

            <DropdownMenuContent
                align='end'
                className='w-40 rounded-2xl border-border/50 p-2 shadow-sm dark:border-white/10'
            >
                {themeOptions.map((option) => {
                    const Icon = option.icon;
                    const isSelected = theme === option.value;

                    return (
                        <DropdownMenuItem
                            key={option.value}
                            onClick={() => setTheme(option.value)}
                            className={cn(
                                'flex min-h-10 cursor-pointer items-center gap-3 rounded-xl px-3 text-sm font-semibold transition-colors focus:outline-none',
                                isSelected
                                    ?
                                        'bg-primary/10 text-primary focus:bg-primary/15 dark:bg-primary/20 dark:text-primary dark:focus:bg-primary/30'
                                    :
                                        'text-muted-foreground focus:bg-surface-muted focus:text-foreground dark:focus:bg-white/10 dark:focus:text-foreground',
                            )}
                        >
                            <Icon className='size-4 shrink-0' aria-hidden='true' />
                            <span className='flex-1 text-left'>{option.label}</span>
                            {isSelected && <Check className='size-4' aria-hidden='true' />}
                        </DropdownMenuItem>
                    );
                })}
            </DropdownMenuContent>
        </DropdownMenu>
    );
}
