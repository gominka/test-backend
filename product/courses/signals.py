from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from users.models import Subscription


@receiver(post_save, sender=Subscription)
def post_save_subscription(sender, instance: Subscription, created, **kwargs):
    """
    Распределение нового студента в группу курса.

    """

    if created:
        course = instance.course
        student = instance.user

        groups = course.groups.annotate(student_count=Count('students'))

        available_groups = groups.filter(student_count__lt=30)

        if available_groups.exists():
            group = available_groups.order_by('student_count').first()
        else:
            group_name = f'{course.title} - Group {groups.count() + 1}'
            group = course.groups.create(name=group_name)

        group.students.add(student)
        group.save()
