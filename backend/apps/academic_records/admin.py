from django.contrib import admin

from .models import CourseEnrollment, Grade


class GradeInline(admin.TabularInline):
    model = Grade
    extra = 0


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'offering', 'status')
    list_filter = ('status', 'offering__academic_term')
    inlines = [GradeInline]
