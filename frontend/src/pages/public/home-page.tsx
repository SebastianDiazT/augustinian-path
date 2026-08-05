import { SessionStatus } from '@/features/auth/components/session-status';

export function HomePage() {
    return (
        <section id='access' className='scroll-mt-28'>
            <SessionStatus />
        </section>
    );
}
