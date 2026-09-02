from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=200)
    grade = models.CharField(max_length=50)
    short_description = models.TextField()
    long_description = models.TextField()
    instructor_name = models.CharField(max_length=150)
    duration = models.CharField(max_length=50)
    lessons_count = models.IntegerField(default=0)
    video_url = models.URLField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class LearningObjective(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='objectives')
    text = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.course.title} - {self.text}"

class Chapter(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=150)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} | {self.title}"

class Lesson(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    duration = models.CharField(max_length=50)
    icon = models.CharField(max_length=50, default='bx-play-circle')
    video_url = models.URLField(blank=True, null=True, default='https://www.youtube.com/embed/PA-f0MjuK_Q')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.chapter.title} | {self.title}"
