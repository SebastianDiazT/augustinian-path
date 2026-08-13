from urllib.parse import quote

import requests
from django.conf import settings
from rest_framework.exceptions import ValidationError


def get_syllabus_upload_url(syllabus) -> dict:
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise ValidationError('El almacenamiento no está configurado en el servidor.')

    course_code = syllabus.course.code
    course_name = syllabus.course.name.upper()
    term_code = syllabus.academic_term.code

    course_name = course_name.replace('/', '-').replace('\\', '-')

    filename = f'SILABO-{course_code}-{course_name} ({term_code}).pdf'

    path = quote(filename)

    sign_url = (
        f'{settings.SUPABASE_URL}/storage/v1/object/upload/sign/'
        f'{settings.SUPABASE_STORAGE_BUCKET}/{path}'
    )

    try:
        response = requests.post(
            sign_url,
            headers={'Authorization': f'Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}'},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        upload_url = f'{settings.SUPABASE_URL}{data["url"]}'
        public_url = (
            f'{settings.SUPABASE_URL}/storage/v1/object/public/'
            f'{settings.SUPABASE_STORAGE_BUCKET}/{path}'
        )

        return {'upload_url': upload_url, 'public_url': public_url}

    except requests.RequestException as exc:
        raise ValidationError('No se pudo generar el enlace seguro de subida.') from exc
