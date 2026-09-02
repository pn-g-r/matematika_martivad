from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="სათაური")
    grade = models.CharField(max_length=50, verbose_name="კლასი")
    short_description = models.TextField(verbose_name="მოკლე აღწერა")
    long_description = models.TextField(verbose_name="სრული აღწერა")
    instructor_name = models.CharField(max_length=150, verbose_name="მასწავლებელი")
    duration = models.CharField(max_length=50, verbose_name="ხანგრძლივობა")
    lessons_count = models.IntegerField(default=0, verbose_name="გაკვეთილების რაოდენობა")
    video_url = models.URLField(verbose_name="შესავალი ვიდეოს ბმული")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ფასი")
    order = models.PositiveIntegerField(default=0, verbose_name="თანმიმდევრობა")

    class Meta:
        ordering = ['order']
        verbose_name = "კურსი"
        verbose_name_plural = "კურსები"

    def __str__(self):
        return self.title

class LearningObjective(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='objectives', verbose_name="კურსი")
    text = models.CharField(max_length=255, verbose_name="მიზანი / რას ისწავლით")

    class Meta:
        verbose_name = "სასწავლო მიზანი"
        verbose_name_plural = "სასწავლო მიზნები"

    def __str__(self):
        return f"{self.course.title} - {self.text}"

class Chapter(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chapters', verbose_name="კურსი")
    title = models.CharField(max_length=150, verbose_name="თავის სახელი (Chapter Title)")
    order = models.PositiveIntegerField(default=0, verbose_name="თანმიმდევრობა")

    class Meta:
        ordering = ['order']
        verbose_name = "თავი (Chapter)"
        verbose_name_plural = "თავები (Chapters)"

    def __str__(self):
        return f"{self.course.title} | {self.title}"

class Lesson(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='lessons', verbose_name="თავი")
    title = models.CharField(max_length=200, verbose_name="გაკვეთილის სახელი")
    duration = models.CharField(max_length=50, blank=True, default="", verbose_name="ხანგრძლივობა")
    icon = models.CharField(max_length=50, default='bx-play-circle', blank=True, verbose_name="აიკონი")
    video_url = models.URLField(blank=True, null=True, default='https://www.youtube.com/embed/PA-f0MjuK_Q', verbose_name="ვიდეოს ბმული (Video URL)")
    order = models.PositiveIntegerField(default=0, verbose_name="თანმიმდევრობა")

    class Meta:
        ordering = ['order']
        verbose_name = "გაკვეთილი (Lesson)"
        verbose_name_plural = "გაკვეთილები (Lessons)"

    def __str__(self):
        return f"{self.chapter.title} | {self.title}"
