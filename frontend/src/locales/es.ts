export const ES_UI = {
    brand: {
        name: 'Ruta Agustina',
        tagline: 'Planificación académica',
    },
    common: {
        loading: 'Cargando plataforma...',
        backToHome: 'Volver al inicio',
        backToLogin: 'Ir a iniciar sesión',
    },
    errors: {
        notFoundCode: '404',
        notFoundTitle: 'Página no encontrada',
        notFoundDescription:
            'La página que buscas no existe, ha sido movida o la URL es incorrecta.',
        forbiddenCode: '403',
        forbiddenTitle: 'Acceso denegado',
        forbiddenDescription:
            'No tienes los permisos necesarios para ver esta página o tu sesión ha expirado. Por favor, inicia sesión con tu cuenta institucional.',
    },
    navigation: {
        login: 'Iniciar sesión',
        loginMobile: 'Ingresar',
    },
    marketing: {
        seo: {
            title: 'Planificador Académico',
            description:
                'Organiza tus cursos, explora tu malla curricular y construye un horario universitario sin cruces. Una herramienta exclusiva para estudiantes agustinos.',
        },
        heroBadge: 'Exclusivo para estudiantes agustinos',
        heroTitle: 'Planifica tu futuro académico',
        heroTitleHighlight: 'con claridad',
        heroSubtitle:
            'Organiza tus cursos, explora tu malla curricular y construye un horario que se adapte a tus objetivos.',
        heroCta: 'Iniciar sesión',
        heroSecondaryCta: 'Explorar funciones',
        heroDisclaimer:
            'Accede con tu cuenta institucional. Si es tu primera vez, crearemos tu cuenta automáticamente.',

        preview: {
            badge: 'Vista previa',
            title: 'Planificación {year}',
            status: 'Sin conflictos',
            selectedCourses: 'Cursos seleccionados',
            schedule: 'Mi horario',
            progress: 'Progreso del plan',
            readyMessage: '{count} cursos listos para generar tu horario',
            credits: '{count} créditos',
            hours: '{count} horas',
        },

        featuresTitle: 'Todo en un solo lugar',
        featuresSubtitle:
            'Diseñamos las herramientas exactas que necesitas para dejar de pelear con hojas de cálculo y enfocarte en lo importante: estudiar.',
        features: {
            visualize: {
                title: 'Visualiza tu malla',
                description:
                    'Identifica los cursos que ya aprobaste, los prerrequisitos que te faltan y descubre exactamente qué materias estás habilitado a llevar este semestre.',
            },
            schedules: {
                title: 'Horarios sin cruces',
                description:
                    'Genera combinaciones automáticas y compara diferentes escenarios antes de tu matrícula oficial.',
            },
            simulator: {
                title: 'Simulador de notas',
                description:
                    'Calcula exactamente cuánto necesitas sacar en la tercera fase para aprobar el curso sin sorpresas de última hora.',
            },
        },

        bottomCta: {
            title: '¿Listo para tomar el control de tu semestre?',
            description:
                'Deja de adivinar qué cursos puedes llevar. Accede ahora con tu correo institucional y arma tu horario en minutos.',
            button: 'Ingresar a la plataforma',
        },
    },
    footer: {
        description:
            'Una plataforma diseñada para simplificar tu planificación académica, dándote visibilidad completa sobre tu ruta universitaria.',
        studentProject: 'Proyecto estudiantil independiente',
        columns: {
            platform: {
                title: 'Plataforma',
                features: 'Funciones',
            },
            support: {
                title: 'Soporte',
                helpCenter: 'Centro de ayuda',
                contact: 'Contacto de soporte',
            },
            legal: {
                title: 'Legal',
                privacy: 'Política de privacidad',
                terms: 'Términos de servicio',
            },
        },
    },
    legal: {
        disclaimer:
            'Aviso de Independencia: Ruta Agustina es un proyecto creado por estudiantes. No representa oficialmente a la Universidad Nacional de San Agustín (UNSA) ni reemplaza sus sistemas oficiales.',
        copyright: '© {year} Ruta Agustina. Todos los derechos reservados.',
    },
    privacyPage: {
        eyebrow: 'Privacidad',
        title: 'Política de privacidad',
        description:
            'Explica qué información utiliza Ruta Agustina, para qué la necesita y qué opciones tienes sobre tus datos.',
        sections: {
            responsible: {
                title: 'Responsable y alcance',
                p1: 'Ruta Agustina es un proyecto independiente de planificación académica. No representa oficialmente a la Universidad Nacional de San Agustín ni actúa en su nombre.',
                p2: 'Para consultas relacionadas con privacidad o tratamiento de datos, puedes escribir a',
            },
            collectedData: {
                title: 'Datos que tratamos',
                p1: 'Cuando accedes con tu cuenta institucional podemos recibir y conservar:',
                list: [
                    'Identificador de usuario.',
                    'Nombre y apellidos asociados a la cuenta.',
                    'Correo electrónico institucional.',
                    'Roles y permisos dentro de la plataforma.',
                    'Información de sesión y datos técnicos necesarios para seguridad y funcionamiento.',
                    'Información académica que ingreses voluntariamente al utilizar las herramientas de planificación.',
                ],
                p2: 'No solicitamos tu contraseña de Google ni tenemos acceso a ella.',
            },
            purposes: {
                title: 'Para qué utilizamos los datos',
                list: [
                    'Autenticar tu identidad y mantener tu sesión.',
                    'Comprobar que utilizas una cuenta institucional admitida.',
                    'Administrar roles y permisos.',
                    'Guardar y mostrar tu planificación académica.',
                    'Prevenir abusos, errores y accesos no autorizados.',
                    'Atender consultas y solicitudes de soporte.',
                    'Mejorar la estabilidad y seguridad del servicio.',
                ],
            },
            serviceProviders: {
                title: 'Servicios tecnológicos y transferencias',
                p1: 'Para operar la plataforma utilizamos servicios especializados de autenticación, alojamiento, almacenamiento de datos y caché.',
                p2: 'Estos servicios pueden procesar información técnica o personal únicamente en la medida necesaria para prestar sus funciones. Algunos recursos tecnológicos podrían encontrarse fuera del Perú.',
                p3: 'No vendemos tus datos personales ni los utilizamos para publicidad comercial.',
            },
            retention: {
                title: 'Conservación de información',
                p1: 'Conservamos la información mientras tu cuenta permanezca activa o mientras sea necesaria para proporcionar y proteger el servicio.',
                p2: 'Puedes solicitar la eliminación de tus datos por correo. Algunos registros técnicos o copias de respaldo podrían conservarse temporalmente por razones de seguridad, integridad o cumplimiento de obligaciones aplicables.',
            },
            rights: {
                title: 'Tus derechos',
                p1: 'Puedes solicitar acceso, rectificación, cancelación u oposición al tratamiento de tus datos personales, así como formular consultas relacionadas con su utilización.',
                p2: 'Envía tu solicitud desde una dirección que permita verificar tu identidad a',
                p3: 'También puedes consultar la',
                linkArco: 'orientación oficial sobre derechos ARCO',
            },
            security: {
                title: 'Seguridad',
                p1: 'Aplicamos medidas técnicas y organizativas razonables para proteger la información. Sin embargo, ningún sistema conectado a internet puede garantizar seguridad absoluta.',
            },
            changes: {
                title: 'Cambios a esta política',
                p1: 'Podemos actualizar esta política cuando cambien las funcionalidades, obligaciones aplicables o prácticas del proyecto. La fecha mostrada al inicio identifica la versión vigente.',
            },
        },
    },
    supportPage: {
        eyebrow: 'Ayuda',
        title: 'Soporte de Ruta Agustina',
        description:
            'Encuentra orientación para resolver problemas de acceso, planificación, privacidad o seguridad.',
        sections: {
            accessHelp: {
                title: 'Problemas de acceso',
                p1: 'El acceso está limitado a cuentas institucionales admitidas por la plataforma.',
                list: [
                    'Comprueba que elegiste la cuenta institucional correcta.',
                    'Permite las cookies necesarias para mantener la sesión.',
                    'Intenta cerrar y volver a abrir el navegador.',
                    'Si el problema continúa, incluye el mensaje de error al contactarnos.',
                ],
            },
            planningHelp: {
                title: 'Planificación académica',
                p1: 'Recuerda que Ruta Agustina es una herramienta de apoyo. Verifica siempre cursos, horarios, prerrequisitos, vacantes y procedimientos mediante los canales oficiales correspondientes.',
            },
            privacyHelp: {
                title: 'Privacidad y datos personales',
                p1: 'Puedes solicitar información, rectificación o eliminación de tus datos enviando un mensaje desde una cuenta que permita comprobar tu identidad.',
            },
            security: {
                title: 'Reportar un problema de seguridad',
                p1: 'Si encuentras una posible vulnerabilidad, descríbela de forma responsable y evita acceder, modificar o divulgar información de otros usuarios.',
                p2: 'No incluyas contraseñas, cookies, códigos de autenticación ni otros secretos en el mensaje.',
            },
            contact: {
                title: 'Contacto',
                p1: 'Para soporte, privacidad o reportes de seguridad, escribe a:',
                p2: 'Incluye una descripción clara, los pasos que realizaste y, si es posible, una captura que no contenga información sensible.',
            },
        },
    },
    termsPage: {
        eyebrow: 'Condiciones de uso',
        title: 'Términos de servicio',
        description:
            'Establecen las condiciones para utilizar Ruta Agustina y aclaran el alcance independiente de la plataforma.',
        sections: {
            acceptance: {
                title: 'Aceptación de los términos',
                p1: 'Al acceder o utilizar Ruta Agustina aceptas estos términos. Si no estás de acuerdo, debes abstenerte de utilizar el servicio.',
            },
            independence: {
                title: 'Naturaleza independiente',
                p1: 'Ruta Agustina es una herramienta independiente de apoyo a la planificación académica.',
                p2: 'No es un sistema oficial de matrícula, no representa a la Universidad Nacional de San Agustín y no reemplaza la información, decisiones o procedimientos de las autoridades universitarias.',
            },
            access: {
                title: 'Acceso y cuenta',
                list: [
                    'El acceso se realiza mediante una cuenta institucional admitida.',
                    'Debes mantener el control y la seguridad de tu cuenta externa.',
                    'No debes intentar acceder a información o funciones para las que no tienes autorización.',
                    'Podemos restringir el acceso ante usos abusivos, fraudulentos o contrarios a estos términos.',
                ],
            },
            academicInformation: {
                title: 'Información académica',
                p1: 'La información mostrada busca ayudarte a explorar alternativas y organizar una planificación personal.',
                p2: 'Debes contrastar cursos, horarios, requisitos, disponibilidad y cualquier otra información relevante con los canales oficiales antes de tomar decisiones académicas o realizar una matrícula.',
            },
            acceptableUse: {
                title: 'Uso permitido',
                p1: 'Puedes utilizar la plataforma para fines personales y académicos.',
                p2: 'No está permitido:',
                list: [
                    'Interferir con la seguridad o disponibilidad del servicio.',
                    'Automatizar solicitudes de manera abusiva.',
                    'Suplantar identidades o compartir acceso no autorizado.',
                    'Extraer, alterar o divulgar datos de otros usuarios.',
                    'Utilizar la plataforma con fines ilícitos.',
                ],
            },
            availability: {
                title: 'Disponibilidad y cambios',
                p1: 'El servicio puede modificarse, suspenderse o presentar interrupciones durante mantenimiento, pruebas o incidentes técnicos. Procuraremos mantenerlo disponible, pero no garantizamos funcionamiento ininterrumpido.',
            },
            responsibility: {
                title: 'Responsabilidad',
                p1: 'Ruta Agustina no garantiza que una planificación genere vacantes, matrícula, aprobación de cursos o resultados académicos específicos. Cada usuario es responsable de verificar la información y tomar sus propias decisiones, dentro de los límites permitidos por la legislación aplicable.',
            },
            termination: {
                title: 'Suspensión y finalización',
                p1: 'Podemos suspender cuentas cuando sea necesario para proteger a los usuarios, investigar abusos o mantener la seguridad. También puedes solicitar la eliminación de tu información escribiendo a',
            },
            changes: {
                title: 'Cambios a estos términos',
                p1: 'Podemos actualizar estos términos para reflejar cambios funcionales, técnicos o normativos. La versión vigente será la publicada en esta página.',
            },
        },
    },
} as const;
