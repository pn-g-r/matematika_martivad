from django.contrib import admin
import nested_admin
from .models import Course, LearningObjective, Chapter, Lesson

class LessonNestedInline(nested_admin.NestedTabularInline):
    model = Lesson
    fields = ('title', 'video_url', 'duration', 'order')
    extra = 1
    sortable_field_name = "order"

class ChapterNestedInline(nested_admin.NestedStackedInline):
    model = Chapter
    fields = ('title', 'order')
    inlines = [LessonNestedInline]
    extra = 1
    sortable_field_name = "order"

class LearningObjectiveNestedInline(nested_admin.NestedTabularInline):
    model = LearningObjective
    fields = ('text',)
    extra = 1

@admin.register(Course)
class CourseAdmin(nested_admin.NestedModelAdmin):
    inlines = [LearningObjectiveNestedInline, ChapterNestedInline]
    list_display = ('title', 'grade', 'instructor_name', 'price', 'order')
    list_editable = ('order',)
    search_fields = ('title', 'grade', 'instructor_name')
    sortable_field_name = "order"


