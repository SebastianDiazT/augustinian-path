from django.contrib import admin

from .models import (
    PublicShareLink,
    ScheduleAlternative,
    ScheduleAlternativeSection,
    ScheduleSimulation,
)


class ScheduleAlternativeSectionInline(admin.TabularInline):
    model = ScheduleAlternativeSection
    extra = 0


class ScheduleAlternativeInline(admin.TabularInline):
    model = ScheduleAlternative
    extra = 0
    show_change_link = True


@admin.register(ScheduleSimulation)
class ScheduleSimulationAdmin(admin.ModelAdmin):
    list_display = ('student', 'academic_term', 'created_at')
    list_filter = ('academic_term',)
    inlines = [ScheduleAlternativeInline]


@admin.register(ScheduleAlternative)
class ScheduleAlternativeAdmin(admin.ModelAdmin):
    list_display = ('simulation', 'rank', 'score', 'is_favorite')
    inlines = [ScheduleAlternativeSectionInline]


@admin.register(PublicShareLink)
class PublicShareLinkAdmin(admin.ModelAdmin):
    list_display = ('alternative', 'include_personal_info', 'is_active', 'created_at')
