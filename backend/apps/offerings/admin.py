from django.contrib import admin

from .models import Meeting, Offering, Section, TimeBlock


@admin.register(Offering)
class OfferingAdmin(admin.ModelAdmin):
    list_display = ('course', 'academic_term', 'is_active')
    list_filter = ('academic_term',)


class MeetingInline(admin.TabularInline):
    model = Meeting
    extra = 0


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('offering', 'section_type', 'number', 'instructor')
    list_filter = ('section_type', 'offering__academic_term')
    inlines = [MeetingInline]


@admin.register(TimeBlock)
class TimeBlockAdmin(admin.ModelAdmin):
    list_display = ('order', 'start_time', 'end_time')
    ordering = ['order']
