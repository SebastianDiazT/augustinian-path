import { Link } from 'react-router-dom';
import { ArrowLeft, FileQuestion } from 'lucide-react';
import { publicPaths } from '@/app/paths';
import { ES_UI } from '@/locales/es';
import { Button } from '@/components/ui/button';
import { SEO } from '@/components/seo';

export default function NotFoundPage() {
    return (
        <div className='flex min-h-screen flex-col items-center justify-center bg-background px-6 text-center'>
            <SEO
                title={ES_UI.errors.notFoundTitle}
                description={ES_UI.errors.notFoundDescription}
            />

            <div className='mb-8 flex size-24 items-center justify-center rounded-3xl bg-primary/10 text-primary dark:bg-primary/20'>
                <FileQuestion className='size-12' aria-hidden='true' />
            </div>

            <h1 className='font-display text-9xl font-extrabold tracking-tight text-primary/10 dark:text-primary/5'>
                {ES_UI.errors.notFoundCode}
            </h1>

            <div className='-mt-10'>
                <h2 className='font-display text-3xl font-extrabold text-foreground sm:text-4xl'>
                    {ES_UI.errors.notFoundTitle}
                </h2>
                <p className='mx-auto mt-4 max-w-md text-lg leading-relaxed text-muted-foreground'>
                    {ES_UI.errors.notFoundDescription}
                </p>
            </div>

            <Link to={publicPaths.home} className='mt-10'>
                <Button
                    size='lg'
                    className='h-12 rounded-xl px-8 font-bold shadow-sm transition-transform hover:scale-[1.02] active:scale-95'
                >
                    <ArrowLeft className='mr-2 size-4' aria-hidden='true' />
                    {ES_UI.common.backToHome}
                </Button>
            </Link>
        </div>
    );
}
