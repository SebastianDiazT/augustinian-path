import {
    PublicDocumentLayout,
    type PublicDocumentSection,
} from '@/components/layout/public-document-layout';
import { projectConfig } from '@/config/project';
import { ES_UI } from '@/locales/es';
import { SEO } from '@/components/seo';

const dict = ES_UI.supportPage;

const sections: PublicDocumentSection[] = [
    {
        id: 'access-help',
        title: dict.sections.accessHelp.title,
        content: (
            <>
                <p>{dict.sections.accessHelp.p1}</p>
                <ul className='list-disc space-y-2 pl-5'>
                    {dict.sections.accessHelp.list.map((item, idx) => (
                        <li key={idx}>{item}</li>
                    ))}
                </ul>
            </>
        ),
    },
    {
        id: 'planning-help',
        title: dict.sections.planningHelp.title,
        content: <p>{dict.sections.planningHelp.p1}</p>,
    },
    {
        id: 'privacy-help',
        title: dict.sections.privacyHelp.title,
        content: <p>{dict.sections.privacyHelp.p1}</p>,
    },
    {
        id: 'security',
        title: dict.sections.security.title,
        content: (
            <>
                <p>{dict.sections.security.p1}</p>
                <p>{dict.sections.security.p2}</p>
            </>
        ),
    },
    {
        id: 'contact',
        title: dict.sections.contact.title,
        content: (
            <>
                <p>{dict.sections.contact.p1}</p>
                <a
                    href={`mailto:${projectConfig.supportEmail}?subject=Soporte%20Ruta%20Agustina`}
                    className='inline-flex min-h-11 items-center rounded-xl bg-primary px-5 py-3 text-sm font-extrabold text-primary-foreground transition-colors hover:bg-primary-hover focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary mt-2 mb-2'
                >
                    {projectConfig.supportEmail}
                </a>
                <p>{dict.sections.contact.p2}</p>
            </>
        ),
    },
];

export default function SupportPage() {
    return (
        <>
            <SEO title={dict.title} description={dict.description} />
            <PublicDocumentLayout
                eyebrow={dict.eyebrow}
                title={dict.title}
                description={dict.description}
                sections={sections}
            />
        </>
    );
}
