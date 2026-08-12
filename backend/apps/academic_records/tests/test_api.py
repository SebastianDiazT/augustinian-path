import uuid

import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_course_enrollment_isolation(
    api_client, student_profile_factory, course_enrollment_factory
):
    student1 = student_profile_factory()
    student2 = student_profile_factory()

    course_enrollment_factory(student=student2)

    api_client.force_authenticate(user=student1.user)

    url = reverse('academic_records:course-enrollment-list')
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    results = response.data.get('data', response.data)
    if isinstance(results, dict) and 'results' in results:
        results = results['results']

    assert len(results) == 0


def test_academic_progress_endpoints(api_client, student_profile_factory, curriculum_plan_factory):
    student = student_profile_factory()
    plan = curriculum_plan_factory()

    api_client.force_authenticate(user=student.user)

    url_progress = reverse('academic_records:progress')
    response_progress = api_client.get(f'{url_progress}?curriculum_plan={plan.public_id}')
    assert response_progress.status_code == status.HTTP_200_OK
    assert 'courses_passed' in response_progress.data

    url_eligible = reverse('academic_records:eligible-courses')
    response_eligible = api_client.get(f'{url_eligible}?curriculum_plan={plan.public_id}')
    assert response_eligible.status_code == status.HTTP_200_OK


