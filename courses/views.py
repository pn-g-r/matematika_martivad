from django.shortcuts import render, get_object_or_404
from .models import Course

def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/index.html', {'courses': courses})

def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    return render(request, 'courses/course.html', {'course': course})
