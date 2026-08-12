from django.contrib import admin

from .models import (
    AcademicTerm,
    Course,
    CurriculumPlan,
    ElectiveBranch,
    EvaluationComponent,
    Instructor,
    Prerequisite,
    Syllabus,
)


@admin.register(CurriculumPlan)
class CurriculumPlanAdmin(admin.ModelAdmin):
    list_display = ('school', 'year', 'name', 'min_elective_branches_to_complete', 'is_active')
    list_filter = ('school',)


@admin.register(ElectiveBranch)
class ElectiveBranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'curriculum_plan', 'is_active')
    list_filter = ('curriculum_plan',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'curriculum_plan', 'cycle', 'credits', 'has_lab', 'branch')
    list_filter = ('curriculum_plan', 'cycle', 'course_type', 'branch')
    search_fields = ('code', 'name')


@admin.register(Prerequisite)
class PrerequisiteAdmin(admin.ModelAdmin):
    list_display = ('course', 'required_course')


@admin.register(AcademicTerm)
class AcademicTermAdmin(admin.ModelAdmin):
    list_display = ('code', 'start_date', 'end_date', 'is_active')


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'is_active')
    search_fields = ('full_name',)


class EvaluationComponentInline(admin.TabularInline):
    model = EvaluationComponent
    extra = 0


@admin.register(Syllabus)
class SyllabusAdmin(admin.ModelAdmin):
    list_display = ('course', 'academic_term', 'is_active')
    list_filter = ('academic_term',)
    inlines = [EvaluationComponentInline]
