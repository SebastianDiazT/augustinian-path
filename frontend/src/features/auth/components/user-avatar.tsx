import { useState } from 'react';

import type { CurrentUser } from '@/api/auth';

interface UserAvatarProps {
    className?: string;
    user: CurrentUser;
}

function getInitials(user: CurrentUser): string {
    const firstName = user.first_name.trim();
    const lastName = user.last_name.trim();

    if (firstName || lastName) {
        return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
    }

    return user.email.slice(0, 2).toUpperCase();
}

export function UserAvatar({ className = 'size-10', user }: UserAvatarProps) {
    const [failedUrl, setFailedUrl] = useState<string | null>(null);

    const shouldShowImage = user.avatar_url !== null && failedUrl !== user.avatar_url;

    return (
        <span
            className={`inline-flex shrink-0 items-center justify-center overflow-hidden rounded-full bg-primary font-bold text-primary-foreground ${className}`}
            aria-hidden='true'
        >
            {shouldShowImage ? (
                <img
                    src={user.avatar_url ?? undefined}
                    alt=''
                    className='size-full object-cover'
                    decoding='async'
                    referrerPolicy='no-referrer'
                    onError={() => setFailedUrl(user.avatar_url)}
                />
            ) : (
                <span className='text-[0.72em]'>{getInitials(user)}</span>
            )}
        </span>
    );
}
