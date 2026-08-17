import { CheckCircle2, Lock, Unlock } from 'lucide-react';
import { ES_UI } from '@/locales/es';

const NODE_STYLES = {
    done: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400/80 shadow-[0_0_15px_rgba(16,185,129,0.1)]',
    current:
        'border-primary/60 bg-primary/20 text-primary shadow-[0_0_40px_rgba(var(--primary),0.25)]',
    locked: 'border-foreground/20 bg-foreground/10 text-foreground/60',
};

const NODE_ICONS = {
    done: <CheckCircle2 className='size-4' />,
    current: <Unlock className='size-4' />,
    locked: <Lock className='size-4' />,
};

function BackgroundNode({
    status,
    title,
    subtitle,
}: {
    status: 'done' | 'current' | 'locked';
    title: string;
    subtitle: string;
}) {
    return (
        <div
            className={`flex w-56 flex-col gap-1.5 rounded-2xl border p-4 backdrop-blur-md transition-transform duration-700 hover:scale-105 ${NODE_STYLES[status]}`}
        >
            <div className='flex items-center gap-2'>
                {NODE_ICONS[status]}
                <span className='text-[10px] font-extrabold uppercase tracking-widest opacity-90'>
                    {subtitle}
                </span>
            </div>
            <p className='truncate text-sm font-bold'>{title}</p>
        </div>
    );
}

export function LoginBackgroundMesh() {
    const dict = ES_UI.auth.login.previewWidget;

    return (
        <div
            className='absolute inset-0 z-0 flex items-center justify-center overflow-hidden pointer-events-none select-none opacity-70 dark:opacity-50'
            style={{
                maskImage: 'radial-gradient(circle at center, black 40%, transparent 100%)',
                WebkitMaskImage: 'radial-gradient(circle at center, black 40%, transparent 100%)',
            }}
        >
            <div className='relative flex w-275 justify-between scale-[0.65] sm:scale-90 md:scale-110 lg:scale-[1.35] rotate-[-4deg] transition-transform duration-1000'>
                <svg className='absolute inset-0 size-full overflow-visible' style={{ zIndex: -1 }}>
                    <g
                        stroke='currentColor'
                        className='text-emerald-500/50'
                        strokeWidth='3'
                        fill='none'
                        strokeDasharray='6 6'
                    >
                        <path d='M 224 42 C 258 42, 258 42, 292 42' />
                        <path d='M 224 174 C 258 174, 258 42, 292 42' />
                        <path d='M 224 174 C 258 174, 258 174, 292 174' />
                        <path d='M 224 306 C 258 306, 258 174, 292 174' />
                        <path d='M 224 306 C 258 306, 258 306, 292 306' />
                    </g>
                    <g
                        stroke='currentColor'
                        className='text-primary/50'
                        strokeWidth='3'
                        fill='none'
                        strokeDasharray='6 6'
                    >
                        <path d='M 516 42 C 550 42, 550 42, 584 42' />
                        <path d='M 516 42 C 550 42, 550 174, 584 174' />
                        <path d='M 516 174 C 550 174, 550 174, 584 174' />
                        <path d='M 516 306 C 550 306, 550 174, 584 174' />
                        <path d='M 516 306 C 550 306, 550 306, 584 306' />
                    </g>
                    <g
                        stroke='currentColor'
                        className='text-foreground/20'
                        strokeWidth='3'
                        fill='none'
                    >
                        <path d='M 808 42 C 842 42, 842 42, 876 42' />
                        <path d='M 808 174 C 842 174, 842 42, 876 42' />
                        <path d='M 808 174 C 842 174, 842 174, 876 174' />
                        <path d='M 808 174 C 842 174, 842 306, 876 306' />
                        <path d='M 808 306 C 842 306, 842 306, 876 306' />
                    </g>
                </svg>

                <div className='flex flex-col gap-12'>
                    <BackgroundNode
                        status='done'
                        title={dict.nodes.done1}
                        subtitle={dict.status.done}
                    />
                    <BackgroundNode
                        status='done'
                        title={dict.nodes.done2}
                        subtitle={dict.status.done}
                    />
                    <BackgroundNode
                        status='done'
                        title={dict.nodes.done3}
                        subtitle={dict.status.done}
                    />
                </div>

                <div className='flex flex-col gap-12'>
                    <BackgroundNode
                        status='current'
                        title={dict.nodes.current1}
                        subtitle={dict.status.current}
                    />
                    <BackgroundNode
                        status='current'
                        title={dict.nodes.current2}
                        subtitle={dict.status.current}
                    />
                    <BackgroundNode
                        status='current'
                        title={dict.nodes.current3}
                        subtitle={dict.status.current}
                    />
                </div>

                <div className='flex flex-col gap-12'>
                    <BackgroundNode
                        status='locked'
                        title={dict.nodes.locked1}
                        subtitle={dict.status.locked}
                    />
                    <BackgroundNode
                        status='locked'
                        title={dict.nodes.locked2}
                        subtitle={dict.status.locked}
                    />
                    <BackgroundNode
                        status='locked'
                        title={dict.nodes.locked3}
                        subtitle={dict.status.locked}
                    />
                </div>

                <div className='flex flex-col gap-12'>
                    <BackgroundNode
                        status='locked'
                        title={dict.nodes.locked4}
                        subtitle={dict.status.locked}
                    />
                    <BackgroundNode
                        status='locked'
                        title={dict.nodes.locked5}
                        subtitle={dict.status.locked}
                    />
                    <BackgroundNode
                        status='locked'
                        title={dict.nodes.locked6}
                        subtitle={dict.status.locked}
                    />
                </div>
            </div>
        </div>
    );
}
