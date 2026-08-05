import type { ComponentPropsWithoutRef } from 'react';

import logoMarkUrl from '@/assets/brand/logo-mark.svg';

type BrandMarkProps = Omit<ComponentPropsWithoutRef<'img'>, 'src'>;

export function BrandMark({ alt = 'Ruta Agustina', ...props }: BrandMarkProps) {
    return <img src={logoMarkUrl} alt={alt} {...props} />;
}
