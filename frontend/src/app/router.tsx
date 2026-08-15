import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import PublicLayout from './layouts/public-layout';

// Páginas cargadas perezosamente (Lazy Loading)
const HomePage = lazy(() => import('@/pages/public/home-page'));
const LoginPage = lazy(() => import('@/pages/auth/login-page'));

// Componente temporal de carga
const PageLoader = () => (
    <div className='flex min-h-screen items-center justify-center text-muted-foreground'>
        Cargando plataforma...
    </div>
);

export function AppRouter() {
    return (
        <Suspense fallback={<PageLoader />}>
            <Routes>
                {/* RUTAS PÚBLICAS (Con Header y Footer) */}
                <Route element={<PublicLayout />}>
                    <Route path='/' element={<HomePage />} />
                </Route>

                {/* RUTAS SIN LAYOUT (Pantalla completa, ej: Login) */}
                <Route path='/login' element={<LoginPage />} />

                {/* RUTA 404 CATCH-ALL */}
                <Route
                    path='*'
                    element={
                        <div className='flex min-h-screen items-center justify-center'>
                            <h1 className='text-2xl font-bold'>404 - Ruta no encontrada</h1>
                        </div>
                    }
                />
            </Routes>
        </Suspense>
    );
}
