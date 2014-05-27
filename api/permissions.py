from rest_framework import permissions
import re

class BelongsToStudent(permissions.BasePermission):
    """
    Permission class for objects belonging to a specific student
    """

    def has_permission(self, request, view):
        """
        for requests with a specific object ID, defer to the object 
        permissions by returning "True"; otherwise restrict 
        methods is user is not admin
        """
        status = False
        if request.user.is_staff:
            # admin can do anything!
            status = True
        elif re.search(r'/api/\w+/\d+/', request.path):
            # For requests in the form /api/somestring/<ID>/ pass "True"
            # and defer SAFE permissions to the has_object_permissions handler
            if request.method in permissions.SAFE_METHODS:
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
        






