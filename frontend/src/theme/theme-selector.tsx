import type { ChangeEvent } from 'react';

import type { Theme } from '@/theme/theme-context';
import { useTheme } from '@/theme/use-theme';

export function ThemeSelector() {
    const { theme, resolvedTheme, setTheme } = useTheme();

    const handleChange = (event: ChangeEvent<HTMLSelectElement>) => {
        setTheme(event.target.value as Theme);
    };

    return (
        <label className='flex items-center gap-3 text-sm'>
            <span className='text-muted-foreground'>Tema</span>
            <select
                className='rounded-xl border border-border bg-surface px-3 py-2 text-foreground shadow-sm outline-none transition focus:border-ring focus:ring-2 focus:ring-ring/20'
                value={theme}
                onChange={handleChange}
            >
                <option value='light'>Claro</option>
                <option value='dark'>Oscuro</option>
                <option value='system'>Sistema ({resolvedTheme})</option>
            </select>
        </label>
    );
}
