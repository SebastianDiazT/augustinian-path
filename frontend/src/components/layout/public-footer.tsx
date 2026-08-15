import { Link, useLocation } from 'react-router-dom';
import { ShieldCheck, Info } from 'lucide-react';
import { publicPaths } from '@/app/paths';
import { ES_UI } from '@/locales/es';
import { BrandLogo } from '@/components/brand/brand-logo';

export function PublicFooter() {
    const currentYear = new Date().getFullYear();
    const { pathname } = useLocation();

    const handleFeaturesClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
        if (pathname === publicPaths.home) {
            e.preventDefault();
            document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
        }
    };

    const columnClass = 'space-y-5';
    const titleClass = 'text-sm font-extrabold text-foreground tracking-tight';

    const linkClass =
        'inline-flex items-center text-[0.95rem] text-muted-foreground transition-all duration-200 hover:text-primary hover:translate-x-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-sm';

    return (
        <footer className='relative border-t border-border bg-surface pt-16 pb-8 overflow-hidden'>
            <div
                className='absolute inset-x-0 top-0 h-px bg-linear-to-r from-transparent via-primary/20 to-transparent'
                aria-hidden='true'
            />

            <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
                <div className='grid gap-12 lg:grid-cols-6'>
                    <div className='flex flex-col items-start gap-6 lg:col-span-2'>
                        <Link
                            to={publicPaths.home}
                            className='inline-block rounded-xl focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary transition-transform hover:scale-[0.98]'
                        >
                            <BrandLogo className='scale-95 origin-left' />
                        </Link>
                        <p className='max-w-sm text-sm leading-relaxed text-muted-foreground'>
                            {ES_UI.footer.description}
                        </p>
                        <div className='inline-flex items-center gap-2 rounded-lg border border-accent/20 bg-accent/5 px-3 py-2 text-xs font-bold text-accent-foreground dark:bg-accent/10 dark:text-accent'>
                            <ShieldCheck className='size-4' aria-hidden='true' />
                            {ES_UI.footer.studentProject}
                        </div>
                    </div>

                    <div className='grid grid-cols-2 gap-8 sm:grid-cols-3 lg:col-span-4 lg:justify-items-end'>
                        <nav aria-labelledby='footer-nav' className={columnClass}>
                            <h2 id='footer-nav' className={titleClass}>
                                {ES_UI.footer.columns.platform.title}
                            </h2>
                            <ul className='space-y-3.5'>
                                <li>
                                    <Link
                                        to={`${publicPaths.home}#features`}
                                        onClick={handleFeaturesClick}
                                        className={linkClass}
                                    >
                                        {ES_UI.footer.columns.platform.features}
                                    </Link>
                                </li>
                                <li>
                                    <Link to={publicPaths.login} className={linkClass}>
                                        {ES_UI.navigation.login}
                                    </Link>
                                </li>
                            </ul>
                        </nav>

                        <nav aria-labelledby='footer-support' className={columnClass}>
                            <h2 id='footer-support' className={titleClass}>
                                {ES_UI.footer.columns.support.title}
                            </h2>
                            <ul className='space-y-3.5'>
                                <li>
                                    <Link to={publicPaths.support} className={linkClass}>
                                        {ES_UI.footer.columns.support.helpCenter}
                                    </Link>
                                </li>
                                <li>
                                    <Link to={publicPaths.support} className={linkClass}>
                                        {ES_UI.footer.columns.support.contact}
                                    </Link>
                                </li>
                            </ul>
                        </nav>

                        <nav aria-labelledby='footer-legal' className={columnClass}>
                            <h2 id='footer-legal' className={titleClass}>
                                {ES_UI.footer.columns.legal.title}
                            </h2>
                            <ul className='space-y-3.5'>
                                <li>
                                    <Link to={publicPaths.privacy} className={linkClass}>
                                        {ES_UI.footer.columns.legal.privacy}
                                    </Link>
                                </li>
                                <li>
                                    <Link to={publicPaths.terms} className={linkClass}>
                                        {ES_UI.footer.columns.legal.terms}
                                    </Link>
                                </li>
                            </ul>
                        </nav>
                    </div>
                </div>

                <div className='mt-16 flex flex-col gap-6 border-t border-border pt-8 sm:flex-row sm:items-center sm:justify-between'>
                    <div className='flex items-start gap-3 rounded-xl bg-surface-muted/50 p-4 sm:max-w-2xl sm:bg-transparent sm:p-0'>
                        <Info
                            className='mt-0.5 size-4 shrink-0 text-muted-foreground'
                            aria-hidden='true'
                        />
                        <p className='text-xs leading-relaxed text-muted-foreground'>
                            {ES_UI.legal.disclaimer}
                        </p>
                    </div>

                    <p className='shrink-0 text-sm font-bold text-muted-foreground'>
                        {ES_UI.legal.copyright.replace('{year}', currentYear.toString())}
                    </p>
                </div>
            </div>
        </footer>
    );
}
