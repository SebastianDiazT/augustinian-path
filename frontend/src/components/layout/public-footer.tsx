import { ShieldCheck } from 'lucide-react';
import { Link } from 'react-router';

import { publicPaths } from '@/app/paths';
import { BrandLogo } from '@/components/brand/brand-logo';

const currentYear = new Date().getFullYear();

const footerLinkClass =
    'inline-flex min-h-8 items-center text-sm text-muted-foreground ' +
    'transition hover:translate-x-1 hover:text-primary ' +
    'focus-visible:rounded focus-visible:outline-2 ' +
    'focus-visible:outline-offset-2 focus-visible:outline-primary';

export function PublicFooter() {
    return (
        <footer className='border-t border-border bg-surface'>
            <div className='mx-auto w-full max-w-7xl px-4 py-10 sm:px-6 lg:py-14'>
                <div className='grid gap-10 sm:grid-cols-2 lg:grid-cols-[1.4fr_0.7fr_0.9fr]'>
                    <div className='max-w-md sm:col-span-2 lg:col-span-1'>
                        <Link
                            to={publicPaths.home}
                            className='inline-flex rounded-xl focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-primary'
                            aria-label='Ir al inicio de Ruta Agustina'
                        >
                            <BrandLogo />
                        </Link>

                        <p className='mt-5 text-sm leading-7 text-muted-foreground'>
                            Plataforma independiente para explorar planes de estudio,
                            organizar cursos y preparar una planificación académica
                            personal.
                        </p>

                        <div className='mt-5 inline-flex items-center gap-2 rounded-full border border-border bg-background px-3 py-1.5 text-xs font-bold text-muted-foreground'>
                            <ShieldCheck
                                className='size-4 text-primary'
                                aria-hidden='true'
                            />
                            Proyecto independiente
                        </div>
                    </div>

                    <nav aria-labelledby='footer-support'>
                        <h2
                            id='footer-support'
                            className='text-xs font-extrabold uppercase tracking-[0.16em] text-foreground'
                        >
                            Soporte
                        </h2>

                        <ul className='mt-4 space-y-2'>
                            <li>
                                <Link
                                    to={publicPaths.support}
                                    className={footerLinkClass}
                                >
                                    Centro de ayuda
                                </Link>
                            </li>

                            <li>
                                <Link
                                    to={publicPaths.supportContact}
                                    className={footerLinkClass}
                                >
                                    Contacto de soporte
                                </Link>
                            </li>
                        </ul>
                    </nav>

                    <nav aria-labelledby='footer-legal'>
                        <h2
                            id='footer-legal'
                            className='text-xs font-extrabold uppercase tracking-[0.16em] text-foreground'
                        >
                            Legal
                        </h2>

                        <ul className='mt-4 space-y-2'>
                            <li>
                                <Link
                                    to={publicPaths.privacy}
                                    className={footerLinkClass}
                                >
                                    Política de privacidad
                                </Link>
                            </li>

                            <li>
                                <Link
                                    to={publicPaths.terms}
                                    className={footerLinkClass}
                                >
                                    Términos de servicio
                                </Link>
                            </li>

                            <li>
                                <Link
                                    to={publicPaths.cookies}
                                    className={footerLinkClass}
                                >
                                    Política de cookies
                                </Link>
                            </li>
                        </ul>
                    </nav>
                </div>

                <div className='mt-12 flex flex-col gap-3 border-t border-border pt-6 text-xs leading-5 text-muted-foreground md:flex-row md:items-center md:justify-between'>
                    <p>© {currentYear} Ruta Agustina. Todos los derechos reservados.</p>

                    <p className='max-w-xl md:text-right'>
                        Herramienta independiente de planificación académica. <br />
                        No representa oficialmente a ninguna institución universitaria.
                    </p>
                </div>
            </div>
        </footer>
    );
}
