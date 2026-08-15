import {
    PublicDocumentLayout,
    type PublicDocumentSection,
} from '@/components/layout/public-document-layout';
import { projectConfig } from '@/config/project';
import { ES_UI } from '@/locales/es';
import { SEO } from '@/components/seo';

const dict = ES_UI.termsPage;

const sections: PublicDocumentSection[] = [
    {
        id: 'acceptance',
        title: dict.sections.acceptance.title,
        content: <p>{dict.sections.acceptance.p1}</p>,
    },
    {
        id: 'independence',
        title: dict.sections.independence.title,
        content: (
            <>
                <p>{dict.sections.independence.p1}</p>
                <p>{dict.sections.independence.p2}</p>
            </>
        ),
    },
    {
        id: 'access',
        title: dict.sections.access.title,
        content: (
            <ul className='list-disc space-y-2 pl-5'>
                {dict.sections.access.list.map((item, idx) => (
                    <li key={idx}>{item}</li>
                ))}
            </ul>
        ),
    },
    {
        id: 'academic-information',
        title: dict.sections.academicInformation.title,
        content: (
            <>
                <p>{dict.sections.academicInformation.p1}</p>
                <p>{dict.sections.academicInformation.p2}</p>
            </>
        ),
    },
    {
        id: 'acceptable-use',
        title: dict.sections.acceptableUse.title,
        content: (
            <>
                <p>{dict.sections.acceptableUse.p1}</p>
                <p>{dict.sections.acceptableUse.p2}</p>
                <ul className='list-disc space-y-2 pl-5'>
                    {dict.sections.acceptableUse.list.map((item, idx) => (
                        <li key={idx}>{item}</li>
                    ))}
                </ul>
            </>
        ),
    },
    {
        id: 'availability',
        title: dict.sections.availability.title,
        content: <p>{dict.sections.availability.p1}</p>,
    },
    {
        id: 'responsibility',
        title: dict.sections.responsibility.title,
        content: <p>{dict.sections.responsibility.p1}</p>,
    },
    {
        id: 'termination',
        title: dict.sections.termination.title,
        content: (
            <p>
                {dict.sections.termination.p1}{' '}
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
        title: dict.sections.changes.title,
        content: <p>{dict.sections.changes.p1}</p>,
    },
];

export default function TermsPage() {
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
