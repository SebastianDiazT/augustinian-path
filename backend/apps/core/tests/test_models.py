import uuid

from django.apps import apps

from apps.core.models import CatalogBaseModel


def test_catalog_base_model_is_abstract():
    assert CatalogBaseModel._meta.abstract is True


def test_catalog_base_model_has_expected_fields():
    field_names = {f.name for f in CatalogBaseModel._meta.get_fields()}
    assert {'public_id', 'is_active', 'created_at', 'updated_at'} <= field_names

    public_id_field = CatalogBaseModel._meta.get_field('public_id')
    assert public_id_field.unique is True
    assert public_id_field.editable is False
    assert public_id_field.default is uuid.uuid4


def test_core_app_registers_no_concrete_models():
    # `core` no debe crear ninguna tabla propia en la base de datos.
    assert list(apps.get_app_config('core').get_models()) == []
