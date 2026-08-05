import { SessionStatus } from '@/features/auth/components/session-status';
import { ThemeSelector } from '@/theme/theme-selector';

function App() {
    return (
        <main className='min-h-screen bg-background px-6 py-10 text-foreground transition-colors'>
            <div className='mx-auto max-w-5xl'>
                <SessionStatus />
                <ThemeSelector />
            </div>
        </main>
    );
}

export default App;
