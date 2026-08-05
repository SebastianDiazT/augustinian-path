import { CalendarDays, ShieldCheck } from 'lucide-react';
import { BrandLogo } from '@/components/brand/brand-logo';

export function PublicFooter() {
    return (
        <footer className='relative overflow-hidden bg-primary text-primary-foreground'>
            <div
                className='pointer-events-none absolute -top-24 right-0 size-64 rounded-full bg-accent/20 blur-3xl'
                aria-hidden='true'
            />

            <div className='relative mx-auto w-full max-w-6xl px-6 py-10'>
                <div className='grid gap-10 md:grid-cols-[1.2fr_1fr]'>
                    <div className='max-w-md'>
                        <div className='flex items-center gap-3'>
                            <BrandLogo inverse />
                        </div>

                        <p className='mt-5 text-sm leading-6 text-primary-foreground/75'>
                            Organiza tus cursos, explora tu plan curricular y construye
                            horarios que se adapten a tus necesidades.
                        </p>
                    </div>

                    <ul className='grid gap-3 sm:grid-cols-2'>
                        <li className='flex gap-3 rounded-2xl border border-white/10 bg-white/5 p-4'>
                            <ShieldCheck
                                className='mt-0.5 size-5 shrink-0 text-accent'
                                aria-hidden='true'
                            />

                            <div>
                                <p className='text-sm font-bold'>
                                    Acceso institucional
                                </p>
                                <p className='mt-1 text-xs leading-5 text-primary-foreground/70'>
                                    Disponible para cuentas institucionales autorizadas.
                                </p>
                            </div>
                        </li>

                        <li className='flex gap-3 rounded-2xl border border-white/10 bg-white/5 p-4'>
                            <CalendarDays
                                className='mt-0.5 size-5 shrink-0 text-accent'
                                aria-hidden='true'
                            />

                            <div>
                                <p className='text-sm font-bold'>
                                    Horarios y calendario
                                </p>
                                <p className='mt-1 text-xs leading-5 text-primary-foreground/70'>
                                    Prepara y exporta tu planificación académica.
                                </p>
                            </div>
                        </li>
                    </ul>
                </div>

                <div className='mt-10 border-t border-white/10 pt-5 text-xs text-primary-foreground/60'>
                    Ruta Agustina · Herramienta de planificación académica
                </div>
            </div>
        </footer>
    );
}
