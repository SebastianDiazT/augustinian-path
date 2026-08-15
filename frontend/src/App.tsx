import { BrowserRouter } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { AppRouter } from '@/app/router';
import { ScrollToTop } from '@/components/navigation/scroll-to-top';
import { Toaster } from './components/ui/sonner';

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || 'TU_CLIENT_ID_AQUI';

export default function App() {
    return (
        <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
            <BrowserRouter>
                <ScrollToTop />
                <AppRouter />
                <Toaster position='top-center' richColors />
            </BrowserRouter>
        </GoogleOAuthProvider>
    );
}
