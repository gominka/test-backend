from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from rest_framework import serializers

from courses.models import Course, Group, Lesson
from users.models import Subscription

User = get_user_model()


class LessonSerializer(serializers.ModelSerializer):
    """Список уроков."""

    course = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Lesson
        fields = (
            'title',
            'link',
            'course'
        )


class CreateLessonSerializer(serializers.ModelSerializer):
    """Создание уроков."""

    class Meta:
        model = Lesson
        fields = (
            'title',
            'link',
            'course'
        )


class StudentSerializer(serializers.ModelSerializer):
    """Студенты курса."""

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
        )


class GroupSerializer(serializers.ModelSerializer):
    """Список групп."""

    students = StudentSerializer(many=True, read_only=True)
    filled_percent = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ('id', 'title', 'course', 'students', 'filled_percent')

    def get_filled_percent(self, obj):
        """Процент заполненности группы."""
        max_students = 30
        return (obj.students.count() / max_students) * 100


class CreateGroupSerializer(serializers.ModelSerializer):
    """Создание групп."""

    class Meta:
        model = Group
        fields = (
            'title',
            'course',
        )


class MiniLessonSerializer(serializers.ModelSerializer):
    """Список названий уроков для списка курсов."""

    class Meta:
        model = Lesson
        fields = (
            'title',
        )

class CourseSerializer(serializers.ModelSerializer):
    """Список курсов."""

    lessons = MiniLessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField(read_only=True)
    students_count = serializers.SerializerMethodField(read_only=True)
    groups_filled_percent = serializers.SerializerMethodField(read_only=True)
    demand_course_percent = serializers.SerializerMethodField(read_only=True)

    def get_lessons_count(self, obj):
        """Количество уроков в курсе."""
        return obj.lessons.count()

    def get_students_count(self, obj):
        """Общее количество студентов на курсе."""
        group_ids = obj.groups.values_list('id', flat=True)
        return User.objects.filter(groups__id__in=group_ids).distinct().count()

    def get_groups_filled_percent(self, obj):
        """Средний процент заполненности групп, если в группе максимум 30 чел.."""
        total_groups = obj.groups.count()
        if total_groups == 0:
            return 0

        total_filled_percent = 0
        max_students_per_group = 30

        for group in obj.groups.all():
            filled_percent = (group.students.count() / max_students_per_group) * 100
            total_filled_percent += filled_percent

        average_filled_percent = total_filled_percent / total_groups
        return round(average_filled_percent)

    def get_demand_course_percent(self, obj):
        """Процент приобретения курса."""
        total_users = User.objects.count()
        subscribed_users = self.get_students_count(obj)
        return (subscribed_users / total_users) * 100 if total_users > 0 else 0

    class Meta:
        model = Course
        fields = (
            'id',
            'author',
            'title',
            'start_date',
            'price',
            'lessons_count',
            'lessons',
            'demand_course_percent',
            'students_count',
            'groups_filled_percent',
        )

class CreateCourseSerializer(serializers.ModelSerializer):
    """Создание курсов."""


    class Meta:
        model = Course
        fields = (
            'author',
            'title',
            'start_date',
            'price',
        )
