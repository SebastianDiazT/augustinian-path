export const ES_UI = {
    brand: {
        name: 'Ruta Agustina',
        tagline: 'Planificación académica',
    },
    navigation: {
        login: 'Iniciar sesión',
        loginMobile: 'Ingresar',
    },
    marketing: {
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
                contact: 'Contacto',
            },
            legal: {
                title: 'Legal',
                privacy: 'Privacidad',
                terms: 'Términos',
            },
        },
    },
    legal: {
        disclaimer:
            'Aviso de Independencia: Ruta Agustina es un proyecto creado por estudiantes. No representa oficialmente a la Universidad Nacional de San Agustín (UNSA) ni reemplaza sus sistemas oficiales.',
        copyright: '© {year} Ruta Agustina. Todos los derechos reservados.',
    },
} as const;
