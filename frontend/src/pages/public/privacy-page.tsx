import {
    PublicDocumentLayout,
    type PublicDocumentSection,
} from '@/components/layout/public-document-layout';
import { projectConfig } from '@/config/project';

const sections: PublicDocumentSection[] = [
    {
        id: 'responsible',
        title: 'Responsable y alcance',
        content: (
            <>
                <p>
                    Ruta Agustina es un proyecto independiente de planificación
                    académica. No representa oficialmente a la Universidad Nacional de
                    San Agustín ni actúa en su nombre.
                </p>

                <p>
                    Para consultas relacionadas con privacidad o tratamiento de datos,
                    puedes escribir a{' '}
                    <a
                        href={`mailto:${projectConfig.supportEmail}`}
                        className='font-bold text-primary underline-offset-4 hover:underline'
                    >
                        {projectConfig.supportEmail}
                    </a>
                    .
                </p>
            </>
        ),
    },
    {
        id: 'collected-data',
        title: 'Datos que tratamos',
        content: (
            <>
                <p>
                    Cuando accedes con tu cuenta institucional podemos recibir y
                    conservar:
                </p>

                <ul className='list-disc space-y-2 pl-5'>
                    <li>Identificador de usuario.</li>
                    <li>Nombre y apellidos asociados a la cuenta.</li>
                    <li>Correo electrónico institucional.</li>
                    <li>Roles y permisos dentro de la plataforma.</li>
                    <li>
                        Información de sesión y datos técnicos necesarios para seguridad
                        y funcionamiento.
                    </li>
                    <li>
                        Información académica que ingreses voluntariamente al utilizar
                        las herramientas de planificación.
                    </li>
                </ul>

                <p>No solicitamos tu contraseña de Google ni tenemos acceso a ella.</p>
            </>
        ),
    },
    {
        id: 'purposes',
        title: 'Para qué utilizamos los datos',
        content: (
            <ul className='list-disc space-y-2 pl-5'>
                <li>Autenticar tu identidad y mantener tu sesión.</li>
                <li>Comprobar que utilizas una cuenta institucional admitida.</li>
                <li>Administrar roles y permisos.</li>
                <li>Guardar y mostrar tu planificación académica.</li>
                <li>Prevenir abusos, errores y accesos no autorizados.</li>
                <li>Atender consultas y solicitudes de soporte.</li>
                <li>Mejorar la estabilidad y seguridad del servicio.</li>
            </ul>
        ),
    },
    {
        id: 'service-providers',
        title: 'Servicios tecnológicos y transferencias',
        content: (
            <>
                <p>
                    Para operar la plataforma utilizamos servicios especializados de
                    autenticación, alojamiento, almacenamiento de datos y caché.
                </p>

                <p>
                    Estos servicios pueden procesar información técnica o personal
                    únicamente en la medida necesaria para prestar sus funciones.
                    Algunos recursos tecnológicos podrían encontrarse fuera del Perú.
                </p>

                <p>
                    No vendemos tus datos personales ni los utilizamos para publicidad
                    comercial.
                </p>
            </>
        ),
    },
    {
        id: 'retention',
        title: 'Conservación de información',
        content: (
            <>
                <p>
                    Conservamos la información mientras tu cuenta permanezca activa o
                    mientras sea necesaria para proporcionar y proteger el servicio.
                </p>

                <p>
                    Puedes solicitar la eliminación de tus datos por correo. Algunos
                    registros técnicos o copias de respaldo podrían conservarse
                    temporalmente por razones de seguridad, integridad o cumplimiento de
                    obligaciones aplicables.
                </p>
            </>
        ),
    },
    {
        id: 'rights',
        title: 'Tus derechos',
        content: (
            <>
                <p>
                    Puedes solicitar acceso, rectificación, cancelación u oposición al
                    tratamiento de tus datos personales, así como formular consultas
                    relacionadas con su utilización.
                </p>

                <p>
                    Envía tu solicitud desde una dirección que permita verificar tu
                    identidad a{' '}
                    <a
                        href={`mailto:${projectConfig.supportEmail}?subject=Solicitud%20de%20privacidad`}
                        className='font-bold text-primary underline-offset-4 hover:underline'
                    >
                        {projectConfig.supportEmail}
                    </a>
                    .
                </p>

                <p>
                    También puedes consultar la{' '}
                    <a
                        href='https://www.gob.pe/9270-que-son-los-derechos-arco'
                        target='_blank'
                        rel='noreferrer'
                        className='font-bold text-primary underline-offset-4 hover:underline'
                    >
                        orientación oficial sobre derechos ARCO
                    </a>
                    .
                </p>
            </>
        ),
    },
    {
        id: 'security',
        title: 'Seguridad',
        content: (
            <p>
                Aplicamos medidas técnicas y organizativas razonables para proteger la
                información. Sin embargo, ningún sistema conectado a internet puede
                garantizar seguridad absoluta.
            </p>
        ),
    },
    {
        id: 'changes',
        title: 'Cambios a esta política',
        content: (
            <p>
                Podemos actualizar esta política cuando cambien las funcionalidades,
                obligaciones aplicables o prácticas del proyecto. La fecha mostrada al
                inicio identifica la versión vigente.
            </p>
        ),
    },
];

export function PrivacyPage() {
    return (
        <PublicDocumentLayout
            eyebrow='Privacidad'
            title='Política de privacidad'
            description='Explica qué información utiliza Ruta Agustina, para qué la necesita y qué opciones tienes sobre tus datos.'
            sections={sections}
        />
    );
}
