import { GraduationCap, ArrowRight, Loader2, Clock, Info } from 'lucide-react';
import { ES_UI } from '@/locales/es';
import { SEO } from '@/components/seo';
import { BrandLogo } from '@/components/brand/brand-logo';
import { Button } from '@/components/ui/button';
import { useAuthStore } from '@/store/auth-store';
import { useOnboardingSchool } from '@/hooks/use-onboarding-school';
import { CustomSelect } from '@/components/ui/custom-select';

export default function OnboardingSchoolPage() {
    const { user } = useAuthStore();
    const dict = ES_UI.auth.onboarding.school;
    const firstName = user?.full_name.split(' ')[0] || 'Estudiante';

    const {
        areaOptions,
        filteredFaculties,
        filteredSchools,
        plans,
        selectedArea,
        selectedFaculty,
        selectedSchool,
        selectedPlan,
        isLoading,
        isPageLoading,
        hasPendingRequest,
        handleAreaChange,
        handleFacultyChange,
        handleSchoolChange,
        setSelectedPlan,
        submitRequest,
        handleManualRefresh,
    } = useOnboardingSchool();

    const facultyOptions = filteredFaculties.map((f) => ({ value: f.public_id, label: f.name }));
    const schoolOptions = filteredSchools.map((s) => ({ value: s.public_id, label: s.name }));
    const planOptions = plans.map((p) => ({ value: p.public_id, label: p.name }));

    const onSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        await submitRequest();
    };

    if (isPageLoading) {
        return (
            <div className='flex min-h-screen items-center justify-center bg-background'>
                <Loader2 className='size-8 animate-spin text-primary' />
            </div>
        );
    }

    return (
        <div className='flex min-h-screen items-center justify-center bg-background px-4 py-8 sm:px-6 lg:px-8 overflow-y-auto'>
            <SEO title={dict.seo.title} description={dict.seo.description} />

            <div className='fixed inset-0 z-0 pointer-events-none overflow-hidden opacity-20'>
                <div className='absolute top-0 left-1/2 -translate-x-1/2 size-200 rounded-full bg-primary/10 blur-[120px] dark:bg-primary/20' />
            </div>

            <div className='relative z-10 w-full max-w-xl animate-reveal-soft py-10'>
                <div className='mb-6 sm:mb-8 flex justify-center'>
                    <BrandLogo showTagline={false} className='scale-100 sm:scale-110' />
                </div>

                <div className='rounded-3xl border border-border/60 bg-surface/80 p-6 shadow-2xl backdrop-blur-xl sm:p-10'>
                    {hasPendingRequest ? (
                        <div className='text-center animate-reveal-soft py-8'>
                            <div className='mx-auto mb-6 flex size-16 items-center justify-center rounded-full bg-amber-500/10 text-amber-500 ring-8 ring-amber-500/5'>
                                <Clock className='size-8' />
                            </div>
                            <h2 className='font-display text-2xl font-extrabold tracking-tight text-foreground'>
                                {dict.pending.title}
                            </h2>
                            <p className='mt-4 text-sm leading-relaxed text-muted-foreground'>
                                {dict.pending.subtitle}
                            </p>

                            <Button
                                onClick={handleManualRefresh}
                                variant='outline'
                                className='mt-8 w-full h-12 rounded-xl font-bold'
                            >
                                {dict.pending.refreshBtn}
                            </Button>
                        </div>
                    ) : (
                        <>
                            <div className='mb-6 sm:mb-8 text-center'>
                                <div className='mx-auto mb-4 flex size-10 sm:size-12 items-center justify-center rounded-full bg-primary/10 text-primary'>
                                    <GraduationCap className='size-5 sm:size-6' />
                                </div>
                                <h2 className='font-display text-xl font-extrabold tracking-tight text-foreground sm:text-3xl'>
                                    {dict.title.replace('{name}', firstName)}
                                </h2>
                                <p className='mt-2 sm:mt-3 text-xs sm:text-sm leading-relaxed text-muted-foreground'>
                                    {dict.subtitle}
                                </p>
                            </div>

                            <form onSubmit={onSubmit} className='space-y-5'>
                                <div>
                                    <label
                                        htmlFor='select-area'
                                        className='block text-xs font-semibold text-foreground mb-2'
                                    >
                                        {dict.form.areaLabel}
                                    </label>
                                    <CustomSelect
                                        id='select-area'
                                        value={selectedArea}
                                        onChange={handleAreaChange}
                                        options={areaOptions}
                                        placeholder={dict.form.areaPlaceholder}
                                        disabled={isLoading}
                                    />
                                </div>

                                <div>
                                    <label
                                        htmlFor='select-faculty'
                                        className='block text-xs font-semibold text-foreground mb-2'
                                    >
                                        {dict.form.facultyLabel}
                                    </label>
                                    <CustomSelect
                                        id='select-faculty'
                                        value={selectedFaculty}
                                        onChange={handleFacultyChange}
                                        options={facultyOptions}
                                        placeholder={dict.form.facultyPlaceholder}
                                        disabled={!selectedArea || isLoading}
                                    />
                                </div>

                                <div>
                                    <label
                                        htmlFor='select-school'
                                        className='block text-xs font-semibold text-foreground mb-2'
                                    >
                                        {dict.form.schoolLabel}
                                    </label>
                                    <CustomSelect
                                        id='select-school'
                                        value={selectedSchool}
                                        onChange={handleSchoolChange}
                                        options={schoolOptions}
                                        placeholder={dict.form.schoolPlaceholder}
                                        disabled={!selectedFaculty || isLoading}
                                    />
                                </div>

                                <div>
                                    <label
                                        htmlFor='select-plan'
                                        className='block text-xs font-semibold text-foreground mb-2'
                                    >
                                        {dict.form.planLabel}
                                    </label>
                                    <CustomSelect
                                        id='select-plan'
                                        value={selectedPlan}
                                        onChange={setSelectedPlan}
                                        options={planOptions}
                                        placeholder={dict.form.planPlaceholder}
                                        disabled={
                                            !selectedSchool || isLoading || plans.length === 0
                                        }
                                    />
                                </div>

                                <div className='mt-2 flex items-start gap-3 rounded-xl border border-amber-500/20 bg-amber-500/10 p-4 text-sm text-amber-600 dark:text-amber-500 animate-reveal-soft'>
                                    <Info className='mt-0.5 size-4 shrink-0' />
                                    <p className='leading-relaxed'>{dict.warning}</p>
                                </div>

                                <Button
                                    type='submit'
                                    size='lg'
                                    disabled={isLoading || !selectedSchool || !selectedPlan}
                                    className='w-full h-11 sm:h-12 mt-6 rounded-xl text-sm sm:text-base font-bold shadow-md transition-transform hover:scale-[1.02] active:scale-95'
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
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
