from rest_framework.permissions import BasePermission


class IsMedecin(BasePermission):
    """
    Allows only authenticated users with medecin role to access.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'medecin'


class IsNoteOwner(BasePermission):
    """
    Allows only the doctor (owner) of the note to edit or delete it.
    Other doctors can view the note but cannot modify it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions allowed to any authenticated user
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user.is_authenticated

        # Write permissions only allowed to the note owner (doctor)
        return obj.doctor == request.user


class IsNoteOwnerOrReadOnly(BasePermission):
    """
    Allows any authenticated user to read notes.
    Only the note owner (doctor) can edit or delete.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Read permissions allowed to any authenticated user
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        # Write permissions only allowed to the note owner
        return obj.doctor == request.user


class CanCreateNote(BasePermission):
    """
    Only doctors (medecin) can create notes.
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated and request.user.role == 'medecin'
        return request.user.is_authenticated
