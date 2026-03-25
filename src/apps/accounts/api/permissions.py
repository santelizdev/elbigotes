from rest_framework.permissions import BasePermission


class IsBusinessOwner(BasePermission):
    message = "Esta área está disponible solo para cuentas comerciales."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_business_owner)