def test_simulate_endpoint(
    api_client, student_profile_factory, course_enrollment_factory, evaluation_component_factory
):
    student = student_profile_factory()
    enrollment = course_enrollment_factory(student=student)

    component = evaluation_component_factory(
        syllabus__course=enrollment.offering.course,
        syllabus__academic_term=enrollment.offering.academic_term,
    )

    api_client.force_authenticate(user=student.user)

    url = reverse(
        'academic_records:course-enrollment-simulate', kwargs={'public_id': enrollment.public_id}
    )
    payload = {'expected_grades': {str(component.public_id): '15.00'}}

    response = api_client.post(url, payload, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert 'scenarios' in response.data


def test_admin_sees_all_enrollments(api_client, user_factory, course_enrollment_factory):
    admin = user_factory(is_platform_admin=True)
    course_enrollment_factory()
    course_enrollment_factory()

    api_client.force_authenticate(user=admin)
    response = api_client.get(reverse('academic_records:course-enrollment-list'))

    results = response.data.get('data', response.data.get('results', response.data))
    assert len(results) == 2


def test_api_progress_validations(
    api_client, user_factory, student_profile_factory, curriculum_plan_factory
):
    user = user_factory()
    api_client.force_authenticate(user=user)

    url = reverse('academic_records:progress')

    assert api_client.get(url).status_code == status.HTTP_400_BAD_REQUEST

    assert (
        api_client.get(f'{url}?curriculum_plan=invalido').status_code == status.HTTP_400_BAD_REQUEST
    )

    plan = curriculum_plan_factory()
    assert (
        api_client.get(f'{url}?curriculum_plan={plan.public_id}').status_code
        == status.HTTP_400_BAD_REQUEST
    )


def test_create_enrollment_validations(
    api_client,
    user_factory,
    student_profile_factory,
    course_factory,
    offering_factory,
    section_factory,
):
    user_no_profile = user_factory()
    api_client.force_authenticate(user=user_no_profile)

    course_no_lab = course_factory(lab_hours=0)
    offering_no_lab = offering_factory(course=course_no_lab)
    section_theo = section_factory(offering=offering_no_lab, section_type='theory')

    url = reverse('academic_records:course-enrollment-list')
    payload_no_lab = {
        'offering': offering_no_lab.public_id,
        'theory_section': section_theo.public_id,
    }

    assert (
        api_client.post(url, payload_no_lab, format='json').status_code
        == status.HTTP_400_BAD_REQUEST
    )

    student = student_profile_factory()
    api_client.force_authenticate(user=student.user)

    response = api_client.post(url, payload_no_lab, format='json')
    assert response.status_code == status.HTTP_201_CREATED

    payload_bad_lab = payload_no_lab.copy()
    payload_bad_lab['lab_section'] = section_theo.public_id
    assert (
        api_client.post(url, payload_bad_lab, format='json').status_code
        == status.HTTP_400_BAD_REQUEST
    )

    course_with_lab = course_factory(lab_hours=2)
    offering_lab = offering_factory(course=course_with_lab)
    section_theo_2 = section_factory(offering=offering_lab, section_type='theory')

    payload_missing_lab = {
        'offering': offering_lab.public_id,
        'theory_section': section_theo_2.public_id,
    }
    assert (
        api_client.post(url, payload_missing_lab, format='json').status_code
        == status.HTTP_400_BAD_REQUEST
    )


def test_enrollment_queryset_no_profile_and_simulate_no_syllabus(
    api_client, user_factory, student_profile_factory, course_enrollment_factory
):
    user = user_factory()
    api_client.force_authenticate(user=user)
    assert (
        api_client.get(reverse('academic_records:course-enrollment-list')).status_code
        == status.HTTP_200_OK
    )

    student = student_profile_factory()
    enrollment = course_enrollment_factory(student=student)
    api_client.force_authenticate(user=student.user)
    url_sim = reverse(
        'academic_records:course-enrollment-simulate', kwargs={'public_id': enrollment.public_id}
    )
    assert api_client.post(url_sim, {}).status_code == status.HTTP_400_BAD_REQUEST


def test_eligible_courses_invalid_plan(api_client, student_profile_factory):
    student = student_profile_factory()
    api_client.force_authenticate(user=student.user)
    url = reverse('academic_records:eligible-courses')
    assert (
        api_client.get(f'{url}?curriculum_plan={uuid.uuid4()}').status_code
        == status.HTTP_400_BAD_REQUEST
    )


def test_enrollment_grades_action(
    api_client, student_profile_factory, course_enrollment_factory, evaluation_component_factory
):
    student = student_profile_factory()
    enrollment = course_enrollment_factory(student=student)

    comp_valid = evaluation_component_factory(
        syllabus__course=enrollment.offering.course,
        syllabus__academic_term=enrollment.offering.academic_term,
    )
    comp_invalid = evaluation_component_factory()

    api_client.force_authenticate(user=student.user)
    url = reverse(
        'academic_records:course-enrollment-grades', kwargs={'public_id': enrollment.public_id}
    )

    assert api_client.get(url).status_code == status.HTTP_200_OK

    res_inv = api_client.post(
        url, {'evaluation_component': comp_invalid.public_id, 'score': '15.00'}, format='json'
    )
    assert res_inv.status_code == status.HTTP_400_BAD_REQUEST

    res_val = api_client.post(
        url, {'evaluation_component': comp_valid.public_id, 'score': '15.00'}, format='json'
    )
    assert res_val.status_code == status.HTTP_201_CREATED


def test_invalid_plan_uuid(api_client, student_profile_factory):
    student = student_profile_factory()
    api_client.force_authenticate(user=student.user)

    url = reverse('academic_records:progress')
    fake_uuid = uuid.uuid4()

    response = api_client.get(f'{url}?curriculum_plan={fake_uuid}')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_enrollment_mismatched_sections(
    api_client, student_profile_factory, course_factory, offering_factory, section_factory
):
    student = student_profile_factory()
    api_client.force_authenticate(user=student.user)

    course_1 = course_factory(lab_hours=2)
    offering_1 = offering_factory(course=course_1)

    course_2 = course_factory(lab_hours=2)
    offering_2 = offering_factory(course=course_2)
    section_theo_wrong = section_factory(offering=offering_2, section_type='theory')
    section_lab_wrong = section_factory(offering=offering_2, section_type='lab')

    url = reverse('academic_records:course-enrollment-list')

    res_theo = api_client.post(
        url,
        {
            'offering': offering_1.public_id,
            'theory_section': section_theo_wrong.public_id,
            'lab_section': section_lab_wrong.public_id,
        },
        format='json',
    )
    assert res_theo.status_code == status.HTTP_400_BAD_REQUEST

    section_theo_right = section_factory(offering=offering_1, section_type='theory')
    res_lab = api_client.post(
        url,
        {
            'offering': offering_1.public_id,
            'theory_section': section_theo_right.public_id,
            'lab_section': section_lab_wrong.public_id,
        },
        format='json',
    )
    assert res_lab.status_code == status.HTTP_400_BAD_REQUEST

def test_no_profile_users_in_progress_views(api_client, user_factory, curriculum_plan_factory):
    user = user_factory(is_platform_admin=False)
    api_client.force_authenticate(user=user)

    plan = curriculum_plan_factory()
    url_prog = reverse('academic_records:progress')
    url_elig = reverse('academic_records:eligible-courses')

    assert (
        api_client.get(f'{url_prog}?curriculum_plan={plan.public_id}').status_code
        == status.HTTP_400_BAD_REQUEST
    )
    assert (
        api_client.get(f'{url_elig}?curriculum_plan={plan.public_id}').status_code
        == status.HTTP_400_BAD_REQUEST
    )


def test_platform_admin_full_access(api_client, user_factory, course_enrollment_factory):
    admin = user_factory(is_platform_admin=True)
    enrollment = course_enrollment_factory()

    api_client.force_authenticate(user=admin)

    res_list = api_client.get(reverse('academic_records:course-enrollment-list'))
    assert res_list.status_code == status.HTTP_200_OK

    url_detail = reverse(
        'academic_records:course-enrollment-detail', kwargs={'public_id': enrollment.public_id}
    )
    res_detail = api_client.get(url_detail)
    assert res_detail.status_code == status.HTTP_200_OK