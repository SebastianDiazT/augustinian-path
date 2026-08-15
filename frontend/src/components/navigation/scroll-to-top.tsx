import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

export function ScrollToTop() {
    const { pathname, hash } = useLocation();

    useEffect(() => {
        if (hash) {
            const elementId = hash.replace('#', '');

            setTimeout(() => {
                const element = document.getElementById(elementId);
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth' });
                }
            }, 100);

            return;
        }

        window.scrollTo({
            top: 0,
            left: 0,
            behavior: 'smooth',
        });
    }, [pathname, hash]);

    return null;
}
