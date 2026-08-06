import {
    PublicDocumentLayout,
    type PublicDocumentSection,
} from '@/components/layout/public-document-layout';
import { projectConfig } from '@/config/project';

const sections: PublicDocumentSection[] = [
    {
        id: 'access-help',
        title: 'Problemas de acceso',
        content: (
            <>
                <p>
                    El acceso está limitado a cuentas institucionales admitidas por la
                    plataforma.
                </p>

                <ul className='list-disc space-y-2 pl-5'>
                    <li>Comprueba que elegiste la cuenta institucional correcta.</li>
                    <li>Permite las cookies necesarias para mantener la sesión.</li>
                    <li>Intenta cerrar y volver a abrir el navegador.</li>
                    <li>
                        Si el problema continúa, incluye el mensaje de error al
                        contactarnos.
                    </li>
                </ul>
            </>
        ),
    },
    {
        id: 'planning-help',
        title: 'Planificación académica',
        content: (
            <p>
                Recuerda que Ruta Agustina es una herramienta de apoyo. Verifica siempre
                cursos, horarios, prerrequisitos, vacantes y procedimientos mediante los
                canales oficiales correspondientes.
            </p>
        ),
    },
    {
        id: 'privacy-help',
        title: 'Privacidad y datos personales',
        content: (
            <p>
                Puedes solicitar información, rectificación o eliminación de tus datos
                enviando un mensaje desde una cuenta que permita comprobar tu identidad.
            </p>
        ),
    },
    {
        id: 'security',
        title: 'Reportar un problema de seguridad',
        content: (
            <>
                <p>
                    Si encuentras una posible vulnerabilidad, descríbela de forma
                    responsable y evita acceder, modificar o divulgar información de
                    otros usuarios.
                </p>

                <p>
                    No incluyas contraseñas, cookies, códigos de autenticación ni otros
                    secretos en el mensaje.
                </p>
            </>
        ),
    },
    {
        id: 'contact',
        title: 'Contacto',
        content: (
            <>
                <p>Para soporte, privacidad o reportes de seguridad, escribe a:</p>

                <a
                    href={`mailto:${projectConfig.supportEmail}?subject=Soporte%20Ruta%20Agustina`}
                    className='inline-flex min-h-11 items-center rounded-xl bg-primary px-5 py-3 text-sm font-extrabold text-primary-foreground transition-colors hover:bg-primary-hover focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary'
                >
                    {projectConfig.supportEmail}
                </a>

                <p>
                    Incluye una descripción clara, los pasos que realizaste y, si es
                    posible, una captura que no contenga información sensible.
                </p>
            </>
        ),
    },
];

export function SupportPage() {
    return (
        <PublicDocumentLayout
            eyebrow='Ayuda'
            title='Soporte de Ruta Agustina'
            description='Encuentra orientación para resolver problemas de acceso, planificación, privacidad o seguridad.'
            sections={sections}
        />
    );
}
