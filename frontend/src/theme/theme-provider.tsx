import { useEffect, useState, useMemo } from 'react';
import { ThemeProviderContext, type Theme } from './use-theme';

export function ThemeProvider({
    children,
    defaultTheme = 'system',
    storageKey = 'ruta-agustina-ui-theme',
}: {
    children: React.ReactNode;
    defaultTheme?: Theme;
    storageKey?: string;
}) {
    const [theme, setTheme] = useState<Theme>(
        () => (localStorage.getItem(storageKey) as Theme) || defaultTheme,
    );

    useEffect(() => {
        const root = window.document.documentElement;
        root.classList.remove('light', 'dark');

        if (theme === 'system') {
            const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
                ? 'dark'
                : 'light';
            root.classList.add(systemTheme);
            return;
        }

        root.classList.add(theme);
    }, [theme]);

    const value = useMemo(
        () => ({
            theme,
            setTheme: (newTheme: Theme) => {
                localStorage.setItem(storageKey, newTheme);
                setTheme(newTheme);
            },
        }),
        [theme, storageKey],
    );

    return <ThemeProviderContext.Provider value={value}>{children}</ThemeProviderContext.Provider>;
}
