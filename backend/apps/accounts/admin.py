from django.contrib import admin

from .models import (
    MembershipRequest,
    SchoolDelegation,
    SchoolMembership,
    StudentProfile,
    User,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'full_name',
        'is_platform_admin',
        'is_staff',
        'is_active',
    )
    search_fields = ('email', 'full_name')
    list_filter = ('is_platform_admin', 'is_staff', 'is_active')
    readonly_fields = ('public_id', 'google_sub', 'last_login', 'created_at', 'updated_at')
    exclude = ('password', 'groups', 'user_permissions')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('cui', 'user', 'is_active')
    search_fields = ('cui', 'user__email')


@admin.register(SchoolMembership)
class SchoolMembershipAdmin(admin.ModelAdmin):
    list_display = ('student', 'school', 'curriculum_plan', 'verified_by', 'verified_at')
    list_filter = ('school',)


@admin.register(MembershipRequest)
class MembershipRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'school', 'request_type', 'status', 'created_at')
    list_filter = ('status', 'request_type')
    readonly_fields = ('resolved_by', 'resolved_at')


@admin.register(SchoolDelegation)
class SchoolDelegationAdmin(admin.ModelAdmin):
    list_display = ('delegate', 'school', 'assigned_by', 'is_active')
