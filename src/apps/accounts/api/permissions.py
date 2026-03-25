from rest_framework.permissions import BasePermission


class IsBusinessOwner(BasePermission):
    message = "Esta área está disponible solo para cuentas comerciales."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_business_owner
        )


class IsPetOwner(BasePermission):
    message = "Esta área está disponible solo para cuentas de tutor."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_pet_owner
        )
