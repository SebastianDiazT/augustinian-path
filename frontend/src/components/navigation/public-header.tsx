import { Link } from 'react-router-dom';
import { LogIn } from 'lucide-react';
import { publicPaths } from '@/app/paths';
import { ES_UI } from '@/locales/es';
import { BrandLogo } from '@/components/brand/brand-logo';
import { ThemeMenu } from '@/theme/theme-menu';
import { Button } from '@/components/ui/button';

export function PublicHeader() {
    return (
        <header className='sticky top-0 z-50 w-full border-b border-border bg-background/90 backdrop-blur-xl supports-backdrop-filter:bg-background/60'>
            <div className='mx-auto flex h-16 md:h-20 w-full max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8'>
                <Link
                    to={publicPaths.home}
                    className='inline-flex min-w-0 shrink items-center rounded-xl transition-opacity hover:opacity-80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-4 focus-visible:ring-offset-background'
                    aria-label={`Ir al inicio de ${ES_UI.brand.name}`}
                >
                    <BrandLogo showTagline={false} className='scale-90 origin-left sm:scale-100' />
                </Link>

                <div className='flex shrink-0 items-center gap-2 sm:gap-4'>
                    <ThemeMenu />

                    <Link to={publicPaths.login} tabIndex={-1}>
                        <Button className='group relative h-9 overflow-hidden rounded-xl bg-primary px-4 font-bold text-primary-foreground shadow-[0_1px_4px_rgba(0,0,0,0.16)] transition-all duration-300 hover:scale-[1.02] hover:bg-primary/95 hover:shadow-[0_4px_12px_rgba(128,0,32,0.25)] active:scale-95 sm:h-10 sm:px-5 dark:hover:shadow-[0_4px_12px_rgba(248,113,113,0.25)]'>
                            <span className='hidden sm:inline'>{ES_UI.navigation.login}</span>
                            <span className='sm:hidden'>{ES_UI.navigation.loginMobile}</span>

                            <LogIn
                                className='ml-2 size-4 shrink-0 transition-transform duration-300 group-hover:translate-x-0.5'
                                aria-hidden='true'
                            />
                        </Button>
                    </Link>
                </div>
            </div>
        </header>
    );
}
