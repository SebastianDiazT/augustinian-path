import pytest

from apps.schedules.models import ScheduleAlternativeSection

pytestmark = pytest.mark.django_db


def test_simulation_str(schedule_simulation_factory):
    sim = schedule_simulation_factory()
    assert str(sim.student) in str(sim)


def test_alternative_str(schedule_alternative_factory):
    alt = schedule_alternative_factory(score='95.50', rank=1)
    assert '95.50' in str(alt)
    assert '#1' in str(alt)


def test_alternative_section_str(schedule_alternative_factory, section_factory):
    alt = schedule_alternative_factory()
    section = section_factory()
    bridge = ScheduleAlternativeSection.objects.create(alternative=alt, section=section)
    assert str(alt) in str(bridge)


def test_public_share_link_str(public_share_link_factory):
    link = public_share_link_factory()
    assert 'Share link for' in str(link)
