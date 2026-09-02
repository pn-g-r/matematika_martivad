from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from .models import Course, LearningObjective, Chapter, Lesson

class LessonInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Lesson
    extra = 1

class ChapterInline(SortableInlineAdminMixin, admin.StackedInline):
    model = Chapter
    extra = 1
    show_change_link = True

class LearningObjectiveInline(admin.TabularInline):
    model = LearningObjective
    extra = 1

@admin.register(Course)
class CourseAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = [LearningObjectiveInline, ChapterInline]
    list_display = ('title', 'grade', 'price', 'order')

@admin.register(Chapter)
class ChapterAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ('title', 'course', 'order')

admin.site.register(LearningObjective)
@admin.register(Lesson)
class LessonAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'chapter', 'order')

