from rest_framework import permissions
from .models import Project

class IsProjectOwnerOrReadOnly(permissions.BasePermission):
    """
    Allows modifications only if user is owner of the related project.
    """

    def has_permission(self, request, view):
        # For creation of task, check payload project_id
        if request.method in permissions.SAFE_METHODS:
            return True
        if view.basename == 'project-tasks' or view.kwargs.get('project_id'):
            # handled in view-level check
            return True
        return True

    def has_object_permission(self, request, view, obj):
        # generic object-level; allow only owner to modify projects/tasks as needed
        if isinstance(obj, Project):
            return obj.owner == request.user
        return True
