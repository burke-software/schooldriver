from rest_framework import filters

class BelongsToStudentFilter(filters.BaseFilterBackend):
    """
    A filter class for views that need to only show objects owned by 
    individual students. Admin users can see the entire queryset
    """

    def filter_queryset(self, request, queryset, view):
        """
        return the entire queryset if admin user
        else, return the objects that belong to the user
        """
        if request.user.is_staff:
            return queryset
        else:
            return queryset.filter(student=request.user)