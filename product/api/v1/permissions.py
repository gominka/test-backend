from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission, SAFE_METHODS
from users.models import Subscription


def make_payment(user, amount):
    """
    Списывает указанную сумму с баланса пользователя, если средств достаточно.
    """
    if user.balance.amount < amount:
        raise ValidationError("Insufficient funds.")
    user.balance.amount -= amount
    user.balance.save()


class IsStudentOrIsAdmin(BasePermission):
    def has_permission(self, request, view):
        # Разрешаем доступ, если пользователь аутентифицирован
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Разрешаем доступ администратору
        if request.user.is_staff:
            return True

        # Проверяем, имеет ли пользователь активную подписку на курс
        if isinstance(obj, Subscription):
            return obj.user == request.user and obj.active

        # Если объект - курс, проверяем подписку на этот курс
        if hasattr(obj, 'course'):
            return Subscription.objects.filter(
                user=request.user,
                course=obj.course,
                active=True
            ).exists()

        return False


class ReadOnlyOrIsAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff or request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.method in SAFE_METHODS
