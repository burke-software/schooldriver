from rest_framework import permissions

class BelongsToStudent(permissions.BasePermission):
    """
    Permission class for objects belonging to a specific student
    """

    def has_permission(self, request, view):
        """
        for generic requests (e.g. /api/grades/ and NOT /api/grades/:id)
        admin users can see/do anything, other users can only do SAFE_METHODS
        """
        status = False

        if request.user.is_staff:
            # admin can do anything!
            status = True

        elif request.method in permissions.SAFE_METHODS:
            # other users can only access GET, OPTIONS, and HEAD methods
            status = True

        return status

    def has_object_permission(self, request, view, obj):
        """
        for specific objects, returns true if the object belongs to a student, 
        admins are also allowed to view these objects
        """
        status = False
        if request.user.is_staff:
            # staff user can do anything!
            status = True
        elif request.method in permissions.SAFE_METHODS:
            # student can only handle GET, OPTIONS, and HEAD methods
            if hasattr(obj, 'student'):
                if obj.student.id == request.user.id:
                    status = True

        return status
        






