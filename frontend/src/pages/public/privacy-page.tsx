import {
    PublicDocumentLayout,
    type PublicDocumentSection,
} from '@/components/layout/public-document-layout';
import { projectConfig } from '@/config/project';
import { ES_UI } from '@/locales/es';
import { SEO } from '@/components/seo';

const dict = ES_UI.privacyPage;

const sections: PublicDocumentSection[] = [
    {
        id: 'responsible',
        title: dict.sections.responsible.title,
        content: (
            <>
                <p>{dict.sections.responsible.p1}</p>
                <p>
                    {dict.sections.responsible.p2}{' '}
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
        title: dict.sections.collectedData.title,
        content: (
            <>
                <p>{dict.sections.collectedData.p1}</p>
                <ul className='list-disc space-y-2 pl-5'>
                    {dict.sections.collectedData.list.map((item) => (
                        <li key={item}>{item}</li>
                    ))}
                </ul>
                <p>{dict.sections.collectedData.p2}</p>
            </>
        ),
    },
    {
        id: 'purposes',
        title: dict.sections.purposes.title,
        content: (
            <ul className='list-disc space-y-2 pl-5'>
                {dict.sections.purposes.list.map((item) => (
                    <li key={item}>{item}</li>
                ))}
            </ul>
        ),
    },
    {
        id: 'service-providers',
        title: dict.sections.serviceProviders.title,
        content: (
            <>
                <p>{dict.sections.serviceProviders.p1}</p>
                <p>{dict.sections.serviceProviders.p2}</p>
                <p>{dict.sections.serviceProviders.p3}</p>
            </>
        ),
    },
    {
        id: 'retention',
        title: dict.sections.retention.title,
        content: (
            <>
                <p>{dict.sections.retention.p1}</p>
                <p>{dict.sections.retention.p2}</p>
            </>
        ),
    },
    {
        id: 'rights',
        title: dict.sections.rights.title,
        content: (
            <>
                <p>{dict.sections.rights.p1}</p>
                <p>
                    {dict.sections.rights.p2}{' '}
                    <a
                        href={`mailto:${projectConfig.supportEmail}?subject=Solicitud%20de%20privacidad`}
                        className='font-bold text-primary underline-offset-4 hover:underline'
                    >
                        {projectConfig.supportEmail}
                    </a>
                    .
                </p>
                <p>
                    {dict.sections.rights.p3}{' '}
                    <a
                        href='https://www.gob.pe/9270-que-son-los-derechos-arco'
                        target='_blank'
                        rel='noreferrer'
                        className='font-bold text-primary underline-offset-4 hover:underline'
                    >
                        {dict.sections.rights.linkArco}
                    </a>
                    .
                </p>
            </>
        ),
    },
    {
        id: 'security',
        title: dict.sections.security.title,
        content: <p>{dict.sections.security.p1}</p>,
    },
    {
        id: 'changes',
        title: dict.sections.changes.title,
        content: <p>{dict.sections.changes.p1}</p>,
    },
];

export default function PrivacyPage() {
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
