import {
    PublicDocumentLayout,
    type PublicDocumentSection,
} from '@/components/layout/public-document-layout';
import { projectConfig } from '@/config/project';

const sections: PublicDocumentSection[] = [
    {
        id: 'definition',
        title: 'Qué son las cookies',
        content: (
            <p>
                Las cookies son pequeños datos que el navegador conserva para mantener
                una sesión, recordar preferencias o permitir funciones de seguridad.
            </p>
        ),
    },
    {
        id: 'essential-cookies',
        title: 'Cookies técnicas utilizadas',
        content: (
            <>
                <p>
                    Ruta Agustina utiliza cookies necesarias para autenticación y
                    seguridad:
                </p>

                <div className='overflow-x-auto rounded-xl border border-border'>
                    <table className='w-full min-w-136 border-collapse text-left text-sm'>
                        <thead className='bg-surface-muted text-foreground'>
                            <tr>
                                <th className='px-4 py-3 font-extrabold'>Nombre</th>
                                <th className='px-4 py-3 font-extrabold'>Finalidad</th>
                                <th className='px-4 py-3 font-extrabold'>Tipo</th>
                            </tr>
                        </thead>

                        <tbody className='divide-y divide-border bg-surface'>
                            <tr>
                                <td className='px-4 py-3 font-mono text-xs'>
                                    sessionid
                                </td>
                                <td className='px-4 py-3'>
                                    Mantener la sesión autenticada.
                                </td>
                                <td className='px-4 py-3'>Esencial</td>
                            </tr>

                            <tr>
                                <td className='px-4 py-3 font-mono text-xs'>
                                    csrftoken
                                </td>
                                <td className='px-4 py-3'>
                                    Proteger solicitudes frente a falsificación.
                                </td>
                                <td className='px-4 py-3'>Esencial</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </>
        ),
    },
    {
        id: 'local-storage',
        title: 'Preferencias locales',
        content: (
            <p>
                La preferencia de tema claro, oscuro o del sistema se almacena
                localmente en tu navegador. Esta información no identifica tu cuenta ni
                se utiliza para seguimiento comercial.
            </p>
        ),
    },
    {
        id: 'non-essential',
        title: 'Analítica y publicidad',
        content: (
            <p>
                Actualmente no utilizamos cookies publicitarias, seguimiento comercial
                ni herramientas de analítica de terceros. Si esto cambia, actualizaremos
                esta política y evaluaremos los mecanismos de información o
                consentimiento necesarios.
            </p>
        ),
    },
    {
        id: 'management',
        title: 'Cómo administrar cookies',
        content: (
            <>
                <p>
                    Puedes borrar o bloquear cookies desde la configuración de tu
                    navegador.
                </p>

                <p>
                    Bloquear las cookies técnicas puede impedir el inicio de sesión o
                    provocar que algunas funciones de seguridad no operen correctamente.
                </p>
            </>
        ),
    },
    {
        id: 'contact',
        title: 'Consultas',
        content: (
            <p>
                Si tienes preguntas sobre el uso de cookies, escribe a{' '}
                <a
                    href={`mailto:${projectConfig.supportEmail}`}
                    className='font-bold text-primary underline-offset-4 hover:underline'
                >
                    {projectConfig.supportEmail}
                </a>
                .
            </p>
        ),
    },
];

export function CookiesPage() {
    return (
        <PublicDocumentLayout
            eyebrow='Tecnologías del navegador'
            title='Política de cookies'
            description='Describe las tecnologías necesarias para mantener sesiones, proteger solicitudes y recordar preferencias.'
            sections={sections}
        />
    );
}
