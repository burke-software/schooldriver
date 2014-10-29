from rest_framework import permissions

class ApplicantPermissions(permissions.BasePermission):
    """applicants need to be able to access OPTIONS and POST methods so they
    can load validation (OPTIONS) and also (POST) a new application"""

    def has_permission(self, request, view):
        if request.user and request.user.is_staff == True:
            return True
        elif request.method in ["OPTIONS", "POST"]:
            return True
        else:
            return False

class ApplicantTemplatePermissions(permissions.BasePermission):
    """only an admin can edit the template, everyone else can view it"""

    def has_permission(self, request, view):
        if request.user and request.user.is_staff == True:
            return True
        elif request.method in ["GET", "OPTIONS"]:
            return True
        else:
            return False