from django.contrib import admin

from .models import Area, Faculty, ProfessionalSchool


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    search_fields = ('name', 'code')


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'area', 'code', 'is_active')
    list_filter = ('area',)
    search_fields = ('name', 'code')


@admin.register(ProfessionalSchool)
class ProfessionalSchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'faculty', 'code', 'is_active')
    list_filter = ('faculty__area', 'faculty')
    search_fields = ('name', 'code')
