import { Loader2 } from 'lucide-react';
import { ES_UI } from '@/locales/es';
import { BrandMark } from '@/components/brand/brand-mark';

export function PageLoader() {
    return (
        <div className='flex min-h-screen flex-col items-center justify-center bg-background animate-reveal-soft'>
            <div className='relative flex items-center justify-center'>
                <BrandMark className='size-8 opacity-20 grayscale' aria-hidden='true' />
                <Loader2
                    className='absolute size-16 animate-spin text-primary'
                    aria-hidden='true'
                />
            </div>
            <p className='mt-6 text-sm font-bold uppercase tracking-widest text-muted-foreground'>
                {ES_UI.common.loading}
            </p>
        </div>
    );
}
