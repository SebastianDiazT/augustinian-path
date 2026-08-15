import type { ComponentPropsWithoutRef } from 'react';
import { ES_UI } from '@/locales/es';
import logoMarkUrl from '@/assets/logo-mark.svg';

type BrandMarkProps = Omit<ComponentPropsWithoutRef<'img'>, 'src'>;

export function BrandMark({ alt = ES_UI.brand.name, ...props }: BrandMarkProps) {
    return <img src={logoMarkUrl} alt={alt} {...props} />;
}
