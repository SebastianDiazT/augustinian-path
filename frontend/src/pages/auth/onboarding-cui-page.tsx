import { IdCard, ArrowRight, AlertCircle, Loader2, Info } from 'lucide-react';
import { SEO } from '@/components/seo';
import { BrandLogo } from '@/components/brand/brand-logo';
import { Button } from '@/components/ui/button';
import { useOnboardingCui } from '@/hooks/use-onboarding-cui';

export default function OnboardingCuiPage() {
    const {
        user,
        firstName,
        digits,
        isLoading,
        error,
        inputRefs,
        isComplete,
        handleChange,
        handleKeyDown,
        handlePaste,
        handleSubmit,
        dict,
    } = useOnboardingCui();

    return (
        <div className='flex min-h-screen items-center justify-center bg-background px-4 py-8 sm:px-6 lg:px-8'>
            <SEO title={dict.seo.title} description={dict.seo.description} />

            <div className='absolute inset-0 z-0 pointer-events-none overflow-hidden opacity-20'>
                <div className='absolute top-0 left-1/2 -translate-x-1/2 size-200 rounded-full bg-primary/10 blur-[120px] dark:bg-primary/20' />
            </div>

            <div className='relative z-10 w-full max-w-md animate-reveal-soft'>
                <div className='mb-6 sm:mb-8 flex justify-center'>
                    <BrandLogo showTagline={false} className='scale-100 sm:scale-110' />
                </div>

                <div className='rounded-3xl border border-border/60 bg-surface/80 p-5 shadow-2xl backdrop-blur-xl sm:p-10'>
                    <div className='mb-6 sm:mb-8 text-center'>
                        <div className='mx-auto mb-4 flex size-10 sm:size-12 items-center justify-center rounded-full bg-primary/10 text-primary'>
                            <IdCard className='size-5 sm:size-6' />
                        </div>
                        <h2 className='font-display text-xl font-extrabold tracking-tight text-foreground sm:text-3xl'>
                            {dict.title.replace('{name}', firstName)}
                        </h2>
                        <p className='mt-2 sm:mt-3 text-xs sm:text-sm leading-relaxed text-muted-foreground'>
                            {dict.subtitle}
                        </p>
                    </div>

                    <form onSubmit={handleSubmit} className='space-y-6 sm:space-y-8'>
                        <div>
                            <label className='block text-center text-xs sm:text-sm font-semibold text-foreground mb-3 sm:mb-4'>
                                {dict.label}
                            </label>

                            <div className='flex justify-between gap-1.5 sm:gap-2 md:gap-3'>
                                {digits.map((digit, index) => (
                                    <input
                                        key={index}
                                        ref={(el) => {
                                            inputRefs.current[index] = el;
                                        }}
                                        type='text'
                                        inputMode='numeric'
                                        pattern='\d*'
                                        maxLength={1}
                                        value={digit}
                                        onChange={(e) => handleChange(index, e.target.value)}
                                        onKeyDown={(e) => handleKeyDown(index, e)}
                                        onPaste={handlePaste}
                                        disabled={isLoading}
                                        className={`w-full min-w-0 h-12 sm:h-14 sm:aspect-square rounded-lg sm:rounded-xl border-2 text-center text-lg sm:text-2xl font-extrabold transition-all focus:outline-none focus:ring-4
                                            ${
                                                error
                                                    ? 'border-destructive/50 bg-destructive/5 text-destructive focus:border-destructive focus:ring-destructive/20'
                                                    : 'border-border bg-background text-foreground focus:border-primary focus:ring-primary/20'
                                            }
                                        `}
                                    />
                                ))}
                            </div>

                            {error && (
                                <div className='mt-4 flex items-start justify-center gap-2 text-xs sm:text-sm font-medium text-destructive animate-reveal-soft'>
                                    <AlertCircle className='mt-0.5 size-3.5 sm:size-4 shrink-0' />
                                    <p>{error}</p>
                                </div>
                            )}
                        </div>

                        <div className='flex items-start gap-3 rounded-xl border border-amber-500/20 bg-amber-500/10 p-4 text-sm text-amber-600 dark:text-amber-500 animate-reveal-soft'>
                            <Info className='mt-0.5 size-4 shrink-0' />
                            <p className='leading-relaxed'>{dict.warning}</p>
                        </div>

                        <Button
                            type='submit'
                            size='lg'
                            disabled={isLoading || !isComplete}
                            className='w-full h-11 sm:h-12 rounded-xl text-sm sm:text-base font-bold shadow-md transition-all hover:scale-[1.02] active:scale-95'
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className='mr-2 size-4 sm:size-5 animate-spin' />
                                    {dict.loading}
                                </>
                            ) : (
                                <>
                                    {dict.button}
                                    <ArrowRight className='ml-2 size-4 sm:size-5 transition-transform group-hover:translate-x-1' />
                                </>
                            )}
                        </Button>
                    </form>
                </div>

                {user && (
                    <div className='mt-4 sm:mt-6 flex items-center justify-center gap-2 sm:gap-3 text-xs sm:text-sm text-muted-foreground'>
                        <img
                            src={user.picture_url}
                            alt='Tu foto de perfil'
                            className='size-5 sm:size-6 rounded-full border border-border'
                            referrerPolicy='no-referrer'
                        />
                        <span>
                            Vinculado como <strong>{user.email}</strong>
                        </span>
                    </div>
                )}
            </div>
        </div>
    );
}
