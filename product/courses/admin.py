from django.contrib import admin

from courses.models import Course, Lesson, Group

admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Group)

