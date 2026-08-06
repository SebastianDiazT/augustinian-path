import {
    PublicDocumentLayout,
    type PublicDocumentSection,
} from '@/components/layout/public-document-layout';
import { projectConfig } from '@/config/project';

const sections: PublicDocumentSection[] = [
    {
        id: 'acceptance',
        title: 'Aceptación de los términos',
        content: (
            <p>
                Al acceder o utilizar Ruta Agustina aceptas estos términos. Si no estás
                de acuerdo, debes abstenerte de utilizar el servicio.
            </p>
        ),
    },
    {
        id: 'independence',
        title: 'Naturaleza independiente',
        content: (
            <>
                <p>
                    Ruta Agustina es una herramienta independiente de apoyo a la
                    planificación académica.
                </p>

                <p>
                    No es un sistema oficial de matrícula, no representa a la
                    Universidad Nacional de San Agustín y no reemplaza la información,
                    decisiones o procedimientos de las autoridades universitarias.
                </p>
            </>
        ),
    },
    {
        id: 'access',
        title: 'Acceso y cuenta',
        content: (
            <ul className='list-disc space-y-2 pl-5'>
                <li>
                    El acceso se realiza mediante una cuenta institucional admitida.
                </li>
                <li>Debes mantener el control y la seguridad de tu cuenta externa.</li>
                <li>
                    No debes intentar acceder a información o funciones para las que no
                    tienes autorización.
                </li>
                <li>
                    Podemos restringir el acceso ante usos abusivos, fraudulentos o
                    contrarios a estos términos.
                </li>
            </ul>
        ),
    },
    {
        id: 'academic-information',
        title: 'Información académica',
        content: (
            <>
                <p>
                    La información mostrada busca ayudarte a explorar alternativas y
                    organizar una planificación personal.
                </p>

                <p>
                    Debes contrastar cursos, horarios, requisitos, disponibilidad y
                    cualquier otra información relevante con los canales oficiales antes
                    de tomar decisiones académicas o realizar una matrícula.
                </p>
            </>
        ),
    },
    {
        id: 'acceptable-use',
        title: 'Uso permitido',
        content: (
            <>
                <p>Puedes utilizar la plataforma para fines personales y académicos.</p>

                <p>No está permitido:</p>

                <ul className='list-disc space-y-2 pl-5'>
                    <li>Interferir con la seguridad o disponibilidad del servicio.</li>
                    <li>Automatizar solicitudes de manera abusiva.</li>
                    <li>Suplantar identidades o compartir acceso no autorizado.</li>
                    <li>Extraer, alterar o divulgar datos de otros usuarios.</li>
                    <li>Utilizar la plataforma con fines ilícitos.</li>
                </ul>
            </>
        ),
    },
    {
        id: 'availability',
        title: 'Disponibilidad y cambios',
        content: (
            <p>
                El servicio puede modificarse, suspenderse o presentar interrupciones
                durante mantenimiento, pruebas o incidentes técnicos. Procuraremos
                mantenerlo disponible, pero no garantizamos funcionamiento
                ininterrumpido.
            </p>
        ),
    },
    {
        id: 'responsibility',
        title: 'Responsabilidad',
        content: (
            <p>
                Ruta Agustina no garantiza que una planificación genere vacantes,
                matrícula, aprobación de cursos o resultados académicos específicos.
                Cada usuario es responsable de verificar la información y tomar sus
                propias decisiones, dentro de los límites permitidos por la legislación
                aplicable.
            </p>
        ),
    },
    {
        id: 'termination',
        title: 'Suspensión y finalización',
        content: (
            <p>
                Podemos suspender cuentas cuando sea necesario para proteger a los
                usuarios, investigar abusos o mantener la seguridad. También puedes
                solicitar la eliminación de tu información escribiendo a{' '}
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
    {
        id: 'changes',
        title: 'Cambios a estos términos',
        content: (
            <p>
                Podemos actualizar estos términos para reflejar cambios funcionales,
                técnicos o normativos. La versión vigente será la publicada en esta
                página.
            </p>
        ),
    },
];

export function TermsPage() {
    return (
        <PublicDocumentLayout
            eyebrow='Condiciones de uso'
            title='Términos de servicio'
            description='Establecen las condiciones para utilizar Ruta Agustina y aclaran el alcance independiente de la plataforma.'
            sections={sections}
        />
    );
}
