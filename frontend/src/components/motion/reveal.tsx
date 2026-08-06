import { useEffect, useRef } from 'react';
import type { PropsWithChildren } from 'react';

interface RevealProps extends PropsWithChildren {
    className?: string;
}

export function Reveal({ children, className = '' }: RevealProps) {
    const elementRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const element = elementRef.current;

        if (!element) {
            return;
        }

        const prefersReducedMotion = window.matchMedia(
            '(prefers-reduced-motion: reduce)',
        ).matches;

        if (prefersReducedMotion || !('IntersectionObserver' in window)) {
            element.dataset.revealed = 'true';
            return;
        }

        const observer = new IntersectionObserver(
            ([entry]) => {
                if (!entry?.isIntersecting) {
                    return;
                }

                element.dataset.revealed = 'true';
                observer.unobserve(element);
            },
            {
                rootMargin: '0px 0px -10% 0px',
                threshold: 0.15,
            },
        );

        observer.observe(element);

        return () => {
            observer.disconnect();
        };
    }, []);

    return (
        <div ref={elementRef} className={`reveal-on-scroll ${className}`}>
            {children}
        </div>
    );
}
