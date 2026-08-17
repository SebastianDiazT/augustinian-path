import { useAuthStore } from '@/store/auth-store';
import { SEO } from '@/components/seo';

export default function DashboardPage() {
    const { user } = useAuthStore();

    // Obtenemos el primer nombre y la escuela activa
    const firstName = user?.full_name.split(' ')[0] || 'Estudiante';
    const activeMembership = user?.school_memberships.find((m) => m.is_active);

    return (
        <div className='space-y-8 animate-reveal-soft'>
            <SEO title='Mi Panel' description='Resumen académico de Ruta Agustina' />

            {/* Cabecera de bienvenida */}
            <div>
                <h1 className='font-display text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl'>
                    Hola, {firstName} 👋
                </h1>
                <p className='mt-2 text-lg text-muted-foreground'>
                    Bienvenido a tu panel estudiantil. Aquí tienes el resumen de tu progreso.
                </p>
            </div>

            {/* Tarjeta de información de escuela */}
            <div className='rounded-3xl border border-border bg-surface p-6 sm:p-8 shadow-sm'>
                <h2 className='text-lg font-bold text-foreground'>Tu Escuela Profesional</h2>
                {activeMembership ? (
                    <div className='mt-4 grid gap-4 sm:grid-cols-2'>
                        <div className='rounded-xl bg-background p-4 border border-border/50'>
                            <p className='text-xs font-medium text-muted-foreground uppercase tracking-wider'>
                                Escuela
                            </p>
                            {/* Por ahora tenemos el ID, cuando hagamos populate desde el backend veremos el nombre real */}
                            <p className='mt-1 font-semibold text-foreground truncate'>
                                {activeMembership.school}
                            </p>
                        </div>
                        <div className='rounded-xl bg-background p-4 border border-border/50'>
                            <p className='text-xs font-medium text-muted-foreground uppercase tracking-wider'>
                                Plan de Estudios
                            </p>
                            <p className='mt-1 font-semibold text-foreground truncate'>
                                {activeMembership.curriculum_plan}
                            </p>
                        </div>
                    </div>
                ) : (
                    <p className='mt-4 text-sm text-muted-foreground'>
                        Cargando información de tu escuela...
                    </p>
                )}
            </div>

            {/* Área de trabajo para el futuro */}
            <div className='rounded-3xl border border-dashed border-border/60 p-12 text-center'>
                <p className='text-muted-foreground font-medium'>
                    Próximamente: Gráficas de avance, cursos disponibles y simulador de matrícula.
                </p>
            </div>
        </div>
    );
}
