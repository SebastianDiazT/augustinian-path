import { useEffect, useMemo, useState } from 'react';
import type { PropsWithChildren } from 'react';

import { ThemeContext, type ResolvedTheme, type Theme } from '@/theme/theme-context';

const STORAGE_KEY = 'ruta-unsa-theme';

function getStoredTheme(): Theme {
    const storedTheme = window.localStorage.getItem(STORAGE_KEY);

    if (storedTheme === 'light' || storedTheme === 'dark' || storedTheme === 'system') {
        return storedTheme;
    }

    return 'system';
}

function resolveTheme(theme: Theme): ResolvedTheme {
    if (theme !== 'system') {
        return theme;
    }

    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

export function ThemeProvider({ children }: PropsWithChildren) {
    const [theme, setTheme] = useState<Theme>(getStoredTheme);
    const [resolvedTheme, setResolvedTheme] = useState<ResolvedTheme>(() =>
        resolveTheme(theme),
    );

    useEffect(() => {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

        const applyTheme = () => {
            const nextTheme = resolveTheme(theme);

            document.documentElement.dataset.theme = nextTheme;

            setResolvedTheme(nextTheme);
        };

        window.localStorage.setItem(STORAGE_KEY, theme);
        applyTheme();

        if (theme === 'system') {
            mediaQuery.addEventListener('change', applyTheme);
        }

        return () => {
            mediaQuery.removeEventListener('change', applyTheme);
        };
    }, [theme]);

    const value = useMemo(
        () => ({
            theme,
            resolvedTheme,
            setTheme,
        }),
        [theme, resolvedTheme],
    );

    return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}
